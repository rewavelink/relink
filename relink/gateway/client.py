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

from relink import _registry
from relink._version import __version__
from relink.gateway.player_new import FrameworkLiteral, PlayerFactory
from relink.models.settings import CacheSettings, InactivitySettings
from relink.rest.enums import TrackSourceType

from .node import Node

if TYPE_CHECKING:
    from relink.models.responses import SearchResult
    from relink.models.track import Playable
    from relink.network import SessionType


__all__ = ("Client",)

_log = logging.getLogger(__name__)


class Client[N: Node]:
    """
    Represents a ReLink client.

    A client helps you manage all Node connections and players.

    Parameters
    ----------
    client: :class:`discord.Client`
        The discord.py's client this ReLink client is attached to.
    node_cls: ``type[Node]``
        The class to use when creating new nodes. Defaults to :class:`Node`.
    """

    _client: discord.Client
    _framework: FrameworkLiteral
    _nodes: dict[str, N]
    _session: SessionType | None
    __node_tasks: dict[str, asyncio.Task[Any]]

    def __init__(
        self,
        client: discord.Client,
        *,
        node_cls: type[N] = Node,
        framework: FrameworkLiteral | None = None,
    ) -> None:
        self._client = client

        if framework is None:
            framework = PlayerFactory().detect_framework() or "discord.py"

        self._framework = framework
        self._nodes = {}
        self._session = None
        self.__node_tasks = {}
        self._node_cls: type[N] = node_cls

        if client in _registry.clients:
            raise RuntimeError(
                f"relink.Client already attached to this {framework}.Client"
            )

        os.environ["RELINK_FRAMEWORK"] = framework
        _registry.clients[client] = self

    def __repr__(self) -> str:
        return f"<relink.Client nodes={len(self._nodes)}>"

    @property
    def nodes(self) -> list[N]:
        """The active nodes attached to this client."""
        return list(self._nodes.values())

    @property
    def framework(self) -> FrameworkLiteral:
        """
        The Discord framework used by this client
        (``"discord.py"``, ``"disnake"``, or ``"pycord"``).
        """
        return self._framework

    def create_node(
        self,
        *,
        uri: str,
        password: str,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60,
        cache_settings: CacheSettings | None = None,
        inactivity_settings: InactivitySettings | None = None,
        session: SessionType | None = None,
    ) -> N:
        """
        Creates a :class:`Node` attached to this client.

        Parameters
        ----------
        uri: :class:`str`
            The URI the node will connect to. You should only provide the base URI without
            any routes, as the library will do it for you.
        password: :class:`str`
            The password of the node.
        id: :class:`str` | :data:`None`
            The ID of this node. This is used internally to identify this node. If ``None`` is passed, it is
            generated automatically.
        retries: :class:`int` | :data:`None`
            The amount of retries to attempt when connecting or reconnecting this node. Whenever the limit
            is reached, it closes the node automatically. If this is set to ``None``, it retries indefinetely.
            Defaults to ``None``.
        resume_timeout: :class:`int`
            The maximum amount of seconds a resume can take before closing the node. Defaults to ``60``.
        cache_settings: :class:`CacheSettings` | :data:`None`
            The search result caching configuration.
            Defaults to ``CacheSettings.default()``.
        inactivity_settings: :class:`InactivitySettings` | :data:`None`
            The inactivity configuration for all players connected to this node.
            If ``None`` is passed, it uses ``InactivitySettings.default()``.
        session: ``aiohttp.ClientSession`` | ``curl_cffi.AsyncSession`` | :data:`None`
            The session this node should use. If ``None`` is provided, creates one. Defaults to ``None``.

        Returns
        -------
        :class:`Node`
            The node that was created.
        """

        i_settings = inactivity_settings or InactivitySettings.default()
        c_settings = cache_settings or CacheSettings.default()

        node = self._node_cls(
            client=self,
            uri=uri,
            password=password,
            id=id,
            retries=retries,
            resume_timeout=resume_timeout,
            cache_settings=c_settings,
            inactivity_settings=i_settings,
            session=session,
        )
        self._nodes[node.id] = node
        return node

    def remove_node(self, identifier: str, /) -> None:
        """
        Removes a Node from this client.

        Parameters
        ----------
        identifier: :class:`str`
            The ID of the node to remove.
        """

        try:
            node = self._nodes.pop(identifier)
        except KeyError:
            pass
        else:
            self._cleanup_node(node)

    def clear_nodes(self) -> None:
        """Clears all Nodes from this Client."""

        for node in self.nodes:
            self.remove_node(node.id)

    async def start(self) -> None:
        """
        Connects all registered nodes to their respective Lavalink servers.

        This method should typically be called after the discord client is logged in,
        often within the ``on_ready`` event.
        """
        if not self._nodes:
            return

        for node in self.nodes:
            if node.is_connected:
                continue

            try:
                await node.connect()
            except Exception as exc:
                _log.exception(
                    "Ignoring exception while connecting Node %r", node, exc_info=exc
                )
                continue

    async def close(self) -> None:
        """
        Gracefully closes all :class:`Node` connections and cleans up internal resources.

        This will stop all active players and close the underlying websocket and HTTP sessions.
        """

        for node in self.nodes:
            if not node.is_connected:
                continue

            try:
                await node.close()
            except Exception as exc:
                _log.exception(
                    "Ignoring exception while closing Node %r", node, exc_info=exc
                )
                continue

        self._nodes.clear()

    def get_best_node(self) -> N:
        """
        Returns the best available :class:`Node` based on current load and connectivity.

        Returns
        -------
        :class:`Node`
            The node with the lowest penalty that is currently connected.

        Raises
        ------
        RuntimeError
            No nodes are currently connected to handle the request.
        """

        connected_nodes = [node for node in self.nodes if node.is_connected]
        if not connected_nodes:
            raise RuntimeError("No nodes are currently connected.")

        return min(
            connected_nodes,
            key=lambda node: node.stats.penalty if node.stats else 0.0,
        )

    async def search_track(
        self,
        query: str,
        *,
        source: TrackSourceType | str = TrackSourceType.YOUTUBE,
    ) -> SearchResult:
        """
        Searches for ``query`` in the best Node available, obtained with :meth:`Client.get_best_node`.

        Parameters
        ----------
        query: :class:`str`
            The query to search. This can be a full URL, or headed by hosts specified by any plugin.
        source: :class:`TrackSourceType` | :class:`str`
            The source to search from. This is, essentially, providing a host to ``query``. The library
            provides default source types under :class:`TrackSourceType`, but custom ones can be passed
            with a raw string.

        Returns
        -------
        :class:`SearchResult`
            The search result.
        """
        node = self.get_best_node()
        return await node.search_track(query, source=source)

    async def decode_track(self, encoded: str) -> Playable:
        """
        Decodes a track from its encoded data using the best Node available, obtained with
        :meth:`Client.get_best_node`.

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
        node = self.get_best_node()
        return await node.decode_track(encoded)

    async def decode_tracks(self, *encoded: str) -> list[Playable]:
        """
        Bulk decode encoded tracks using the best Node available, obtained with :meth:`Client.get_best_node`.

        Parameters
        ----------
        *encoded: :class:`str`
            The encoded data for each track to be decoded.

        Returns
        -------
        ``list[Playable]``
            The decoded resolved tracks.
        """
        node = self.get_best_node()
        return await node.decode_tracks(*encoded)

    def _cleanup_node(self, node: Node) -> asyncio.Task[None]:
        if node.id in self.__node_tasks:
            return self.__node_tasks[node.id]

        task = asyncio.create_task(node.close(), name=f"relink:node-close:{node.id}")
        self.__node_tasks[node.id] = task

        task.add_done_callback(lambda _: self.__node_tasks.pop(node.id, None))
        return task

    def _dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        self._client.dispatch(f"relink_{event}", *args, **kwargs)

    def _build_ws_headers(self) -> dict[str, str]:
        if self._client.user is None:
            raise RuntimeError(
                "Cannot connect Nodes without the underlying client running."
            )

        return {
            "User-Id": str(self._client.user.id),
            "Client-Name": f"relink/{__version__}",
        }
