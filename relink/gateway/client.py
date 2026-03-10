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
from typing import TYPE_CHECKING, Any, ClassVar
from weakref import WeakKeyDictionary

import discord

from relink._version import __version__

from .events.router import EventRouter
from .node import Node

if TYPE_CHECKING:
    from relink.network import SessionType

__all__ = ("Client",)

_ClientRegistry = WeakKeyDictionary[discord.Client, "Client"]


class Client:
    """
    Represents a ReLink client.

    A client helps you manage all Node connections and players.

    Parameters
    ----------
    client: :class:`discord.Client`
        The discord.py's client this ReLink client is attached to.
    """

    __clients__: ClassVar[_ClientRegistry] = WeakKeyDictionary()

    _client: discord.Client
    _nodes: dict[str, Node]
    _session: SessionType | None
    _event_router: EventRouter
    __node_tasks: dict[str, asyncio.Task[Any]]

    def __init__(self, client: discord.Client) -> None:
        self._client = client
        self._nodes = {}
        self._session = None
        self._event_router = EventRouter(self)
        self.__node_tasks = {}

        if client in Client.__clients__:
            raise RuntimeError("ReLink Client already attached to this discord.Client")

        Client.__clients__[client] = self

    def __repr__(self) -> str:
        return f"<ReLink.Client nodes={len(self._nodes)}>"

    @property
    def nodes(self) -> list[Node]:
        """The active nodes attached to this client."""
        return list(self._nodes.values())

    def create_node(
        self,
        *,
        uri: str,
        password: str,
        id: str | None = None,
        retries: int | None = None,
        resume_timeout: float = 60,
        inactive_player_timeout: int | None = 300,
    ) -> Node:
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
        inactive_player_timeout: :class:`int` | :data:`None`
            The default :attr:`Player.inactive_timeout` for all players connected to this node. Defaults to ``300``.

        Returns
        -------
        :class:`Node`
            The node that was created.
        """

        node = Node(
            client=self,
            uri=uri,
            password=password,
            id=id,
            retries=retries,
            resume_timeout=resume_timeout,
            inactive_player_timeout=inactive_player_timeout,
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
        Connects all registered :class:`Node`s to their respective Lavalink servers.

        This method should typically be called after the discord client is logged in,
        often within the ``on_ready`` event.
        """
        if not self._nodes:
            return

        tasks = [node.connect() for node in self.nodes]
        await asyncio.gather(*tasks, return_exceptions=True)

    async def close(self) -> None:
        """
        Gracefully closes all :class:`Node` connections and cleans up internal resources.

        This will stop all active players and close the underlying websocket and HTTP sessions.
        """
        tasks = [node.close() for node in self.nodes if node.is_connected()]
        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

        self._nodes.clear()

    def get_best_node(self) -> Node:
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

        connected_nodes = [node for node in self.nodes if node.is_connected()]
        if not connected_nodes:
            raise RuntimeError("No nodes are currently connected.")

        return min(
            connected_nodes,
            key=lambda node: node.stats.penalty if node.stats else 0.0,
        )

    def _cleanup_node(self, node: Node) -> asyncio.Task[None]:
        if node.id in self.__node_tasks:
            return self.__node_tasks[node.id]

        task = asyncio.create_task(node.close(), name=f"relink:node-close:{node.id}")
        self.__node_tasks[node.id] = task

        task.add_done_callback(lambda _: self.__node_tasks.pop(node.id, None))
        return task

    def _dispatch(self, event: str, *args: Any, **kwargs: Any) -> None:
        self._event_router.dispatch(event, *args, **kwargs)

    def _build_ws_headers(self) -> dict[str, str]:
        if self._client.user is None:
            raise RuntimeError(
                "Cannot connect Nodes without the underlying client running."
            )

        return {
            "User-Id": str(self._client.user.id),
            "Client-Name": f"relink/{__version__}",
        }
