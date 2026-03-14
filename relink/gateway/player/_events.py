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

import time
from typing import Any

import msgspec
from discord.types.voice import GuildVoiceState, VoiceServerUpdate

from relink.rest.schemas.player import (
    PlayerVoiceState,
    UpdatePlayerRequest,
)

from ..enums import TrackEndReason
from ..schemas.events import (
    TrackEndEvent,
    TrackExceptionEvent,
    TrackStartEvent,
    TrackStuckEvent,
    WebSocketClosedEvent,
)
from ..schemas.receive import PlayerState
from ._base import HandlerBase, _log

__all__ = ()


class EventsHandler(HandlerBase):
    """Internal handler responsible for processing Gateway and Lavalink events."""

    __slots__ = ()

    async def on_voice_server_update(self, data: VoiceServerUpdate) -> None:
        self._player._connection.token = data.get("token")
        self._player._connection.endpoint = data.get("endpoint")

        # The endpoint might be None; Lavalink needs a string or it will fail.
        # Thus we wait for a non-None endpoint before dispatching.
        if self._player._connection.endpoint:
            await self._dispatch_voice_update()

    async def _dispatch_event(self, data: dict[str, Any]) -> None:
        event_type = data.get("type")
        _log.debug(
            "Player %s receiving even type: %s", self._player.guild_id, event_type
        )

        assert self._player._node is not None
        assert self._player._node._client is not None

        match event_type:
            case "TrackStartEvent":
                payload = msgspec.convert(data, TrackStartEvent)

                self._player._paused = False
                self._player._stop_inactivity_timer()

                self._player._node._client._dispatch(
                    "track_start", self._player, payload
                )

            case "TrackEndEvent":
                payload = msgspec.convert(data, TrackEndEvent)

                if payload.reason != TrackEndReason.REPLACED:
                    self._player._last_position = 0
                    self._player._last_update = 0.0

                if payload.reason.can_start_next:
                    await self._player.skip()

                self._player._node._client._dispatch("track_end", self._player, payload)
                self._player._check_inactivity()

            case "TrackExceptionEvent":
                payload = msgspec.convert(data, TrackExceptionEvent)
                _log.error(
                    "Track exception in guild %s: %s",
                    self._player.guild_id,
                    payload.exception.message,
                )

                self._player._node._client._dispatch(
                    "track_exception", self._player, payload
                )

            case "TrackStuckEvent":
                payload = msgspec.convert(data, TrackStuckEvent)
                _log.warning(
                    "Track stuck in guild %s at %dms",
                    self._player.guild_id,
                    payload.threshold,
                )

                self._player._node._client._dispatch(
                    "track_stuck", self._player, payload
                )

            case "WebSocketClosedEvent":
                payload = msgspec.convert(data, WebSocketClosedEvent)

                _log.warning(
                    "Player %s: Lavalink voice WS closed. Code %s, Reason: %s",
                    self._player.guild_id,
                    payload.code,
                    payload.reason,
                )

                if not payload.by_remote:
                    await self._dispatch_voice_update()

            case _:
                _log.debug(
                    "Player %s received unhandled event type: %s",
                    self._player.guild_id,
                    event_type,
                )

    def _update_state(self, state: PlayerState, /) -> None:
        self._player._last_position = state.position
        self._player._last_update = time.monotonic()

        _log.debug(
            "Player %s: Synced position to %dms (connected %s)",
            self._player.guild_id,
            state.position,
            state.connected,
        )

    async def on_voice_state_update(self, data: GuildVoiceState) -> None:
        self._player._connection.session_id = data.get("session_id")
        self._player._connection.channel_id = str(data.get("channel_id"))

        await self._dispatch_voice_update()
        self._player._check_inactivity()

    async def _dispatch_voice_update(self) -> None:
        if not self._player._connection.is_complete or not self._player._node:
            return

        assert self._player._connection.token is not None
        assert self._player._connection.endpoint is not None
        assert self._player._connection.session_id is not None
        assert self._player._connection.channel_id is not None
        assert self._player._node._resume_session is not None

        voice_state = PlayerVoiceState(
            token=self._player._connection.token,
            endpoint=self._player._connection.endpoint,
            session_id=self._player._connection.session_id,
            channel_id=self._player._connection.channel_id,
        )

        request_data = UpdatePlayerRequest(voice=voice_state)

        try:
            await self._player._node._manager.update_player(
                session_id=self._player._node._resume_session,
                guild_id=str(self._player.guild_id),
                data=request_data,
            )
            _log.debug(
                "Player %s: Successfully dispatched voice update to Node %r.",
                self._player.guild_id,
                self._player._node.id,
            )
        except Exception as exc:
            _log.error(
                "Player %s: Failed to dispatch voice update to Node %r. Error: %s",
                self._player.guild_id,
                self._player._node.id,
                exc,
                exc_info=True,
            )

        self._player._connection._connected_flag.set()
