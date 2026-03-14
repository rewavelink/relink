"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2025-present ReWaveLink Development Team.

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

import msgspec

from ..enums import TrackEndReason, TrackExceptionSeverity

if TYPE_CHECKING:
    from relink.rest.schemas.track import Track

__all__ = (
    "TrackStartEvent",
    "TrackEndEvent",
    "TrackExceptionEvent",
    "TrackException",
    "TrackStuckEvent",
    "WebSocketClosedEvent",
)


class TrackStartEvent(msgspec.Struct):
    """Represents a track start event dispatched whenever a new track starts playing."""

    _track: Track = msgspec.field(name="track")


class TrackEndEvent(msgspec.Struct):
    """Represents a track end event dispatched whenever a track stops playing."""

    track: Track
    reason: TrackEndReason


class TrackExceptionEvent(msgspec.Struct):
    """Represents a track exception event dispatched whenever an error is found when playing a track."""

    track: Track
    exception: TrackException


class TrackException(msgspec.Struct):
    """Represents a TrackExceptionEvent's :attr:`TrackExceptionEvent.exception`."""

    message: str | None
    severity: TrackExceptionSeverity
    cause: str
    cause_stack_trace: str = msgspec.field(name="causeStackTrace")


class TrackStuckEvent(msgspec.Struct):
    """Represents a track stuck event dispatched whenever a track gets stuck while playing."""

    track: Track
    threshold: int = msgspec.field(name="thresholdMs")
