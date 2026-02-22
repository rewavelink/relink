from __future__ import annotations

from typing import TYPE_CHECKING

import msgspec

from ..schemas import planner

if TYPE_CHECKING:
    from .base import HTTPClient


class RoutePlannerHTTPMixin:
    """Mixin for Planner related HTTP operations."""

    async def status(
        self: HTTPClient,
    ) -> planner.RoutePlannerStatusResponse:
        url = "/routeplanner/status"
        res = await self.request("GET", url)
        return msgspec.json.decode(res, type=planner.RoutePlannerStatusResponse)

    async def unmark_failed_address(
        self: HTTPClient, data: planner.UnmarkFailedAddressRequest
    ) -> None:
        url = "/routeplanner/free/address"
        await self.request("POST", url, data=msgspec.json.encode(data))

    async def unmark_all_failed_addresses(self: HTTPClient) -> None:
        url = "/routeplanner/free/all"
        await self.request("POST", url)
