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

from typing import Any

import msgspec

from .filters import PlayerFilters
from .track import Track


class Player(msgspec.Struct, kw_only=True):
    """
    Represents a Lavalink Player.

    This object is returned by the REST API under `/players` endpoints.

    :attr guild_id: The Discord guild ID the player belongs to.
    :attr track: Currently playing track (:class:`Track`) or ``None`` if no track is loaded.
    :attr volume: Player volume (0-1000 percent scale).
    :attr paused: Whether the player is currently paused.
    :attr state: Current state of the player (:class:`PlayerState`).
    :attr voice: Voice connection state (:class:`PlayerVoiceState`).
    :attr filters: Active audio filters (:class:`PlayerFilters`).
    """

    guild_id: int = msgspec.field(name="guildId")
    track: Track | None = None
    volume: int
    paused: bool
    state: PlayerState
    voice: PlayerVoiceState
    filters: PlayerFilters


class PlayerState(msgspec.Struct, kw_only=True):
    """
    Represents the state of a Lavalink Player.

    :attr time: Timestamp of the state in milliseconds.
    :attr position: Current track position in milliseconds.
    :attr connected: Whether the player is connected to a voice channel.
    :attr ping: Connection ping in milliseconds, ``-1`` if not connected.
    """

    time: int
    position: int
    connected: bool
    ping: int


class PlayerVoiceState(msgspec.Struct, kw_only=True):
    """
    Represents the voice connection state of a Lavalink Player.

    :attr token: Voice connection token.
    :attr endpoint: Voice server endpoint.
    :attr session_id: Session ID of the voice connection.
    """

    token: str
    endpoint: str
    session_id: str = msgspec.field(name="sessionId")


class UpdatePlayerRequest(msgspec.Struct, kw_only=True):
    """
    Payload to update a Lavalink Player.

    This object is sent to `/players/{guildId}` to modify player state.

    :attr track: Track to play or update (:class:`UpdatePlayerTrackRequest`), optional.
    :attr position: Seek position in milliseconds, optional.
    :attr endtime: Track end time in milliseconds, optional.
    :attr volume: Volume to set (0-1000 percent scale), optional.
    :attr paused: Whether to pause the player, optional.
    :attr filters: Audio filters to apply (:class:`PlayerFilters`), optional.
    :attr voice: Voice state updates (:class:`PlayerVoiceState`), optional.
    """

    track: UpdatePlayerTrackRequest | None = None
    position: int | None = None
    endtime: int | None = msgspec.field(name="endTime", default=None)
    volume: int | None = None
    paused: bool | None = None
    filters: PlayerFilters | None = None
    voice: PlayerVoiceState | None = None


class UpdatePlayerTrackRequest(msgspec.Struct, kw_only=True):
    """
    Represents a track update request for a Lavalink Player.

    Used within :class:`UpdatePlayerRequest` to play or modify a track.

    :attr encoded: Base64-encoded track string, optional.
    :attr identifier: Unique track identifier, optional.
    :attr user_data: Optional user data previously provided when updating the player.
    """

    encoded: str | None = None
    identifier: str | None = None
    user_data: dict[str, Any] | None = msgspec.field(name="userData", default=None)


GetPlayersResponse = list[Player]
"""Response type for GET /players. Returns a list of :class:`Player` objects."""

GetPlayerResponse = Player
"""Response type for GET /players/{guildId}. Returns a single :class:`Player` object."""

UpdatePlayerResponse = Player
"""Response type for PATCH /players/{guildId}. Returns the updated :class:`Player` object."""

DestroyPlayerResponse = None
"""Response type for DELETE /players/{guildId}. Returns nothing on success."""
