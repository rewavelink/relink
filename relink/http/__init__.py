"""
relink.http
~~~~~~~~~~~~

HTTP manager(s) for the library.
"""

import importlib.util
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseHTTPManager, BaseWebsocketManager

HAS_CURL: bool = bool(importlib.util.find_spec("curl_cffi"))


def get_http_manager() -> type["BaseHTTPManager"]:
    """Selects and returns the best available HTTP Manager class."""
    if HAS_CURL:
        from .curl_cffi import CurlHTTPManager
        return CurlHTTPManager

    from .aiohttp import AioHTTPManager
    return AioHTTPManager


def get_websocket_manager() -> type["BaseWebsocketManager"]:
    """Selects and returns the best available Websocket Manager class."""
    if HAS_CURL:
        from .curl_cffi import CurlWebsocketManager
        return CurlWebsocketManager

    from .aiohttp import AioWebsocketManager
    return AioWebsocketManager


__all__ = (
    "BaseHTTPManager",
    "BaseWebsocketManager",
    "HAS_CURL",
    "get_http_manager",
    "get_websocket_manager",
)
