"""
MIT License

Copyright (c) 2019-2026 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

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

from typing import TYPE_CHECKING, Self, Sequence

import discord

if TYPE_CHECKING:
    from .node import Node

__all__ = (
    "NodePool",
)


class NodePool:
    """A pool of nodes for managing connections to Lavalink servers.

    Parameters
    ----------
    client: :class:`discord.Client`
        The client to use for managing connections to Lavalink servers.
    nodes: Sequence[:class:`Node`] | :data:`None`
        The nodes to add to this pool. Defaults to ``None``.
    """

    client: discord.Client
    _nodes: dict[str, Node]

    def __init__(self, *, client: discord.Client, nodes: Sequence[Node] | None = None) -> None:
        self.client = client
        self._nodes = {}

        if nodes:
            for node in nodes:
                self.add_node(node)

    @property
    def nodes(self) -> list[Node]:
        """Returns a list of all the nodes in this pool."""
        return list(self._nodes.values())

    def get_node(self, id: str, /) -> Node | None:
        """Returns a node with :attr:`Node.id` set as ``id``, or ``None`` if not found."""
        return self._nodes.get(id)

    def add_node(self, node: Node) -> Self:
        """Adds a node to this pool."""
        node._pool = self
        self._nodes[node.id] = node
        return self
        
    def remove_node(self, id: str, /) -> Self:
        """Removes a node from this pool."""
        try:
            node = self._nodes.pop(id)
        except KeyError:
            pass
        else:
            node._pool = None
        return self
