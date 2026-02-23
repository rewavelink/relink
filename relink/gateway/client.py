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
from typing import TYPE_CHECKING, ClassVar

import discord

from .node import Node

from relink.rest.http import HTTPClient

if TYPE_CHECKING:
    from relink.network import SessionType


class Client:
    """Represents a ReLink client.

    A client helps you manage all Node connections and players.

    Parameters
    ----------
    client: :class:`discord.Client`
        The discord.py's client this ReLink client is attached to.
    """

    __clients__: ClassVar[dict[discord.Client, Client]] = {}

    _client: discord.Client
    _nodes: dict[str, Node]
    _session: SessionType | None
    _http: HTTPClient

    def __init__(
        self,
        client: discord.Client,
        *,
        session: SessionType | None = None,
    ) -> None:
        self._client = client
        self._nodes = {}
        self._session = None
        self._http = HTTPClient(session=session)

        Client.__clients__[client] = self

    @property
    def nodes(self) -> list[Node]:
        """The nodes attached to this client."""
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
        inactive_channel_tokens: int | None = 3,
    ) -> Node:
        """Creates a :class:`Node` attached to this client.
        
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
        inactive_channel_tokens: :class:`int` | :data:`None`
            The default :attr:`Player.inactive_channel_tokens` for all players connected to this node. Defaults to ``3``.

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
            inactive_channel_tokens=inactive_channel_tokens,
        )
        self._nodes[node.id] = node
        return node

    def remove_node(self, id: str, /) -> None:
        """Removes a Node from this client.

        Parameters
        ----------
        id: :class:`str`
            The ID of the node to remove.
        """

        try:
            self._nodes.pop(id)
        except KeyError:
            pass