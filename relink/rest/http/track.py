from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from ..schemas import track

if TYPE_CHECKING:
    from .base import HTTPClient


class TrackHTTPMixin:
    """Mixin for Track related HTTP operations."""

    async def load_track(
        self: HTTPClient, identifier: str
    ) -> track.TrackLoadingResponse:
        url = "/loadtracks/"
        res = await self.request("GET", url, params={"identifier": identifier})
        return msgspec.json.decode(res, type=track.TrackLoadingResponse)

    async def decode_track(
        self: HTTPClient, encoded: str
    ) -> track.TrackLoadingResponse:
        url = "/decodetrack/"
        res = await self.request("GET", url, params={"encodedTrack": encoded})
        return msgspec.json.decode(res, type=track.TrackLoadingResponse)

    async def decode_tracks(
        self: HTTPClient, encoded_tracks: list[str]
    ) -> track.TrackLoadingResponse:
        url = "/decodetracks/"
        res = await self.request("GET", url, data=encoded_tracks)
        return msgspec.json.decode(res, type=track.TrackLoadingResponse)
