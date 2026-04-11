"""
MIT License

Copyright (c) 2026-present ReWaveLink Development Team.

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

from relink.models.track import Playable

if TYPE_CHECKING:
    from relink.models.playlist import Playlist


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
    ) -> tuple[list[Playable], int]:
        if isinstance(tracks, Playable):
            return [tracks], 1

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
        tracks: :class:`relink.models.Playable` | :class:`relink.models.Playlist` | Iterable[:class:`relink.models.Playable`]
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

    def put_at(
        self,
        index: int,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        """
        Put one or more tracks at ``index``.

        Parameters
        ----------
        index: :class:`int`
            The index to insert the track(s) to.
        tracks: :class:`relink.models.Playable` | :class:`relink.models.Playlist` | Iteraeble[:class:`relink.models.Playable`]
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
        if count == 1:
            self._items.insert(index, items[0])
        elif count > 1:
            queue_list = list(self._items)
            prev = queue_list[:index]
            post = queue_list[index:]
            self._items = deque(prev + items + post)
        return count

    def remove(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        remove_all: bool = True,
    ) -> int:
        """
        Removes one or more tracks from this queue.

        Parameters
        ----------
        tracks: :class:`relink.models.Playable` | :class:`relink.models.Playlist` | Iterable[:class:`relink.models.Playable`]
            The track(s) or playlist to remove from the queue.
        remove_all: :class:`bool`
            Whether to remove all occurrences of a track from this queue. When set to ``False``, only the first occurrence of each
            track is removed. Defaults to ``True``.

        Returns
        -------
        :class:`int`
            The number of tracks removed from the queue.
        """
        items, _ = self._materialize_tracks(tracks, atomic=False)
        count = 0
        for i in items:
            if remove_all:
                while i in self._items:
                    self._items.remove(i)
                    count += 1

                    if i not in self._items:
                        break
            else:
                try:
                    self._items.remove(i)
                except ValueError:
                    continue
                else:
                    count += 1
        return count

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()
