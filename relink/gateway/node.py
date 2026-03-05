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
import logging
import os
from typing import TYPE_CHECKING, Any

import discord

from relink.network import BaseWebsocketManager, HTTPFactory
from relink.network.errors import WebSocketError
from relink.network.message import MessageType
from relink.rest.http import RESTClient

from .enums import NodeStatus
from .errors import InvalidNodePassword, NodeURINotFound
from .events.raw_models import PlayerUpdateEvent, ReadyEvent
from .player import Player
from .schemas.receive import PlayerUpdateEvent as PlayerUpdatePayload
from .schemas.receive import ReadyEvent as ReadyPayload

if TYPE_CHECKING:
    from relink.network import SessionType

    from .client import Client

_log = logging.getLogger(__name__)


class Node:
    """Represents a connectable Node."""

    retries: int | None
    """The amount of retries to attempt when connecting or reconnecting this node."""
    resume_timeout: float
    """The maximum amount of seconds a resume can take before closing the node."""

    _id: str
    _ws: BaseWebsocketManager[Any, Any] | None
    _uri: str
    _password: str
    _client: Client | None
    _keep_alive: asyncio.Task[None] | None
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
        auto_reconnect: bool = True,
        inactive_player_timeout: int | None = 300,
        inactive_channel_tokens: int | None = 3,
        session: SessionType | None = None,
    ) -> None:
        self._client = client
        self._id = id or os.urandom(16).hex()
        self._password = password

        self.retries = retries
        self.resume_timeout = resume_timeout
        self.auto_reconnect = auto_reconnect

        self._status: NodeStatus = NodeStatus.disconnected
        self._resume_session = None
        self._ws = None
        self._keep_alive = None

        self._players: dict[str, Player] = {}
        self._inactive_player_timeout = inactive_player_timeout
        self._inactive_channel_tokens = inactive_channel_tokens

        self._uri = uri.removesuffix("/")
        self._manager: RESTClient = self._init_manager(session)

    def __repr__(self) -> str:
        return f"<Node id={self._id} status={self._status.name} uri={self._uri}>"

    def _init_manager(self, session: SessionType | None) -> RESTClient:
        headers = {"Authorization": self.password}
        if session:
            manager = HTTPFactory.from_http(session)
        else:
            manager_cls = HTTPFactory.http_manager()
            manager = manager_cls()
        return RESTClient(manager, base_url=self._uri, headers=headers)

    def _build_headers(self) -> dict[str, str]:
        assert self._client is not None

        headers = self._client._build_ws_headers()
        if self._resume_session:
            headers["Session-Id"] = self._resume_session

        return headers

    @property
    def password(self) -> str:
        """The password of the node."""
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value
        self._manager.update_headers({"Authorization": value})

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
            raise RuntimeError("Cannot update the node uri while it is connected.")
        self._uri = value

    @property
    def client(self) -> Client | None:
        """The client this node is attached to."""
        return self._client

    def is_connected(self) -> bool:
        """:class:`bool`: Whether the Node is connected and Players can be attached to it."""
        return self._status is NodeStatus.connected

    def get_player(self, id: str, /) -> Player | None:
        """Gets a player connected to this node."""
        return self._players.get(id)

    def get_player_by_guild(self, guild_id: int, /) -> Player | None:
        """Gets a player connected to this Node by its guild ID."""
        return discord.utils.find(
            lambda p: p.guild_id == guild_id, self._players.values()
        )

    async def connect(self) -> None:
        """Connects this node.

        This can only be done when the node has been attached to a pool.
        """
        if self._client is None:
            raise RuntimeError("Cannot connect a node that is bound to a client.")

        await self._manager.setup()
        self._status = NodeStatus.connecting

        if self._keep_alive is not None:
            raise RuntimeError("This node is already connected.")

        await self._attempt_connect()

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

    async def _attempt_connect(self) -> None:
        assert self._client is not None

        headers = self._build_headers()

        retries = 1 if self.retries is None else self.retries
        base_delay = 0.5
        max_delay = 10.0

        for attempt in range(1, retries + 1):
            _log.info(
                "Starting connection attempt %d/%d on Node %r",
                attempt,
                retries,
                self,
            )

            try:
                if await self._connect_ws(headers):
                    return
            except WebSocketError as exc:
                await self._handle_connection_error(exc)

            if attempt >= retries:
                _log.warning(
                    "%r exhausted %d connection attempts. Node will remain disconnected.",
                    self,
                    retries,
                )
                self._status = NodeStatus.disconnected
                await self.cleanup()
                return

            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            _log.debug("Retrying %r in %.2f seconds...", self, delay)
            await asyncio.sleep(delay)

    async def _keep_alive_coro(self) -> None:
        assert self._ws is not None
        assert self._client

        while True:
            msg = await self._ws.receive()

            if MessageType.CLOSE in msg.flags:
                if self.auto_reconnect and self._status not in (
                    NodeStatus.connecting,
                    NodeStatus.disconnected,
                ):
                    _log.info("%r WS closed, attempting reconnect...", self)
                    asyncio.create_task(self.connect())
                break

            if msg.data is None:
                _log.debug("Received a None message from the websocket. Ignoring.")
                continue

            data = msg.json()
            event_type = data.get("op")

            match event_type:
                case "ready":
                    await self._handle_ready(data)
                case "playerUpdate":
                    await self._handle_player_update(data)
                case _:
                    _log.debug(
                        "Received unhandled event type %r from Node %r",
                        event_type,
                        self,
                    )

    async def _handle_ready(self, data: dict[str, Any]) -> None:
        assert self._client is not None

        payload = ReadyPayload(**data)
        self._resume_session = payload.session_id
        self._status = NodeStatus.connected

        event = ReadyEvent(payload)
        self._client._dispatch("node_ready", event)

    async def _handle_player_update(self, data: dict[str, Any]) -> None:
        assert self._client is not None

        payload = PlayerUpdatePayload(**data)
        event = PlayerUpdateEvent(payload)

        self._client._dispatch("player_update", event)

    async def _connect_ws(self, headers: dict[str, str]) -> bool:
        self._ws = await self._manager.connect_ws("/v4/websocket", headers=headers)
        self._keep_alive = asyncio.create_task(self._keep_alive_coro())
        return True

    async def _handle_connection_error(self, exc: WebSocketError) -> None:
        if exc.status in (3000, 3003, 401):
            await self.cleanup()
            raise InvalidNodePassword(self) from exc

        if exc.status in (1014, 404):
            await self.cleanup()
            raise NodeURINotFound(self) from exc

        _log.warning("Unexpected error while connecting %r to Lavalink: %s", self, exc)

    async def cleanup(self) -> None:
        """A function that may be overriden in order to add custom clean-up
        logic to a node.

        This is automatically called by the library.
        """
        ...
