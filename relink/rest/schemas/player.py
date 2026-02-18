"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

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

from typing import Annotated, Any

import msgspec

from .filters import PlayerFilters
from .track import Track


class Player(msgspec.Struct, kw_only=True):
    """Represents a Player structure payload."""

    guild_id: int = msgspec.field(name="guildId")
    track: Track | None = None
    volume: Annotated[int, "0..1000 (percentage)"]
    paused: bool
    state: PlayerState
    voice: PlayerVoiceState
    filters: PlayerFilters


class PlayerState(msgspec.Struct, kw_only=True):
    """Represents a PlayerState structure payload."""

    time: int
    position: int
    connected: bool
    ping: Annotated[int, "-1 if not connected"]


class PlayerVoiceState(msgspec.Struct, kw_only=True):
    """Represents a PlayerVoiceState structure payload."""

    token: str
    endpoint: str
    session_id: str = msgspec.field(name="sessionId")


# PATCH /v4/sessions/{sessionId}/players/{guildId}?noReplace=true


class UpdatePlayerRequest(msgspec.Struct, kw_only=True):
    """Represents an UpdatePlayerRequest structure payload."""

    track: UpdatePlayerTrackRequest | None = None
    position: int | None = None
    endtime: int | None = msgspec.field(name="endTime", default=None)
    volume: Annotated[int | None, "0..1000 (percentage)"] = None
    paused: bool | None = None
    filters: PlayerFilters | None = None
    voice: PlayerVoiceState | None = None


class UpdatePlayerTrackRequest(msgspec.Struct, kw_only=True):
    """Represents an UpdatePlayerTrackRequest structure payload."""

    encoded: str | None = None
    identifier: str | None = None
    user_data: dict[str, Any] | None = msgspec.field(name="userData", default=None)


GetPlayersResponse = list[Player]
GetPlayerResponse = Player
UpdatePlayerResponse = Player
DestroyPlayerResponse = None
