"""
MIT License

Copyright (c) 2026-present ReWaveLink Development Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from __future__ import annotations

import importlib.metadata
import logging
import os
from typing import Literal, cast, get_args

from packaging.version import Version

from ._base import BasePlayer

FrameworkLiteral = Literal["discord.py", "pycord", "disnake"]

_log = logging.getLogger(__name__)


class PlayerFactory:
    _FRAMEWORK_DATA: dict[str, dict[str, str]] = {
        "discord.py": {"pkg": "discord.py", "import_name": "discord", "min": "2.7"},
        "disnake": {"pkg": "disnake", "import_name": "disnake", "min": "2.12"},
        "pycord": {"pkg": "py-cord", "import_name": "discord", "min": "2.8"},
    }

    def get_player(
        self,
        framework: FrameworkLiteral,
    ) -> type[BasePlayer]:
        """
        Returns the appropriate VoiceProtocol based on the framework string.
        """
        if not self.has_framework(framework):
            pkg_info = self._FRAMEWORK_DATA[framework]
            raise RuntimeError(
                f"Framework '{framework}' is not installed or does not meet "
                f"the minimum version requirement (v{pkg_info['min']}+)."
            )

        match framework:
            case "discord.py":
                from .adapters._dpy import DpyPlayer

                return DpyPlayer
            case "disnake":
                from .adapters._disnake import DisnakePlayer

                return DisnakePlayer
            case "pycord":
                from .adapters._pycord import PycordPlayer

                return PycordPlayer

    def detect_framework(self) -> FrameworkLiteral | None:
        if env := os.environ.get("RELINK_FRAMEWORK"):
            return cast(FrameworkLiteral, env)

        available: list[FrameworkLiteral] = [
            framework
            for framework in get_args(FrameworkLiteral)
            if self.has_framework(framework)
        ]

        if not available:
            raise RuntimeError(
                "No supported framework detected meeting the minimum version requirements.\n"
                "Ensure one of the following is installed: "
                "discord.py >= 2.7, py-cord >= 2.8, or disnake >= 2.12."
            )

        if len(available) > 1:
            _log.warning(
                "Multiple frameworks detected: %s, using '%s'.\n"
                "Override this by passing 'framework' to relink.Client.",
                available,
                available[0],
            )

        return available[0]

    def has_framework(self, framework: FrameworkLiteral) -> bool:
        data = self._FRAMEWORK_DATA.get(framework)
        if not data:
            return False

        pkg, import_name, min_ver = data["pkg"], data["import_name"], data["min"]
        target_norm = self._normalize(pkg)

        try:
            installed_version = importlib.metadata.version(pkg)

            if Version(installed_version).release < Version(min_ver).release:
                _log.warning(
                    f"Found {pkg} v{installed_version}, but v{min_ver}+ is required."
                )
                return False

            known = {self._normalize(d["pkg"]) for d in self._FRAMEWORK_DATA.values()}
            mapping = importlib.metadata.packages_distributions()
            providers = {self._normalize(p) for p in mapping.get(import_name, [])}

            return (providers & known) == {target_norm}

        except importlib.metadata.PackageNotFoundError:
            return False

    def _normalize(self, name: str) -> str:
        return name.strip().casefold().replace("_", "-").replace(".", "-")
