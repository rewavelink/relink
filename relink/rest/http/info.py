from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from ..schemas import info

if TYPE_CHECKING:
    from .base import HTTPClient


class InfoHTTPMixin:
    """Mixin for Info related HTTP operations."""

    async def lavalink_info(self: HTTPClient) -> info.InfoResponse:
        url = "/info"
        res = await self.request("GET", url)
        return msgspec.json.decode(res, type=info.InfoResponse)

    async def version(
        self: HTTPClient,
    ) -> info.VersionResponse:
        url = "/version"
        res = await self.request("GET", url)
        return res.decode()

    async def stats(self: HTTPClient) -> info.StatsResponse:
        url = "/stats"
        res = await self.request("GET", url)
        return msgspec.json.decode(res, type=info.StatsResponse)
