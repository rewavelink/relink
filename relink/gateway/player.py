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

import abc
from typing import TYPE_CHECKING, Self, overload

import discord

if TYPE_CHECKING:
    from .node import Node

MISSING = discord.utils.MISSING


class PlayerConnectionState(abc.ABC):
    """A :class:`Player` voice connection state.

    This offers a default implementation, but you can subclass it to implement
    custom behaviour.
    """


class Player(discord.VoiceProtocol):
    """Represents a player that is used to play music in a voice channel.

    There are two ways to create a player:

    1. Via creating an instance and then passing it to :meth:`Connectable.connect`:
    
        .. code-block:: python3
    
            player = relink.gateway.Player(node=...)
            await connectable.connect(cls=player)
    
    2. Passing the class directly to :meth:`Connectable.connect`:
    
        .. code-block:: python3
    
            player = await connectable.connect(cls=relink.gateway.Player)

    Parameters
    ----------
    node: :class:`Node` | :data:`None`
        The node to connect this player to. If ``None``, then this attempts to connect to an available node
        under the parent :class:`NodePool`.
    """

    _ready: bool
    _connection: PlayerConnectionState

    @overload
    def __init__(self, *, node: Node) -> None: ...

    @overload
    def __init__(self, client: discord.Client, channel: discord.abc.Connectable) -> None: ...

    def __init__(
        self,
        client: discord.Client = MISSING,
        channel: discord.abc.Connectable = MISSING,
        *,
        node: Node | None = None,
    ) -> None:
        if client is not MISSING and channel is not MISSING:
            super().__init__(client, channel)
            self._ready = True
        else:
            self._ready = False

    def get_connection_state(self) -> PlayerConnectionState:
        """Gets the connection for this player. This can be overriden by subclasses to implement custom behaviour
        on the connection state.
        """
        return PlayerConnectionState()

    def __call__(self, client: discord.Client, channel: discord.abc.Connectable) -> Self:
        super().__init__(client, channel)
        return self
