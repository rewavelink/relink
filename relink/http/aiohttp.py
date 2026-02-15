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

from collections.abc import Mapping
from typing import Any, Optional

import aiohttp

from .base import BaseHTTPManager


class AioHTTPManager(BaseHTTPManager):
    """Aiohttp implementation of the HTTP Manager."""

    def __init__(self) -> None:
        self._session: aiohttp.ClientSession | None = None

    async def setup(self) -> None:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()

    async def request(
        self,
        method: str,
        url: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, Any] | None = None,
        json: Optional[Any] = None,
        data: Optional[Any] = None,
    ) -> Any:
        if self._session is None:
            await self.setup()

        assert self._session is not None

        async with self._session.request(
            method=method,
            url=url,
            headers=headers,
            params=params,
            json=json,
            data=data,
        ) as response:
            if response.status == 204:
                return None

            try:
                return await response.json()
            except (aiohttp.ContentTypeError, ValueError):
                return await response.text()

    async def close(self) -> None:
        if self._session is not None and not self._session.closed:
            await self._session.close()

    @property
    def is_closed(self) -> bool:
        return self._session is None or self._session.closed
