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

from typing import TYPE_CHECKING, cast

from relink.rest.enums import TrackLoadResult
from relink.utils import cached_property

from .base import BaseModel
from .playlist import Playlist
from .track import Playable

if TYPE_CHECKING:
    from relink.gateway.schemas.events import TrackException
    from relink.rest.schemas.track import PlaylistData, Track, TrackLoadingResponse

__all__ = ("SearchResult",)


class SearchResult(BaseModel[TrackLoadingResponse]):
    """
    The result of a track search.
    """

    __slots__ = "_cs_data"

    @property
    def type(self) -> TrackLoadResult:
        """The result type."""
        return self._data.load_type

    def is_error(self) -> bool:
        """Whether this search result is an error."""
        return self.type is TrackLoadResult.ERROR

    def is_empty(self) -> bool:
        """
        Whether this search result is empty.
        An empty search result has no :attr:`SearchResult.result`.
        """
        return self.type is TrackLoadResult.EMPTY

    @cached_property("_cs_data")
    def result(self) -> Playlist | Playable | list[Playable] | None:
        r"""
        The data of the search result. Depending on :attr:`SearchResult.type`, this property
        will return a different value.

        If type is :attr:`TrackLoadResult.TRACK`, this will return a :class:`Playable`.
        If type is :attr:`TrackLoadResult.PLAYLIST`, this will return a :class:`Playlist`.
        If type is :attr:`TrackLoadResult.SEARCH`, this will return a list of :class:`Playable`\s.
        """

        match self.type:
            case TrackLoadResult.TRACK:
                return Playable(
                    client=self._client,
                    data=cast("Track", self._data.data),
                    playlist=None,
                )
            case TrackLoadResult.PLAYLIST:
                return Playlist(
                    client=self._client, data=cast("PlaylistData", self._data.data)
                )
            case TrackLoadResult.SEARCH:
                tracks = cast("list[Track]", self._data.data)
                return [
                    Playable(client=self._client, data=d, playlist=None) for d in tracks
                ]
            case _:
                return None

    @property
    def exception(self) -> TrackException | None:
        """
        The raw exception data of this search result.

        This will be ``None`` if :meth:`SearchResult.is_error` is ``False``.
        """
        if not self.is_error():
            return None

        return cast("TrackException", self._data.data)
