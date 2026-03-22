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

import time

import msgspec

from relink.models.track import Playable
from relink.rest.schemas.filters import PlayerFilters
from relink.rest.schemas.player import UpdatePlayerRequest, UpdatePlayerTrackRequest

from ..enums import AutoPlayMode, QueueMode
from ..errors import QueueEmpty
from ._base import HandlerBase, _log

__all__ = ()


class PlaybackHandler(HandlerBase):
    """Internal handler responsible for audio playback control logic."""

    __slots__ = ()

    async def play(
        self,
        track: Playable,
        /,
        *,
        start: int = 0,
        end: int | None = None,
        volume: int | None = None,
        paused: bool | None = None,
    ) -> Playable:
        node = self._player.node
        assert node._resume_session is not None

        volume = volume if volume is not None else self._player._volume
        paused = paused if paused is not None else self._player._paused

        track_payload = UpdatePlayerTrackRequest(encoded=track.encoded)
        data = UpdatePlayerRequest(
            track=track_payload,
            position=start,
            endtime=end if end is not None else msgspec.UNSET,
            volume=volume,
            paused=paused,
        )

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._volume = volume
        self._player._paused = paused
        self._player._last_position = start
        self._player._last_update = time.monotonic()
        self._player._queue.current_track = track

        self._player._stop_inactivity_timer()
        return track

    async def stop(
        self,
        /,
        *,
        clear_queue: bool = False,
        clear_history: bool = False,
    ) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(track=UpdatePlayerTrackRequest(encoded=None))

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._last_position = 0
        self._player._last_update = 0.0
        self._player._queue.current_track = None

        if clear_queue:
            self._player._queue.clear()
            self._player._queue.mode = QueueMode.NORMAL

        if clear_history:
            self._player._queue.clear_history()

        _log.debug(
            "Player %s: Stopped playback and reset state.", self._player.guild.id
        )
        self._player._check_inactivity()

    async def pause(self, value: bool = True, /) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(paused=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._paused = value
        _log.debug("Player %s: Set paused state to %s", self._player.guild.id, value)

    async def resume(self) -> None:
        await self.pause(False)

    async def previous(self) -> Playable:
        track = self._player._queue.previous()
        await self.play(track)
        return track

    async def skip(self) -> Playable | None:
        try:
            next_track = self._player.queue.get()
            await self.play(next_track)
            return next_track
        except QueueEmpty:
            pass

        handler = self._player._autoplay_handler
        if handler._settings.mode != AutoPlayMode.DISABLED:
            if autoplay_track := await handler.auto_play():
                return autoplay_track
            return None

        await self.stop()

    async def seek(self, position: int, /) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(position=position)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._last_position = position
        self._player._last_update = time.monotonic()

        _log.debug("Player %s: Seeked to %dms", self._player.guild.id, position)

    async def set_volume(self, value: int, /) -> None:
        if not 0 <= value <= 1000:
            raise ValueError("Volume must be between 0 and 1000.")

        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(volume=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._volume = value
        _log.debug("Player %s: Set volume to %d.", self._player.guild.id, value)

    async def set_filters(
        self,
        filters: PlayerFilters,
        /,
        *,
        seek: bool = False,
    ) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(filters=filters)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild.id),
            data=data,
        )

        self._player._filters = filters

        if seek:
            await self.seek(self._player.position)

        _log.debug(
            "Player %s: Successfully applied filters: %r",
            self._player.guild.id,
            filters,
        )
