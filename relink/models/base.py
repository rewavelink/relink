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

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..gateway.client import Client


class BaseModel[D]:
    """
    The base class for all relink models.

    This class provides the connection to the :class:`relink.Client`
    and holds the raw msgspec data structure.
    """

    def __init__(self, *, client: Client, data: D) -> None:
        self._client: Client = client
        self._data: D = data

    def __repr__(self) -> str:
        attrs = ", ".join(
            f"{k}={v!r}"
            for k, v in self._data.__dict__.items()
            if v is not None and not isinstance(v, (list, dict))
        )
        return f"<relink.{self.__class__.__name__} {attrs}>"

    @property
    def client(self) -> Client:
        """The :class:`relink.Client` instance associated with this object."""
        return self._client

    @property
    def data(self) -> D:
        """The raw msgspec schema object holding the data for this model."""
        return self._data
