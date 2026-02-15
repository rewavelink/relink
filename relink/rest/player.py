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
from typing import Any

import msgspec

from .track import TrackType
from .filters import PlayerFilterType


class PlayerType(msgspec.Struct, kw_only=True):
    """Represents a Player structure payload."""

    guild_id: int = msgspec.field(name="guildId")
    track: TrackType | None = None
    volumne: int
    paused: bool
    state: PlayerStateType
    voice: PlayerVoiceStateType
    filters: PlayerFilterType


class PlayerStateType(msgspec.Struct, kw_only=True):
    """Represents a PlayerState structure payload."""

    time: int
    position: int
    connected: bool
    ping: int  # -1 if not connected


class PlayerVoiceStateType(msgspec.Struct, kw_only=True):
    """Represents a PlayerVoiceState structure payload."""

    token: str
    endpoint: str
    session_id: str = msgspec.field(name="sessionId")
