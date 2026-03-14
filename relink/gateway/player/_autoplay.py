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

import asyncio
from typing import TYPE_CHECKING

from relink.models.track import Playable, Playlist

from ..enums import AutoPlayMode
from ._base import HandlerBase, _log

if TYPE_CHECKING:
    from ..player import Player


class AutoPlayHandler(HandlerBase):
    __slots__ = (
        "_mode",
        "_seeds",
        "_lock",
    )

    def __init__(self, player: Player) -> None:
        super().__init__(player)
        self._mode: AutoPlayMode = AutoPlayMode.DISABLED
        self._seeds: set[str] = set()
        self._lock: asyncio.Lock = asyncio.Lock()

    async def auto_play(self) -> None:
        if self._mode == AutoPlayMode.DISABLED:
            return

        if len(self._player.queue) > 0 or self._lock.locked():
            return

        async with self._lock:
            await self._fill_auto_queue()

    async def _fill_auto_queue(self) -> None:
        history_items = self._player.queue.history._items
        reference = self._player.current or (
            history_items[-1] if history_items else None
        )

        if not reference or not reference.identifier:
            _log.debug(
                "Player %s: AutoPlay has no seed tracks available.",
                self._player.guild_id,
            )
            return

        if len(self._seeds) > 100:
            self._seeds.clear()

        self._seeds.add(reference.identifier)

        # YouTube Radio Mix
        query = f"https://www.youtube.com/watch?v={reference.identifier}&list=RD{reference.identifier}"

        try:
            search = await self._player.node.search_track(query)

            if search.is_error() or search.is_empty():
                return

            result = search.result

            if isinstance(result, Playlist):
                tracks = result.tracks
            elif isinstance(result, list):
                tracks = result
            elif isinstance(result, Playable):
                tracks = [result]
            else:
                return

            to_add = [track for track in tracks if track.identifier not in self._seeds]

            if not to_add:
                return

            if self._mode == AutoPlayMode.ENABLED:
                self._player.queue.put(to_add[:20])

            if not self._player.current:
                next_track = (
                    to_add[0]
                    if self._mode == AutoPlayMode.PARTIAL
                    else self._player.queue.get()
                )
                await self._player.play(next_track)
        except Exception as exc:
            _log.error(
                "Player %s: AutoPlay failed: %s",
                self._player.guild_id,
                exc,
                exc_info=True,
            )
