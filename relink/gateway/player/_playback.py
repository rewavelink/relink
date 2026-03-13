from __future__ import annotations

import time

from relink.rest.schemas.filters import PlayerFilters
from relink.rest.schemas.player import UpdatePlayerRequest, UpdatePlayerTrackRequest

from ...models.track import Playable
from ..enums import QueueMode
from ._base import HandlerBase, _log

__all__ = ()


class PlaybackHandler(HandlerBase):
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
            endtime=end,
            volume=volume,
            paused=paused,
        )

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild_id),
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

        data = UpdatePlayerRequest(track=None)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild_id),
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
            "Player %s: Stopped playback and reset state.", self._player.guild_id
        )
        self._player._check_inactivity()

    async def pause(self, value: bool = True, /) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(paused=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild_id),
            data=data,
        )

        self._player._paused = value
        _log.debug("Player %s: Set paused state to %s", self._player.guild_id, value)

    async def resume(self) -> None:
        await self.pause(False)

    async def previous(self) -> None:
        track = self._player._queue.previous()
        await self.play(track)

    async def skip(self) -> None:
        next_track = self._player._queue.get()
        await self.play(next_track)

    async def seek(self, position: int, /) -> None:
        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(position=position)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild_id),
            data=data,
        )

        self._player._last_position = position
        self._player._last_update = time.monotonic()

        _log.debug("Player %s: Seeked to %dms", self._player.guild_id, position)

    async def set_volume(self, value: int, /) -> None:
        if not 0 <= value <= 1000:
            raise ValueError("Volume must be between 0 and 1000.")

        node = self._player.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(volume=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self._player.guild_id),
            data=data,
        )

        self._player._volume = value
        _log.debug("Player %s: Set volume to %d.", self._player.guild_id, value)

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
            guild_id=str(self._player.guild_id),
            data=data,
        )

        self._player._filters = filters

        if seek:
            await self.seek(self._player.position)

        _log.debug(
            "Player %s: Successfully applied filters: %r",
            self._player.guild_id,
            filters,
        )
