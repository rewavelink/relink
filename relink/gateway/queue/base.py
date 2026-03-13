"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2025-present ReWaveLink Development Team.

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

from collections import deque
from collections.abc import Iterable, Iterator
from itertools import islice
from typing import TYPE_CHECKING, TypeGuard, overload

if TYPE_CHECKING:
    from relink.models.playlist import Playlist
    from relink.models.track import Playable


class ReadableCollection:
    """A base class for read-only collection operations."""

    __slots__ = ("_items",)

    def __init__(self) -> None:
        self._items: deque[Playable] = deque()

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} size={len(self._items)}>"

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return len(self._items) > 0

    def __iter__(self) -> Iterator[Playable]:
        return iter(self._items)

    def __contains__(self, item: object) -> bool:
        return item in self._items

    @overload
    def __getitem__(self, index: int) -> Playable: ...

    @overload
    def __getitem__(self, index: slice) -> list[Playable]: ...

    def __getitem__(self, index: int | slice) -> Playable | list[Playable]:
        if isinstance(index, int):
            return self._items[index]

        size = len(self._items)
        start, stop, step = index.indices(size)
        if step > 0:
            return list(islice(self._items, start, stop, step))

        reverse_start = size - 1 - start
        reverse_stop = size - 1 - stop
        return list(islice(reversed(self._items), reverse_start, reverse_stop, -step))

    def _ensure_playable(self, value: object) -> TypeGuard[Playable]:
        if not isinstance(value, Playable):
            raise TypeError(f"Expected Playable, got {type(value).__name__}")
        return True


class MutableQueueBase(ReadableCollection):
    """A base class for collections that can be modified"""

    __slots__ = ()

    def _materialize_tracks(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        *,
        atomic: bool,
    ) -> tuple[Iterable[Playable], int]:
        if isinstance(tracks, Playable):
            return (tracks,), 1

        if atomic:
            validated = [t for t in tracks if self._ensure_playable(t)]
            return validated, len(validated)

        items = list(tracks)
        return items, len(items)

    def put(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        """
        Put one or more tracks at the end of the queue.

        Parameters
        ----------
        tracks: :class:`Playable` | :class:`Playlist` | Iterable[:class:`Playable`]
            The track(s) or playlist to add to the queue.
        atomic: :class:`bool`
            Whether to insert the items atomically. If ``True``, all items must be
            Playable or a TypeError is raised and nothing is added. If ``False``,
            non-Playable items are filtered out. Defaults to ``True``.

        Returns
        -------
        :class:`int`
            The number of tracks added to the queue.

        Raises
        ------
        :exc:`TypeError`
            When ``atomic=True`` and a non-Playable item is encountered.
        """
        items, count = self._materialize_tracks(tracks, atomic=atomic)
        if count != 0:
            self._items.extend(items)
        return count

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()
