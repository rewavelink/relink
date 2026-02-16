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

from abc import ABC, abstractmethod
from collections.abc import Mapping
from typing import Any


class BaseHTTPManager(ABC):
    """Abstract Base Class for ReWaveLink HTTP backends."""

    @abstractmethod
    async def setup(self) -> None:
        """Initialize the underlying session (ClientSession or AsyncSession)"""
        pass

    @abstractmethod
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
        """Perform an async HTTP request and return the response body/JSON"""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the session and cleanup connectors."""
        pass

    @property
    @abstractmethod
    def is_closed(self) -> bool:
        """Check if the underlying session is closed."""
        pass


class BaseWebsocketManager(ABC):
    """Abstract Base Class for ReWaveLink Websocket backends."""

    @abstractmethod
    async def connect(
        self,
        url: str,
        # ! heartbeat: float, => since curl_cffi doesn't have one
        headers: Mapping[str, str],
    ) -> None:
        """Establish a connection to the Lavalink Websocket server."""
        pass

    @abstractmethod
    async def receive(self) -> Any:
        """Wait for a message from the websocket and return the parsed JSON data."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the websocket connection and perform cleanup."""
        pass

    @property
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if the websocket is currently connected and active."""
        pass
