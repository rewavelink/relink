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

import enum
import os
from typing import TYPE_CHECKING, Any

from relink.http import BaseWebsocketManager

from .player import Player

if TYPE_CHECKING:
    from .pool import NodePool


class NodeStatus(enum.Enum):
    """Represents the connection status of a node."""

    disconnected = 1
    connected = 2


class Node:
    """Represents a connectable Node.

    Parameters
    ----------
    uri: :class:`str`
        The URI the node will connect to. You should only provide the base URI without
        any routes, as the library will do it for you.
    password: :class:`str`
        The password of the node.
    retries: :class:`int` | :data:`None`
        The amount of retries to attempt when connecting or reconnecting this node. Whenever the limit
        is reached, it closes the node automatically. If this is set to ``None``, it retries indefinetely.
        Defaults to ``None``.
    resume_timeout: :class:`int`
        The maximum amount of seconds a resume can take before closing the node. Defaults to ``60``.
    inactive_player_timeout: :class:`int` | :data:`None`
        The default :attr:`Player.inactive_timeout` for all players connected to this node. Defaults to ``300``.
    inactive_channel_tokens: :class:`int` | :data:`None`
        The default :attr:`Player.inactive_channel_tokens` for all players connected to this node. Defaults to ``3``.
    """

    password: str
    """The password of the node."""
    retries: int | None
    """The amount of retries to attempt when connecting or reconnecting this node."""
    resume_timeout: float
    """The maximum amount of seconds a resume can take before closing the node."""
    _id: str
    _ws: BaseWebsocketManager[Any, Any] | None
    _uri: str
    _pool: NodePool | None

    def __init__(
        self,
        *,
        uri: str,
        password: str,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60,
        inactive_player_timeout: int | None = 300,
        inactive_channel_tokens: int | None = 3,
    ) -> None:
        self._id = id or os.urandom(16).hex()
        self.password = password
        self.retries = retries
        self.resume_timeout = resume_timeout

        self._uri = uri
        self._inactive_player_timeout = inactive_player_timeout
        self._inactive_channel_tokens = inactive_channel_tokens
        self._status: NodeStatus = NodeStatus.disconnected     
        self._players: dict[str, Player] = {}
        
        self._ws = None
        self._pool = None

    @property
    def id(self) -> str:
        """The ID of this node."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if self._pool is not None:
            self._pool._nodes.pop(self._id)
            self._id = value
            self._pool._nodes[value] = self
        else:
            self._id = value

    @property
    def uri(self) -> str:
        """The URI this node connects to. This can only be changed when :attr:`Node.status` is :attr:`NodeStatus.disconnected`"""
        return self._uri

    @uri.setter
    def uri(self, value: str) -> None:
        if self._status is not NodeStatus.disconnected:
            raise RuntimeError("Can not update the node uri while it is connected.")
        self._uri = value

    @property
    def pool(self) -> NodePool | None:
        """The pool this node is attached to."""
        return self._pool

    def get_player(self, id: str) -> Player | None:
        """Gets a player connected to this node."""
        return self._players.get(id)

    async def connect(self) -> None:
        """Connects this node.

        This can only be done when the node has been attached to a pool.
        """
        if self._pool is None:
            raise RuntimeError("Can not connect a node with no pool attached to it.")

        # TODO: implement connect logic
