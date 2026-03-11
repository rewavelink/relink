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
import random
from collections import deque
from collections.abc import Iterable, Iterator
from itertools import islice
from typing import Literal, Self, TypeGuard, overload

from ..models.playlist import Playlist
from ..models.track import Playable
from .enums import QueueMode
from .errors import QueueEmpty


class QueueBase:
    """
    A queue implementation for managing playable tracks.

    This queue supports multiple modes including normal, loop, and loop_all.
    It maintains a history of played tracks and supports asynchronous waiting.

    Parameters
    ----------
    history: bool
        Whether to maintain a history of played tracks. Defaults to ``True``.
    mode: :class:`QueueMode`
        The initial queue mode. Defaults to :class:`QueueMode.normal`.
    """

    __slots__ = ("_items",)

    def __init__(
        self,
    ) -> None:
        self._items: deque[Playable] = deque()

    def __len__(self) -> int:
        return len(self._items)

    def __bool__(self) -> bool:
        return bool(self._items)

    def __iter__(self) -> Iterator[Playable]:
        return iter(self._items)

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

    def __contains__(self, item: Playable) -> bool:
        return item in self._items

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(size={len(self._items)})"

    @staticmethod
    def _is_playable(value: object) -> TypeGuard[Playable]:
        return isinstance(value, Playable)

    @classmethod
    def _ensure_playable(cls, value: object) -> bool:
        if not cls._is_playable(value):
            raise TypeError("This queue only accepts Playable items.")
        return True

    @classmethod
    def _materialize_tracks(
        cls,
        tracks: Iterable[Playable] | Playable | Playlist,
        *,
        atomic: bool,
    ) -> tuple[Iterable[Playable], int]:
        if cls._is_playable(tracks):
            return (tracks,), 1

        if not isinstance(tracks, Iterable):
            raise TypeError("Expected Playable, Playlist, or iterable of Playable")

        if atomic:
            validated = [t for t in tracks if cls._ensure_playable(t)]
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
        if not count:
            return 0

        self._items.extend(items)
        return count

    def get(self) -> Playable:
        """
        Get and remove the next track from the queue.

        Returns
        -------
        :class:`Playable`
            The retrieved track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty and cannot retrieve a track.
        """
        if not self:
            raise QueueEmpty

        return self._items.popleft()

    def copy(self) -> Self:
        """
        Create a shallow copy of the queue.

        Returns
        -------
        :class:`QueueBase`
            A shallow copy of the queue with the same items, mode, and history settings.
        """
        new_queue = self.__class__()
        new_queue._items = self._items.copy()
        return new_queue

    def clear(self) -> None:
        """Remove all items from the queue."""
        self._items.clear()


class Queue(QueueBase):
    __slots__ = (
        "_mode",
        "_history_enabled",
        "_lock",
        "_items",
        "_waiters",
        "_history",
        "_current_track",
    )

    def __init__(
        self,
        *,
        history: bool = True,
        mode: QueueMode = QueueMode.normal,
    ) -> None:
        self._mode: QueueMode = mode
        self._history_enabled: bool = history
        self._lock: asyncio.Lock = asyncio.Lock()

        self._items: deque[Playable] = deque()
        self._waiters: deque[asyncio.Future[None]] = deque()
        self._history: History | None = History() if history else None

        self._current_track: Playable | None = None

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"size={len(self._items)}, "
            f"mode={self._mode.name}, "
            f"current_track={self._current_track!r})"
        )

    @property
    def mode(self) -> QueueMode:
        """
        The current queue mode.

        - :attr:`QueueMode.normal`: Tracks are played in order and removed from the queue.
        - :attr:`QueueMode.loop`: :attr:`current_track` is repeated indefinitely until manually changed.
        - :attr:`QueueMode.loop_all`: When the queue is empty, all tracks from history are restored
            to the queue and played again.

        Returns
        -------
        :class:`QueueMode`
            The current queue mode.
        """
        return self._mode

    @mode.setter
    def mode(self, value: QueueMode) -> None:
        if not isinstance(value, QueueMode):  # pyright: ignore[reportUnnecessaryIsInstance]
            raise TypeError(f"Expected QueueMode, got {type(value).__name__}")
        self._mode = value

    @property
    def current_track(self) -> Playable | None:
        """
        The currently loaded track.

        This track is typically the one being played or most recently played.

        This is also used when :attr:`mode` is set to :attr:`QueueMode.loop` to
        determine which track to repeat. This can be manually set too.

        Returns
        -------
        :class:`Playable` | None
            The current track, or ``None`` if not set.
        """
        return self._current_track

    @current_track.setter
    def current_track(self, value: Playable | None) -> None:
        if value is not None:
            self._ensure_playable(value)
        self._current_track = value

    @property
    def history(self) -> History | None:
        """
        The queue history.

        Returns
        -------
        :class:`History` | None
            The queue history if history is enabled, otherwise ``None``.
        """
        return self._history

    def _wakeup_next(self) -> None:
        while self._waiters:
            waiter = self._waiters.popleft()
            if not waiter.done():
                waiter.set_result(None)
                return

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
        count = super().put(tracks, atomic=atomic)
        self._wakeup_next()
        return count

    def put_at(self, index: int, track: Playable) -> None:
        """
        Insert a track into the queue at a specific index.

        Parameters
        ----------
        index: :class:`int`
            The index to insert the track at.
        track: :class:`Playable`
            The track to insert.

        Raises
        ------
        :exc:`TypeError`
            The track is not a Playable.
        """
        self._ensure_playable(track)
        self._items.insert(index, track)
        self._wakeup_next()

    async def put_wait(
        self,
        tracks: Iterable[Playable] | Playable | Playlist,
        /,
        *,
        atomic: bool = True,
    ) -> int:
        """
        Asynchronously put one or more tracks into the queue.

        This method is thread-safe and maintains insert order through a lock.

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
        async with self._lock:
            count = self.put(tracks, atomic=atomic)

        if count:
            await asyncio.sleep(0)

        return count

    def get(self) -> Playable:
        """
        Get the next track from the queue, respecting the current queue mode.

        If the queue is in ``loop`` mode, returns the current track.
        If the queue is in ``loop_all`` mode and empty, restores tracks from history.

        Returns
        -------
        :class:`Playable`
            The retrieved track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty and cannot retrieve a track.
        """
        if self._mode is QueueMode.loop and self._current_track is not None:
            return self._current_track

        if self._mode is QueueMode.loop_all and not self:
            if self._history is not None:
                if self._history:
                    self._items.extend(self._history)
                    self._history.clear()

                if self._current_track is not None:
                    self._items.append(self._current_track)
                    self._current_track = None

        if not self:
            raise QueueEmpty

        return self.pop()

    def get_at(self, index: int) -> Playable:
        """
        Get a track from a specific queue index.

        This method retrieves exactly the item at ``index`` and sets it as current.

        Parameters
        ----------
        index: :class:`int`
            The index to pop from.

        Returns
        -------
        :class:`Playable`
            The retrieved track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty and cannot retrieve a track.
        IndexError
            There is no item at the given index.
        """
        if not self:
            raise QueueEmpty

        return self.pop_at(index)

    async def get_wait(self) -> Playable:
        """
        Asynchronously get a track from the queue, waits if necessary.

        This method will wait indefinitely until a track is available in the queue.

        This method can be used to implement a system that waits for a next track to
        play after the current track finishes, for example.

        Returns
        -------
        :class:`Playable`
            The retrieved track.
        """
        while not self:
            waiter = asyncio.get_running_loop().create_future()
            self._waiters.append(waiter)

            try:
                await waiter
            except BaseException:
                waiter.cancel()
                try:
                    self._waiters.remove(waiter)
                except ValueError:
                    pass

                if self and not waiter.cancelled():
                    self._wakeup_next()
                raise

        return self.get()

    def pop(self) -> Playable:
        """
        Remove and return the next track from the queue.

        The returned track is set as the current track.
        If history is enabled, the previous current track is added to history.

        Returns
        -------
        :class:`Playable`
            The popped track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty.
        """
        if not self:
            raise QueueEmpty

        track = self._items.popleft()

        self._current_track = track
        return track

    def pop_at(self, index: int) -> Playable:
        """
        Remove and return a track from a specific queue index.

        The returned track is set as the current track.
        If history is enabled, the previous current track is added to history.

        Parameters
        ----------
        index: :class:`int`
            The index to pop from.

        Returns
        -------
        :class:`Playable`
            The popped track.

        Raises
        ------
        :class:`QueueEmpty`
            The queue is empty.
        :exc:`IndexError`
            There is no item at the given index.
        """
        if not self:
            raise QueueEmpty

        track = self._items[index]
        del self._items[index]

        self._current_track = track
        return track

    def peek(self, index: int = 0) -> Playable:
        """
        Peek at an item in the queue without removing it.

        Parameters
        ----------
        index: :class:`int`
            The index to peek at. Defaults to ``0`` (the first item).

        Returns
        -------
        :class:`Playable`
            The track at the given index.

        Raises
        ------
        :exc:`IndexError`
            There is no item at the given index.
        """
        return self._items[index]

    @overload
    def remove(
        self,
        track: Playable,
        count: int,
        *,
        return_count: Literal[True],
    ) -> int: ...

    @overload
    def remove(
        self,
        track: Playable,
        count: int | None = 1,
        *,
        return_count: Literal[False] = False,
    ) -> None: ...

    def remove(
        self,
        track: Playable,
        count: int | None = 1,
        *,
        return_count: bool = False,
    ) -> int | None:
        """
        Remove a specific track from the queue.

        Searches from the left side of the queue and removes up to ``count`` instances
        of the specified track.

        Parameters
        ----------
        track: :class:`Playable`
            The track to remove.
        count: :class:`int` | None
            The number of times to remove the track. If ``None``, removes all instances.
            Defaults to ``1``.
        return_count: :class:`bool`
            Whether to return the number of tracks removed. Defaults to ``False``.

        Returns
        -------
        :class:`int` | None
            The number of tracks removed if ``return_count=True``, otherwise ``None``.

        Raises
        ------
        :exc:`TypeError`
            The track is not a Playable.
        :exc:`ValueError`
            If ``count`` is not ``None`` and is less than 0.
        """
        self._ensure_playable(track)

        if count is not None and count < 0:
            raise ValueError("count must be >= 0 or None")

        if count == 1:
            try:
                self._items.remove(track)
                return 1 if return_count else None
            except ValueError:
                return 0 if return_count else None

        initial_len = len(self._items)
        if count is None:
            self._items = deque(t for t in self._items if t != track)
        else:
            removed = 0
            new_items: deque[Playable] = deque()

            for item in self._items:
                if removed < count and item == track:
                    removed += 1
                    continue
                new_items.append(item)
            
            self._items = new_items

        return (initial_len - len(self._items)) if return_count else None

    def delete(self, index: int) -> None:
        """
        Delete a track from the queue at a specific index.

        Parameters
        ----------
        index: :class:`int`
            The index of the track to delete.

        Raises
        ------
        :exc:`IndexError`
            There is no item at the given index.
        """
        del self._items[index]

    def swap(self, old: int, new: int) -> None:
        """
        Swap two tracks in the queue by index.

        Parameters
        ----------
        old: :class:`int`
            The index of the first track.
        new: :class:`int`
            The index of the second track.

        Raises
        ------
        :exc:`IndexError`
            One or both indices are out of range.
        """
        self._items[old], self._items[new] = self._items[new], self._items[old]

    def index(self, track: Playable) -> int:
        """
        Return the index of the first occurrence of a track in the queue.

        Parameters
        ----------
        track: :class:`Playable`
            The track to find.

        Returns
        -------
        :class:`int`
            The index of the track.

        Raises
        ------
        :exc:`TypeError`
            The track is not a Playable.
        :exc:`ValueError`
            The track was not found in the queue.
        """
        self._ensure_playable(track)
        return self._items.index(track)

    def shuffle(self) -> None:
        """
        Shuffle the queue in place.

        This does not return anything.
        """
        random.shuffle(self._items)

    def copy(self) -> Queue:
        """
        Create a shallow copy of the queue.

        Returns
        -------
        :class:`Queue`
            A shallow copy of the queue with the same items, mode, and history settings.
        """
        new_queue = self.__class__(
            history=self._history_enabled,
            mode=self._mode,
        )
        new_queue._items = self._items.copy()
        new_queue._current_track = self._current_track

        if self._history is not None:
            new_queue._history = self._history.copy()

        return new_queue

    def clear(self) -> None:
        """
        Remove all items from the queue.

        This does not clear history.
        """
        super().clear()

    def clear_history(self) -> None:
        """
        Clear the queue history if history is enabled.

        If history is disabled, this method does nothing.
        """
        if self._history is not None:
            self._history.clear()

    def reset(self) -> None:
        """
        Reset the queue to its default state.

        This will:
        - Clear all items from the queue
        - Clear history
        - Reset the mode to :class:`QueueMode.normal`
        - Clear the current track
        - Cancel all waiting futures
        """
        self.clear()
        self.clear_history()

        self._current_track = None
        self._mode = QueueMode.normal

        for waiter in self._waiters:
            if not waiter.done():
                waiter.cancel()

        self._waiters.clear()


class History(QueueBase):
    pass
