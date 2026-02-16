"""
relink.http
~~~~~~~~~~~~

HTTP manager(s) for the library.
"""
from __future__ import annotations

import importlib.util
from typing import TYPE_CHECKING, cast
from typing_extensions import TypeIs

import aiohttp

if TYPE_CHECKING:
    from .base import BaseHTTPManager, BaseWebsocketManager

    import curl_cffi  # curl_cffi may not be available, but aiohttp will always be thanks to the discord.py requirement

    SessionType = curl_cffi.AsyncSession[curl_cffi.Response] | aiohttp.ClientSession
    WebsocketType = curl_cffi.AsyncWebSocket | aiohttp.ClientWebSocketResponse


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
    def http_manager(cls) -> type[BaseHTTPManager]:
        return cast(
            type["BaseHTTPManager"],
            cls._select("CurlHTTPManager", "AioHTTPManager"),
        )

    @classmethod
    def websocket_manager(cls) -> type[BaseWebsocketManager]:
        return cast(
            type["BaseWebsocketManager"],
            cls._select("CurlWebsocketManager", "AioWebsocketManager"),
        )

    @staticmethod
    def _is_aiohttp_session(session: SessionType) -> TypeIs[aiohttp.ClientSession]:
        return isinstance(session, aiohttp.ClientSession)

    @classmethod
    def _is_ccffi_session(cls, session: SessionType) -> TypeIs[curl_cffi.AsyncSession[curl_cffi.Response]]:
        if cls.HAS_CURL:
            import curl_cffi

            return isinstance(session, curl_cffi.AsyncSession)
        return False

    @classmethod
    def from_http(cls, session: SessionType) -> BaseHTTPManager:
        if cls._is_aiohttp_session(session):
            from .aiohttp import AioHTTPManager
            return AioHTTPManager(session=session)
        elif cls._is_ccffi_session(session):
            from .curl_cffi import CurlHTTPManager
            return CurlHTTPManager(session=session)
        else:
            raise TypeError(f"expected aiohttp.ClientSession or curl_cffi.AsyncSession, got {session.__class__.__name__}")

    @classmethod
    def create_websocket(cls, session: SessionType) -> BaseWebsocketManager:
        if cls._is_aiohttp_session(session):
            from .aiohttp import AioWebsocketManager
            return AioWebsocketManager(session)
        elif cls._is_ccffi_session(session):
            from .curl_cffi import CurlWebsocketManager
            return CurlWebsocketManager(session)
        else:
            raise TypeError(f"expected aiohttp.ClientSession or curl_cffi.AsyncSession, got {session.__class__.__name__}")


__all__ = (
    "BaseHTTPManager",
    "BaseWebsocketManager",
    "HTTPFactory",
)
