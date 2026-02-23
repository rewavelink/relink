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

from relink.network import BaseWebsocketManager, HTTPFactory

from .player import Player

if TYPE_CHECKING:
    from .client import Client

    from relink.network import SessionType


class NodeStatus(enum.Enum):
    """Represents the connection status of a node."""

    disconnected = 1
    connected = 2


class Node:
    """Represents a connectable Node.
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
    _client: Client | None

    def __init__(
        self,
        *,
        client: Client,
        uri: str,
        password: str,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60,
        inactive_player_timeout: int | None = 300,
        inactive_channel_tokens: int | None = 3,
    ) -> None:
        self._client = client
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

    @property
    def id(self) -> str:
        """The ID of this node."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if self._client:
            self._client._replace_node_id(self, value)
        else:
            self._id = value or os.urandom(16).hex()

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
    def client(self) -> Client | None:
        """The client this node is attached to."""
        return self._client

    def get_player(self, id: str) -> Player | None:
        """Gets a player connected to this node."""
        return self._players.get(id)

    async def connect(self, *, session: SessionType | None) -> None:
        """Connects this node.

        This can only be done when the node has been attached to a pool.
        """
        if self._client is None:
            raise RuntimeError("Can not connect a node with no pool attached to it.")

        # TODO: implement connect logic

        if session is not None:
            http = HTTPFactory.from_http(session)
            assert http._session
            ws = HTTPFactory.create_websocket(http._session)
        else:
            ws = HTTPFactory.create_websocket(self._client.http._session)

        self._ws = ws

        url = self._client.http._base_url
