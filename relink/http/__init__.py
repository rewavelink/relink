"""
relink.http
~~~~~~~~~~~~

HTTP manager(s) for the library.
"""

import importlib.util
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .base import BaseHTTPManager

HAS_CURL: bool = bool(importlib.util.find_spec("curl_cffi"))
print(HAS_CURL)

def get_http_manager() -> type["BaseHTTPManager"]:
    """Selects and returns the best available HTTP Manager class."""
    if HAS_CURL:
        from .curl_cffi import CurlHTTPManager
        return CurlHTTPManager

    from .aiohttp import AioHTTPManager
    return AioHTTPManager


__all__ = (
    "BaseHTTPManager",
    "HAS_CURL",
    "get_http_manager",
)
