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
import urllib.parse
from collections.abc import Mapping
from typing import TYPE_CHECKING, Any, Literal

import msgspec

from relink.gateway.player_new import PlayerFactory
from relink.models.filters import Filters
from relink.models.info import ServerInfo
from relink.models.player_info import PlayerInfo
from relink.models.responses import SearchResult
from relink.models.settings import (
    AutoPlaySettings,
    CacheSettings,
    HistorySettings,
    InactivitySettings,
)
from relink.models.track import Playable
from relink.network import BaseWebsocketManager, HTTPFactory
from relink.network.errors import WebSocketError
from relink.network.message import MessageType
from relink.rest.enums import TrackSourceType
from relink.rest.errors import HTTPException
from relink.rest.http import RESTClient
from relink.rest.schemas.info import StatsResponse
from relink.rest.schemas.session import UpdateSessionRequest

from .cache import LFUCache
from .enums import NodeStatus, QueueMode
from .errors import InvalidNodePassword, NodeURINotFound
from .event_models import PlayerUpdateEvent, ReadyEvent
from .player_new._base import BasePlayer
from .schemas.receive import PlayerUpdateEvent as PlayerUpdatePayload
from .schemas.receive import ReadyEvent as ReadyPayload

if TYPE_CHECKING:
    from relink.network import SessionType

    from .client import Client

_log = logging.getLogger(__name__)

__all__ = ("Node",)


class Node:
    """
    Represents a connectable Node.

    Parameters
    ----------
    client: :class:`relink.Client`
        The ReLink client this node is attached to.
    uri: :class:`str`
        The base URI for the Lavalink node. Do not include REST or websocket routes.
    password: :class:`str`
        The Lavalink server password used for both HTTP and websocket authentication.
    id: :class:`str` | :data:`None`
        The identifier used to track this node inside the client. If ``None`` is passed,
        a random identifier is generated.
    retries: :class:`int` | :data:`None`
        How many reconnect attempts should be made before the node gives up. If ``None``
        is passed, reconnect attempts are unlimited.
    resume_timeout: :class:`float`
        The number of seconds Lavalink should keep a resumable session alive.
    auto_reconnect: :class:`bool`
        Whether the node should attempt to reconnect automatically after an unexpected
        disconnect.
    cache_settings: :class:`relink.models.CacheSettings` | :data:`None`
        Settings used for the node's search-result cache. If ``None`` is passed, default
        cache settings are used.
    inactivity_settings: :class:`relink.models.InactivitySettings`
        Default inactivity behavior applied to players managed by this node.
    session: ``aiohttp.ClientSession`` | ``curl_cffi.AsyncSession`` | :data:`None`
        Optional pre-existing HTTP session to reuse for this node's REST and websocket
        transport. If ``None`` is passed, the library creates one.
    """

    retries: int | None
    """The amount of retries to attempt when connecting or reconnecting this node."""
    resume_timeout: float
    """The maximum amount of seconds a resume can take before closing the node."""

    _id: str
    _ws: BaseWebsocketManager[Any, Any] | None
    _uri: str
    _password: str
    _client: Client[Any] | None
    _keep_alive: asyncio.Task[None] | None
    _resume_session: str | None
    _stats: StatsResponse | None

    def __init__(
        self,
        *,
        client: Client[Any],
        uri: str,
        password: str,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60,
        auto_reconnect: bool = True,
        cache_settings: CacheSettings | None = None,
        inactivity_settings: InactivitySettings,
        session: SessionType | None = None,
    ) -> None:
        self._client = client
        self._id = id or os.urandom(16).hex()
        self._password = password

        self.retries = retries
        self.resume_timeout = resume_timeout
        self.auto_reconnect = auto_reconnect

        self._status: NodeStatus = NodeStatus.DISCONNECTED
        self._resume_session = None
        self._has_resume_session = asyncio.Event()
        self._ws = None
        self._keep_alive = None
        self._stats = None

        self._players: dict[int, BasePlayer] = {}
        self._player_factory = PlayerFactory()
        self._inactivity_settings = inactivity_settings
        self._waiting_to_disconnect: dict[int, asyncio.Task[None]] = {}
        self._cache: LFUCache[str, Any] = LFUCache(settings=cache_settings)

        self._uri = uri.removesuffix("/")
        self._manager: RESTClient = self._init_manager(session)

    def __repr__(self) -> str:
        return f"<Node id={self._id} status={self._status.name} players={len(self._players)} uri={self._uri}>"

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

    def _ensure_client(self) -> Client[Any]:
        if not self._client:
            raise RuntimeError(
                "Cannot perform HTTP requests without an attached client."
            )
        return self._client

    async def _wait_session(self) -> bool:
        try:
            return await asyncio.wait_for(self._has_resume_session.wait(), timeout=10.0)
        except asyncio.TimeoutError:
            raise RuntimeError("Timed out waiting for node READY payload.")

    @property
    def client(self) -> Client[Any] | None:
        """The client this node is attached to."""
        return self._client

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
    def is_connected(self) -> bool:
        """Whether the Node is connected and Players can be attached to it."""
        return self._status is NodeStatus.CONNECTED

    @property
    def inactivity_settings(self) -> InactivitySettings:
        """The inactivity configuration for all players on this node."""
        return self._inactivity_settings

    @property
    def password(self) -> str:
        """The password of the node."""
        return self._password

    @password.setter
    def password(self, value: str) -> None:
        self._password = value
        self._manager.update_headers({"Authorization": value})

    @property
    def stats(self) -> StatsResponse | None:
        """The latest stats received from the Lavalink node."""
        return self._stats

    @property
    def session_id(self) -> str:
        if not self._resume_session:
            raise RuntimeError(f"Node {self._id!r} is not connected (no session ID).")
        return self._resume_session

    @property
    def uri(self) -> str:
        """The URI this node connects to. This can only be changed while the node is disconnected."""
        return self._uri

    @uri.setter
    def uri(self, value: str) -> None:
        if self._status is not NodeStatus.DISCONNECTED:
            raise RuntimeError("Cannot update the node uri while it is connected.")
        self._uri = value

    async def connect(self) -> None:
        """
        Connects this node.

        This can only be done when the node has been attached to a pool.
        """
        if self._client is None:
            raise RuntimeError("Cannot connect a node that is bound to a client.")

        await self._manager.setup()
        self._status = NodeStatus.CONNECTING

        if self._keep_alive is not None:
            raise RuntimeError("This node is already connected.")

        await self._attempt_connect()

    async def close(self) -> None:
        """
        Closes the connection to this node.

        All Players connected to it will stop playing.

        This also closes all HTTP and WS sessions and connections.

        This dispatches a ``on_node_close`` event.
        """

        if self._client is None:
            raise RuntimeError("Can not close a Node that is not bound to a client.")

        if not self.is_connected:
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
        self._status = NodeStatus.DISCONNECTED

        self._client._dispatch("node_close", self)
        await self.cleanup()

    async def search_track(
        self,
        query: str,
        *,
        source: TrackSourceType | str | None = None,
    ) -> SearchResult:
        """
        Searches for ``query`` in this Node.

        Parameters
        ----------
        query: :class:`str`
            The query to search. This can be a full URL, or headed by hosts specified by any plugin.
        source: :class:`TrackSourceType` | :class:`str` | :data:`None`
            The source to search from. This is, essentially, providing a host to ``query``. The library
            provides default source types under :class:`TrackSourceType`, but custom ones can be passed
            with a raw string.

        Returns
        -------
        :class:`SearchResult`
            The search result.
        """
        client = self._ensure_client()

        is_url = query.startswith(("http://", "https://"))
        formatted = (
            query if is_url or source is None else f"{source.removesuffix(':')}:{query}"
        )

        encoded = urllib.parse.quote(formatted)
        cached_result = self._cache.get(encoded)

        if isinstance(cached_result, SearchResult):
            return cached_result

        data = await self._manager.load_track(formatted)
        result = SearchResult(client=client, data=data)
        self._cache.put(encoded, result)
        return result

    async def decode_track(self, encoded: str) -> Playable:
        """
        Decodes a track from its encoded data.

        When a track is fetched, the encoded data can be found under
        :attr:`relink.rest.schemas.Track.encoded`.

        Parameters
        ----------
        encoded: :class:`str`
            The encoded data to resolve the track from.

        Returns
        -------
        :class:`relink.models.Playable`
            The decoded resolved track.
        """

        client = self._ensure_client()
        data = await self._manager.decode_track(encoded)
        return Playable(client=client, data=data)

    async def decode_tracks(self, *encoded: str) -> list[Playable]:
        """
        Bulk decodes encoded tracks.

        Parameters
        ----------
        *encoded: :class:`str`
            The encoded data for each track to be decoded.

        Returns
        -------
        ``list[Playable]``
            The decoded resolved tracks.
        """

        client = self._ensure_client()
        data = await self._manager.decode_tracks(list(encoded))
        return [Playable(client=client, data=d) for d in data]

    async def fetch_info(self) -> ServerInfo:
        """
        Fetches the Lavalink server info this node is connected to.

        Returns
        -------
        :class:`relink.models.ServerInfo`
            The server info.
        """

        client = self._ensure_client()
        data = await self._manager.lavalink_info()
        return ServerInfo(client=client, data=data)

    async def fetch_players(self) -> list[PlayerInfo]:
        """
        Fetches all the player that are connected to this node.

        This performs a fresh REST request for the current player states on the node.

        Returns
        -------
        ``list[PlayerInfo]``
            The players connected to this node.
        """

        client = self._ensure_client()
        data = await self._manager.get_players(self.session_id)
        return [PlayerInfo(client=client, data=d) for d in data]

    async def fetch_player(self, guild_id: int) -> PlayerInfo:
        """
        Fetches a player from this node connected to the provided guild ID.

        Usually, you should use :attr:`Node.get_player` instead of this method.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild ID the player is connected to.

        Returns
        -------
        :class:`PlayerInfo`
            The player connected to the guild ID.
        """

        client = self._ensure_client()
        data = await self._manager.get_player(
            session_id=self.session_id,
            guild_id=str(guild_id),
        )
        return PlayerInfo(client=client, data=data)

    async def disconnect_player(self, guild_id: int) -> None:
        """
        Force disconnects a player from this node connected to the provided guild ID.

        Parameters
        ----------
        guild_id: :class:`int`
            The guild ID to disconnect the player from.
        """
        _ = self._ensure_client()
        await self._manager.destroy_player(
            session_id=self.session_id,
            guild_id=str(guild_id),
        )

    def get_player(self, guild_id: int, /) -> BasePlayer | None:
        """Gets a player connected to this node."""
        return self._players.get(guild_id)

    def _add_player(self, player: BasePlayer) -> None:
        """Internal helper to register a player to this node."""
        self._players[player.guild.id] = player

    def _remove_player(self, guild_id: int) -> None:
        """Internal helper to unregister a player from this node."""
        self._players.pop(guild_id, None)

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
                    _log.info(
                        "Successfully connected node %r (attempt %d/%d)",
                        self,
                        attempt,
                        retries,
                    )
                    break
            except WebSocketError as exc:
                await self._handle_connection_error(exc)

            if (attempt - 1) >= retries:
                _log.warning(
                    "%r exhausted %d connection attempts. Node will remain disconnected.",
                    self,
                    retries,
                )
                self._status = NodeStatus.DISCONNECTED
                await self.cleanup()
                return

            delay = min(base_delay * (2 ** (attempt - 1)), max_delay)
            _log.debug("Retrying %r in %.2f seconds...", self, delay)
            await asyncio.sleep(delay)

        self._status = NodeStatus.CONNECTED

    async def _connect_ws(self, headers: dict[str, str]) -> bool:
        self._ws = await self._manager.connect_ws("/v4/websocket", headers=headers)
        self._keep_alive = asyncio.create_task(self._keep_alive_coro())
        return True

    async def _keep_alive_coro(self) -> None:
        assert self._ws is not None
        assert self._client

        while True:
            msg = await self._ws.receive()

            if MessageType.CLOSE in msg.flags:
                self._client._dispatch("node_close", self)

                if self.auto_reconnect and self._status not in (
                    NodeStatus.CONNECTING,
                    NodeStatus.DISCONNECTED,
                ):
                    _log.info("%r WS closed, attempting reconnect...", self)
                    asyncio.create_task(self.connect())
                break

            if msg.data is None:
                _log.debug("Received a None message from the websocket. Ignoring.")
                continue

            raw = msg.data
            if isinstance(raw, str):
                raw = raw.encode("utf-8")
            data = msgspec.json.decode(raw)

            event_type = data.pop("op", None)
            _log.debug("Received event OP=%s ; D=%r", event_type, data)

            try:
                match event_type:
                    case "ready":
                        await self._handle_ready(data)
                    case "playerUpdate":
                        await self._handle_player_update(data)
                    case "stats":
                        self._handle_stats(data)
                    case "event":
                        await self._handle_event(data)
                    case _:
                        _log.debug(
                            "Received unhandled event type %r from Node %r",
                            event_type,
                            self,
                        )
            except Exception as exc:
                _log.error(
                    "Node %r: Unhandled exception while processing OP=%s: %s",
                    self._id,
                    event_type,
                    exc,
                    exc_info=True,
                )

    async def _handle_ready(self, data: dict[str, Any]) -> None:
        assert self._client is not None

        payload = msgspec.convert(data, ReadyPayload)
        self._resume_session = payload.session_id
        self._status = NodeStatus.CONNECTED

        try:
            update_data = UpdateSessionRequest(
                resuming=True, timeout=int(self.resume_timeout)
            )

            await self._manager.update_session(
                session_id=self._resume_session, data=update_data
            )
            _log.info(
                "Node %r: Session resumption configured (timeout: %ds).",
                self._id,
                self.resume_timeout,
            )
        except Exception as exc:
            _log.error(
                "Node %r: Failed to configure session resumption: %s",
                self._id,
                exc,
            )

        event = ReadyEvent(payload, self)
        self._client._dispatch("node_ready", event)
        self._has_resume_session.set()

    async def _handle_player_update(self, data: dict[str, Any]) -> None:
        assert self._client is not None

        payload = msgspec.convert(data, PlayerUpdatePayload)

        guild_id = int(payload.guild_id)
        player = self.get_player(guild_id)

        if player:
            player._update_state(payload.state)

        event = PlayerUpdateEvent(payload, self)
        self._client._dispatch("player_update", event)

    def _handle_stats(self, data: dict[str, Any]) -> None:
        self._stats = msgspec.convert(data, StatsResponse)

    async def _handle_event(self, data: dict[str, Any]) -> None:
        assert self._client is not None

        guild_id = int(data.get("guildId", 0))
        player = self.get_player(guild_id)

        if player is None:
            _log.debug(
                "Received event %r for unknown player in guild %s",
                data.get("type"),
                guild_id,
            )
            return

        await player._dispatch_event(data)

    async def _handle_connection_error(self, exc: WebSocketError) -> None:
        if exc.status in (3000, 3003, 401):
            await self.cleanup()
            raise InvalidNodePassword(self) from exc

        if exc.status in (1014, 404):
            await self.cleanup()
            raise NodeURINotFound(self) from exc

        _log.warning("Unexpected error while connecting %r to Lavalink: %s", self, exc)

    async def send(
        self,
        method: Literal["GET", "POST", "PATCH", "PUT", "DELETE", "OPTIONS"],
        path: str,
        *,
        headers: Mapping[str, str] | None = None,
        params: Mapping[str, str] | None = None,
        json: dict[str, Any] | None = None,
        data: Any | None = None,
    ) -> dict[str, Any] | list[Any] | str | bytes | None:
        """Method for doing manual requests to the Lavalink node.

        .. versionadded:: 1.1.0

        .. warning::

            Usually you wouldn't use this method. Please use the built in methods of :class:`~relink.Client`,
            :class:`~relink.Node` and :class:`~relink.Player`, unless you need to send specific plugin data
            to Lavalink.

            Using this method may have unwanted side effects on your players and/or nodes.

        Parameters
        ----------
        method: :class:`str` | :data:`None`
            The method to use when making this request. Available methods are "GET", "POST", "PATCH",
            "PUT", "DELETE" and "OPTIONS". Defaults to "GET".
        path: str
            The path to make this request to. E.g. "stats", which will translate to "/v4/stats".
            Do not include the base URI of the node here or the "/v4" prefix.
        headers: :class:`~collections.abc.Mapping` | :data:`None`
            An optional dict of headers to send with this request. This is merged with the default
            headers used for the node, so you don't have to include authentication headers here. E.g. ``{"X-Thing": "Value"}``.
        params: :class:`~collections.abc.Mapping` | :data:`None`
            An optional dict of query parameters to send with your request. If you include your query
            parameters in the ``path`` parameter, do not pass them here as well. E.g. ``{"thing": 1, "other": 2}``
            would equate to "?thing=1&other=2".
        json: :class:`dict` | :data:`None`
            The optional JSON data to send along with your request.
        data: :class:`~typing.Any` | :data:`None`
            The optional data to send along with your request.

        Returns
        -------
        :class:`dict` | :class:`list` | :class:`str` | :class:`bytes` | :data:`None`
            The response body returned by Lavalink, if any. This can be a dict (if the response is a JSON object),
            a list (if the response is a JSON array), a string (if the response is text) or bytes (if the response is binary).
            If the response has no body or the request is out of lavalink's control, ``None`` is returned.

        Raises
        ------
        :exc:`msgspec.DecodeError`
            The response body could not be decoded.
        :exc:`relink.HTTPException`
            An error occurred while making the request.
        """
        try:
            response = await self._manager.request(
                method=method,
                url=path,
                data=data,
                params=params,
                json=json,
                headers=headers,
            )
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001 # no choice here
            _log.warning("Unexpected error while sending request to %r: %s", self, exc)
            return None

        try:
            data = msgspec.json.decode(response)
        except msgspec.DecodeError:
            pass
        else:
            return data

        try:
            return response.decode("utf-8")
        except UnicodeDecodeError:
            return response

    async def cleanup(self) -> None:
        """A function that may be overriden in order to add custom clean-up
        logic to a node.

        This is automatically called by the library.
        """
        ...

    async def create_player(
        self,
        *,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
    ) -> BasePlayer:
        """
        Creates a player with extra configuration bound to this node.

        Parameters
        ----------
        volume: :class:`int` | :data:`None`
            The volume of the player, in percentage from 0 to 1000. Defaults to ``None``.
        paused: :class:`bool` | :data:`None`
            Whether the player should start paused. Defaults to ``None``.
        filters: :class:`PlayerFilters` | :data:`None`
            The filters to apply to the player. Defaults to ``None``.
        queue_mode: :class:`QueueMode`
            The playback strategy for the queue. Defaults to :attr:`QueueMode.NORMAL`.
        autoplay_settings: :class:`AutoPlaySettings` | :data:`None`
            The autoplay settings to set to this player. Defaults to ``None``.
        history_settings: :class:`HistorySettings` | :data:`None`
            The history settings to set to this player. Defaults to ``None``.

        Returns
        -------
        :class:`Player`
            The player. This can be passed to the ``cls=`` kwarg on :meth:`~discord.abc.Connectable.connect`
        """
        client = self._ensure_client()

        assert client.framework in ("discord.py", "disnake", "pycord")
        player_cls = await self._player_factory.get_player(client.framework)

        player = player_cls(
            node=self,
            volume=volume or 100,
            paused=paused or False,
            filters=filters,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
        )

        return player
