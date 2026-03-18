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

import abc
from typing import TYPE_CHECKING, Any, Generic, TypeVar

import msgspec

if TYPE_CHECKING:
    from ..schemas import receive
    from ..node import Node

T = TypeVar("T", bound=msgspec.Struct, covariant=True)


class EventModel(abc.ABC, Generic[T]):
    """Base class where all events models derive from.

    This is an :class:`abc.ABC` subclass.
    """

    __repr_attrs__: tuple[str, ...]
    _underlying: T

    def __init__(self, underlying: T, node: Node) -> None:
        self._underlying = underlying
        self._node: Node = node

    @property
    def node(self) -> Node:
        """The node that received the event."""
        return self._node

    def __getattr__(self, name: str) -> Any:
        try:
            return getattr(self._underlying, name)
        except AttributeError as exc:
            raise AttributeError(
                f"{self.__class__.__name__} does not have an attribute named {name}"
            ) from exc

    def __repr__(self) -> str:
        attrs = ", ".join(f"{a}={getattr(self, a)}" for a in self.__repr_attrs__)
        return f"<{self.__class__.__name__} {attrs}>"


class ReadyEvent(EventModel["receive.ReadyEvent"]):
    """Represents a ready event."""

    __repr_attrs__ = ("resumed", "session_id")

    resumed: bool
    """Whether the session was resumed, if this is ``False`` it implies a new connection
    was created.
    """
    session_id: str
    """The secret session ID."""


class PlayerUpdateEvent(EventModel["receive.PlayerUpdateEvent"]):
    """Represents a player_update event."""

    __repr_attrs__ = ("state", "guild_id")

    state: receive.PlayerState
    """The state of the player."""
    guild_id: int
    """The guild ID of the player."""


class StatsEvent(EventModel["receive.StatsEvent"]):
    """Represents a stats event."""

    __repr_attrs__ = (
        "players",
        "playing_players",
        "uptime",
        "memory",
        "cpu",
        "frame_stats",
    )

    players: int
    """The players count attached to the node."""
    playing_players: int
    """The players count attached to the node that are playing a track."""
    uptime: int
    """The node uptime in milliseconds."""
    memory: receive.MemoryStats
    """The memory stats of the node."""
    cpu: receive.CPUStats
    """The CPU stats of the node."""
    frame_stats: receive.FrameStats | None
    """The frame stats of the node."""


class WSCloseEvent(EventModel["receive.WebSocketClosedEvent"]):
    """Represents a ws_close event."""

    __repr_attr__ = (
        "code",
        "reason",
        "by_remote",
    )

    code: int
    """The Discord close event code."""
    reason: str
    """The reason why the connection was closed."""
    by_remote: bool
    """Whether the closure was made by Discord."""
