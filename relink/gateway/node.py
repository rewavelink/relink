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

import asyncio
import enum
import logging
import os
from typing import TYPE_CHECKING, Any

import discord
import msgspec.json

from relink.network import BaseWebsocketManager, HTTPFactory
from relink.network.errors import WebSocketError
from relink.rest.http import RESTClient

from .player import Player
from .errors import InvalidNodePassword, NodeURINotFound
from .events.raw_models import PlayerUpdateEvent, ReadyEvent
from .schemas.receive import ReadyEvent as ReadyPayload, PlayerUpdateEvent as PlayerUpdatePayload

if TYPE_CHECKING:
    from .client import Client

    from relink.network import SessionType

_log = logging.getLogger(__name__)


class NodeStatus(enum.Enum):
    """Represents the connection status of a node."""

    disconnected = 1
    connected = 2
    connecting = 3


class Node:
    """Represents a connectable Node.
    """

    retries: int | None
    """The amount of retries to attempt when connecting or reconnecting this node."""
    resume_timeout: float
    """The maximum amount of seconds a resume can take before closing the node."""
    _id: str
    _ws: BaseWebsocketManager[Any, Any] | None
    _uri: str
    _password: str
    _client: Client | None
    _keep_alive: asyncio.Task[Any] | None
    _resume_session: str | None

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
        session: SessionType | None = None,
    ) -> None:
        self._client = client
        self._id = id or os.urandom(16).hex()
        self._password = password
        self.retries = retries
        self.resume_timeout = resume_timeout

        self._uri = uri.removesuffix("/")
        self._inactive_player_timeout = inactive_player_timeout
        self._inactive_channel_tokens = inactive_channel_tokens
        self._status: NodeStatus = NodeStatus.disconnected     
        self._players: dict[str, Player] = {}

        headers = {
            "Authorization": self.password,
        }

        if session:
            manager = HTTPFactory.from_http(session)
        else:
            manager_cls = HTTPFactory.http_manager()
            manager = manager_cls()

        self._manager = RESTClient(manager, base_url=self._uri, headers=headers)
        self._ws = None
        self._keep_alive = None
        self._resume_session = None

    @property
    def password(self) -> str:
        """The password of the node."""
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value
        self._manager._default_headers["Authorization"] = value

    @property
    def id(self) -> str:
        """The ID of this node."""
        return self._id

    @id.setter
    def id(self, value: str) -> None:
        if self._client is not None:
            raise RuntimeError("Node IDs can not be changed when bound to a client.")
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
    def client(self) -> Client | None:
        """The client this node is attached to."""
        return self._client

    def get_player(self, id: str, /) -> Player | None:
        """Gets a player connected to this node."""
        return self._players.get(id)

    def get_player_by_guild(self, guild_id: int, /) -> Player | None:
        """Gets a player connected to this Node by its guild ID."""
        return discord.utils.find(lambda p: p.guild_id == guild_id, self._players.values())

    def is_connected(self) -> bool:
        """:class:`bool`: Whether the Node is connected and Players can be attached to it."""
        return self._status is NodeStatus.connected

    async def connect(self) -> None:
        """Connects this node.

        This can only be done when the node has been attached to a pool.
        """
        if self._client is None:
            raise RuntimeError("Can not connect a node that is not bound to a client.")

        await self._manager.setup()

        self._status = NodeStatus.connecting

        headers = self._client._get_ws_headers()
        if self._resume_session:
            headers["Session-Id"] = self._resume_session

        if self._keep_alive is not None:
            raise RuntimeError("This node is already connected.")

        retries: int = self.retries or 1

        for i in range(retries):
            _log.info("Starting connection attempt %d/%d on Node %r", i + 1, retries, self)

            try:
                self._ws = await self._manager.connect_ws(
                    "/v4/websocket",
                    headers=headers,
                )
            except WebSocketError as exc:
                if exc.status in (3000, 3003, 401):  # Forbidden / Unauthorized
                    await self.cleanup()
                    raise InvalidNodePassword(self) from exc
                elif exc.status in (1014, 404):
                    await self.cleanup()
                    raise NodeURINotFound(self) from exc
                else:
                    _log.warning(
                        "An unexpected error ocurred while connecting %r to Lavalink: %s",
                        self,
                        exc,
                    )

            if self.is_connected():
                self._keep_alive = asyncio.create_task(self._keep_alive_coro())
                break

            if i == (retries - 1):
                _log.warning(
                    "%r has exhausted %d connection attempts, and failed. This Node will not be connected.",
                    self,
                    retries,
                )
                await self.cleanup()
                break

            # TODO: implement some kind of backoff to not spam ws connection attemps?
            await asyncio.sleep(0.5)

    async def _keep_alive_coro(self) -> None:
        assert self._ws is not None
        assert self._client

        while True:
            msg = await self._ws.receive()
            msg_type = msg.flags.__class__

            if msg_type.CLOSE in msg.flags:
                # attempt a reconnect
                # TODO: maybe add a reconnect= flag?
                asyncio.create_task(self.connect())
                break

            if msg.data is None:
                _log.debug("Received a None message from the websocket. Ignoring.")
                continue

            data = msg.json()

            if data["op"] == "ready":
                pd = msgspec.json.decode(data, type=ReadyPayload)

                self._resume_session = pd.session_id
                self._status = NodeStatus.connected

                ready = ReadyEvent(pd)
                self._client._dispatch("node_ready", ready)
            elif data["op"] == "playerUpdate":
                pd = msgspec.json.decode(data, type=PlayerUpdatePayload)
                pupdate = PlayerUpdateEvent(pd)
                self._client._dispatch("player_update", pupdate)

                resolved = self.get_player_by_guild(pd.guild_id)

    async def close(self) -> None:
        """Closes the connection to this node.

        All Players connected to it will stop playing.

        This also closes all HTTP and WS sessions and connections.

        This dispatches a ``on_node_close`` event.
        """

        if self._client is None:
            raise RuntimeError("Can not close a Node that is not bound to a client.")

        if not self.is_connected():
            raise RuntimeError("This Node is not connected.")

        if self._keep_alive and not self._keep_alive.cancelled():
            self._keep_alive.cancel()
        if self._ws and self._ws.is_connected:
            await self._ws.close()
        if not self._manager.is_closed:
            await self._manager.close()

        self._ws = None
        self._keep_alive = None
        self._resume_session = None
        self._status = NodeStatus.disconnected

        self._client._dispatch("node_close", self)
        await self.cleanup()

    async def cleanup(self) -> None:
        """A function that may be overriden in order to add custom clean-up
        logic to a node.

        This is automatically called by the library.
        """
