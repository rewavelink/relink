"""
MIT License

Copyright (c) 2019-2026 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

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

from ._base import BasePlayer

FrameworkLiteral = Literal["discord.py", "pycord", "disnake"]

_log = logging.getLogger(__name__)


class PlayerFactory:
    _FRAMEWORK_DATA: dict[str, dict[str, str]] = {
        "discord.py": {"pkg": "discord.py", "import_name": "discord"},
        "disnake": {"pkg": "disnake", "import_name": "disnake"},
        "pycord": {"pkg": "py-cord", "import_name": "discord"},
    }

    def get_player(
        self,
        framework: FrameworkLiteral,
    ) -> type[BasePlayer]:
        """
        Returns the appropriate VoiceProtocol based on the framework string.
        """
        if not self.has_framework(framework):
            raise RuntimeError(
                f"Framework '{framework}' is not exclusively installed in the current environment."
            )

        match framework:
            case "discord.py":
                from .adapters._dpy import DpyPlayer

                return DpyPlayer
            case "disnake":
                # ! Should be replaced when corresponding implementation is ready
                return BasePlayer  # type: ignore
            case "pycord":
                # ! Should be replaced when corresponding implementation is ready
                return BasePlayer  # type: ignore

    def detect_framework(self) -> FrameworkLiteral | None:
        if env := os.environ.get("RELINK_FRAMEWORK"):
            return cast(FrameworkLiteral, env)

        available: list[FrameworkLiteral] = [
            framework
            for framework in get_args(FrameworkLiteral)
            if self.has_framework(framework)
        ]

        if not available:
            _log.warning(
                "No supported framework exclusively detected (discord.py, py-cord, disnake)."
            )
            return None

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

        pkg, import_name = data["pkg"], data["import_name"]
        target_norm = self._normalize(pkg)

        try:
            importlib.metadata.version(pkg)

            known = {self._normalize(d["pkg"]) for d in self._FRAMEWORK_DATA.values()}

            mapping = importlib.metadata.packages_distributions()
            providers = {self._normalize(p) for p in mapping.get(import_name, [])}

            return (providers & known) == {target_norm}

        except importlib.metadata.PackageNotFoundError:
            return False

    def _normalize(self, name: str) -> str:
        return name.strip().casefold().replace("_", "-").replace(".", "-")
