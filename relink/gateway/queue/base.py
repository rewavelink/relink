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

        return list(self._items)[index]

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
    ) -> list[Playable]:
        if isinstance(tracks, Playable):
            ret = [tracks]
        elif atomic:
            ret = [t for t in tracks if self._ensure_playable(t)]
        else:
            ret = list(tracks)
        return ret

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
        tracks = self._materialize_tracks(tracks, atomic=atomic)
        count = len(tracks)
        if count != 0:
            self._items.extend(tracks)
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
        tracks = self._materialize_tracks(tracks, atomic=atomic)
        count = len(tracks)

        deque_length = len(self._items)

        if count == 1:
            self._items.insert(index, tracks[0])
        elif count > 1:
            # handle negative index
            if index < 0:
                index += deque_length
            index = max(0, min(index, deque_length))

            if index >= (deque_length - index): # index is closer to the right, so we rotate right instead
                k = deque_length - index
                self._items.rotate(k)
                self._items.extend(tracks)
                self._items.rotate(-k)
            else:
                self._items.rotate(-index)
                self._items.extendleft(reversed(tracks)) # extendleft inserts in reverse, so we have to re-reverse it
                self._items.rotate(index)  

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
        tracks = self._materialize_tracks(tracks, atomic=False)
        count = 0
        for track in tracks:
            while True:
                try:
                    self._items.remove(track)
                except ValueError:
                    break
                else:
                    count += 1
                    if not remove_all:
                        break
        return count

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()
