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

from typing import Any

import msgspec

from .playlist import PlaylistInfo
from .enums import TrackLoadResult


class Track(msgspec.Struct, kw_only=True):
    """Represents a Track structure payload."""

    encoded: str
    info: TrackInfo
    plugin_info: Any = msgspec.field(name="pluginInfo")
    user_data: Any = msgspec.field(name="userData")


class TrackInfo(msgspec.Struct, kw_only=True):
    """Represents a Track's info available under :attr:`Track.info`."""

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


# /v4/loadtracks?identifier=ID


class TrackLoadingResult(msgspec.Struct, kw_only=True):
    """Represents a TrackLoadingResult structure payload."""

    load_type: TrackLoadResult = msgspec.field(name="loadType")
    data: TrackLoadingData


class TrackLoadingData(msgspec.Struct, kw_only=True):
    """Represents a TrackLoadingResult structure payload."""

    info: PlaylistInfo
    plugin_info: dict[str, Any] = msgspec.field(name="pluginInfo")
    tracks: list[Track]


TrackDecodeResult = Track
