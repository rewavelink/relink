"""
relink.http
~~~~~~~~~~~~

HTTP manager(s) for the library.
"""

import importlib.util
from typing import TYPE_CHECKING, cast

if TYPE_CHECKING:
    from .base import BaseHTTPManager, BaseWebsocketManager


class HTTPFactory:
    """HTTP/Websocket selector and factory."""

    HAS_CURL: bool = importlib.util.find_spec("curl_cffi") is not None

    @staticmethod
    def _select(curl_name: str, aiohttp_name: str) -> object:
        if HTTPFactory.HAS_CURL:
            module = __import__("relink.http.curl_cffi", fromlist=[curl_name])
            return getattr(module, curl_name)

        module = __import__("relink.http.aiohttp", fromlist=[aiohttp_name])
        return getattr(module, aiohttp_name)

    @classmethod
    def http_manager(cls) -> type["BaseHTTPManager"]:
        return cast(
            type["BaseHTTPManager"],
            cls._select("CurlHTTPManager", "AioHTTPManager"),
        )

    @classmethod
    def websocket_manager(cls) -> type["BaseWebsocketManager"]:
        return cast(
            type["BaseWebsocketManager"],
            cls._select("CurlWebsocketManager", "AioWebsocketManager"),
        )


__all__ = (
    "BaseHTTPManager",
    "BaseWebsocketManager",
    "HTTPFactory",
)
