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

import importlib.util
from typing import Literal

from ._base import BasePlayer


class PlayerFactory:
    async def get_player(
        self,
        framework: Literal["discord.py", "disnake", "pycord"],
    ) -> BasePlayer:
        """
        Returns the appropriate VoiceProtocol based on the framework string.
        """
        if not self.has_framework(framework):
            raise RuntimeError(
                f"Framework '{framework}' is not installed in the current environment."
            )

        match framework:
            case "discord.py":
                from .adapters._dpy import DpyPlayer

                return DpyPlayer()
            case "disnake":
                # ! Should be replaced when corresponding implementation is ready
                return BasePlayer()  # type: ignore
            case "pycord":
                # ! Should be replaced when corresponding implementation is ready
                return BasePlayer()  # type: ignore

    @staticmethod
    def has_framework(framework: str) -> bool:
        """
        Checks if the library for the specific framework is installed.
        """
        return importlib.util.find_spec("discord") is not None
