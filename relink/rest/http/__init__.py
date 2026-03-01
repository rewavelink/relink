"""
relink.rest.http
~~~~~~~~~~~~~~~~
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from ...network import HTTPFactory
from ...network.base import BaseHTTPManager, BaseWebsocketManager
from .info import InfoHTTPMixin
from .planner import RoutePlannerHTTPMixin
from .player import PlayerHTTPMixin
from .session import SessionHTTPMixin
from .track import TrackHTTPMixin

__all__ = ("RESTClient",)


class RESTClient(
    InfoHTTPMixin,
    RoutePlannerHTTPMixin,
    PlayerHTTPMixin,
    SessionHTTPMixin,
    TrackHTTPMixin,
):
    def __init__(
        self,
        manager: BaseHTTPManager[Any],
        *,
        base_url: str = "",
        headers: dict[str, str] | None = None,
    ) -> None:
        self._manager = manager
        self._base_url = base_url.removesuffix("/")
        self._default_headers = headers or {}

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Any | None = None,
        data: Any | None = None,
    ) -> Any:
        merged_headers = {**self._default_headers, **(headers or {})}
        full_url = self._base_url + url if url.startswith("/") else url

        return await self._manager.request(
            method,
            full_url,
            headers=merged_headers or None,
            params=params,
            json=json,
            data=data,
        )

    async def connect_ws(
        self,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
    ) -> BaseWebsocketManager[Any, Any]:
        if not self._manager._session:
            raise RuntimeError("can not create websocket without a manager session")
        merged_headers = {**self._default_headers, **(headers or {})}
        safe = self._base_url.startswith("https://")
        ws_prefix = "wss://" if safe else "ws://"
        base_url = self._base_url.removeprefix("https://").removeprefix("http://")
        full_url = ws_prefix  + base_url + url if url.startswith("/") else url
        ws = HTTPFactory.create_websocket(self._manager._session)
        await ws.connect(
            full_url,
            headers=merged_headers,
        )
        return ws

    async def setup(self) -> None:
        await self._manager.setup()

    async def close(self) -> None:
        await self._manager.close()

    @property
    def is_closed(self) -> bool:
        return self._manager.is_closed

    async def __aenter__(self) -> RESTClient:
        await self.setup()
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.close()
