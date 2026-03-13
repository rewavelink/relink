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

from typing import Iterable

import discord

from relink.gateway.enums import InactivityMode

from .base import BaseSettings


class InactivitySettings(BaseSettings):
    """
    Configuration for player inactivity and auto-disconnection.

    Attributes
    ----------
    timeout: :class:`int` | :data:`None`
        The time in seconds to wait before disconnecting. Defaults to 300.
    mode: :class:`InactivityMode`
        The strategy used to determine if the channel is "inactive".
    user_ids: Iterable[:class:`discord.abc.Snowflake` | :class:`int`]
        An iterable of user IDs or Discord objects that act as "Keep Alive" members.
    """

    __slots__ = (
        "timeout",
        "mode",
        "user_ids",
    )

    def __init__(
        self,
        *,
        timeout: int | None = 300,
        mode: InactivityMode = InactivityMode.ALL_BOTS,
        user_ids: Iterable[discord.abc.Snowflake | int] | None = None,
    ) -> None:
        self.timeout = timeout
        self.mode = mode
        self.user_ids = user_ids or []


class HistorySettings(BaseSettings):
    """
    Configuration for player history tracking.

    Attributes
    ----------
    enabled: :class:`bool`
        Whether history tracking is enabled. Defaults to true.
    max_items: :class:`int` | :data:`None`
        The maximum number of items to keep in history. Defaults to 100.
    """

    __slots__ = (
        "enabled",
        "max_items",
    )

    def __init__(
        self,
        *,
        enabled: bool = True,
        max_items: int | None = 100,
    ) -> None:
        self.enabled = enabled
        self.max_items = max_items
