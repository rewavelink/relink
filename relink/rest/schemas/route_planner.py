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
from typing import Annotated

import msgspec

from .enums import IPBlockType, RoutePlannerType


class DetailsObject(msgspec.Struct, kw_only=True):
    """Represents a DetailsObject structure payload."""

    ip_block: IPBlockObject = msgspec.field(name="ipBlock")
    rotate_index: Annotated[str | None, "Only for RotatingIpRoutePlanner type"] = (
        msgspec.field(name="rotateIndex", default=None)
    )
    ip_index: Annotated[
        int | None, "Only for RotatingIpRoutePlannerRotatingIpRoutePlanner type"
    ] = msgspec.field(name="ipIndex", default=None)
    current_address: Annotated[str | None, "Only for RotatingIpRoutePlanner type"] = (
        msgspec.field(name="currentAddress", default=None)
    )
    current_address_index: Annotated[
        int | None, "Valid for types: NanoIpRoutePlanner, RotatingNanoIpRoutePlanner"
    ] = msgspec.field(name="currentAddressIndex", default=None)
    block_index: Annotated[
        int | None,
        "Only for RotatingNanoIpRoutePlanner type",
    ] = msgspec.field(name="blockIndex", default=None)


class IPBlockObject(msgspec.Struct, kw_only=True):
    """Represents an IPBlockObject structure payload."""

    type: IPBlockType
    size: int


class FailingAddressObject(msgspec.Struct, kw_only=True):
    """Represents a FailingAddressObject structure payload."""

    address: str = msgspec.field(name="failingAddress")
    timestamp: int = msgspec.field(name="failingTimestamp")
    time: str = msgspec.field(name="failingTime")


class RoutePlannerStatusResponse(msgspec.Struct, kw_only=True):
    """Represents a RoutePlannerStatusResponse structure payload."""

    class_: RoutePlannerType = msgspec.field(name="class")
    details: DetailsObject | None = None


class UnmarkFailedAddressRequest(msgspec.Struct, kw_only=True):
    """Represents an UnmarkFailedAddressRequest structure payload."""

    address: str


UnmarkFailedAddressResponse = None
UnmarkAllFailedAddressesResponse = None
