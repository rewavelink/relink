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

from .playlist import PlaylistInfo
from ..enums import TrackLoadResult


class Track(msgspec.Struct, kw_only=True):
    """
     Represents a Track payload.

    :attr encoded: Base64-encoded track string.
    :attr info: Track metadata object (:class:`TrackInfo`).
    :attr plugin_info: Additional track info provided by plugins.
    :attr user_data: Additional track data previously provided (:class:`UpdatePlayerRequest`).
    """

    encoded: str
    info: TrackInfo
    plugin_info: Any = msgspec.field(name="pluginInfo")
    user_data: Any = msgspec.field(name="userData")


class TrackInfo(msgspec.Struct, kw_only=True):
    """
    Represents metadata for Track, available under :attr:`Track.info`.

    :attr identifier: Unique track identifier.
    :attr title: Track title.
    :attr author: Track author or artist name.
    :attr length: Total length of the track in milliseconds.
    :attr position: Current playback position in milliseconds.
    :attr is_seekable: Whether the track is seekable.
    :attr is_stream: Whether the track is a live stream.
    :attr uri: The track's URI, if available (nullable).
    :attr artwork_url: Artwork URL, if available (nullable).
    :attr isrc: International Standard Recording Code (nullable).
    :attr source_name: Name of the source manager that provided the track.
    """

    identifier: str
    uri: str | None = None

    title: str
    author: str
    length: int
    position: int

    is_seekable: bool = msgspec.field(name="isSeekable")
    is_stream: bool = msgspec.field(name="isStream")

    source_name: str = msgspec.field(name="sourceName")
    artwork_url: str | None = msgspec.field(name="artworkUrl", default=None)
    isrc: str | None = msgspec.field(name="isrc", default=None)


class TrackLoadingResponse(msgspec.Struct, kw_only=True):
    """
    Represents a TrackLoadingResponse structure payload.

    :attr load_type: Type of load result (:class:`TrackLoadResult`).
    :attr data: Associated load result data (:class:`TrackLoadingData`).
    """

    load_type: TrackLoadResult = msgspec.field(name="loadType")
    data: TrackLoadingData


class TrackLoadingData(msgspec.Struct, kw_only=True):
    """
    Contains the detailed results of a track load request.

    For playlists, this contains playlist metadata and a list of tracks.
    For single-track results or search results, the track is wrapped in a playlist-like structure.

    :attr info: Playlist metadata (:class:`PlaylistInfo`).
    :attr plugin_info: Additional data returned by the source plugin.
    :attr tracks: List of loaded tracks (:class:`Track`).
    """

    info: PlaylistInfo
    plugin_info: dict[str, Any] = msgspec.field(name="pluginInfo")
    tracks: list[Track]


TrackDecodeResponse = Track
TracksDecodeResponse = list[Track]
