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

import logging
import os
from typing import TYPE_CHECKING, Any, cast

from ..enums import QueueMode
from ._base import BasePlayer, PlayerConnectionState
from ._factory import FrameworkLiteral, PlayerFactory

if TYPE_CHECKING:
    from relink.models.filters import Filters
    from relink.models.settings import AutoPlaySettings, HistorySettings

    from ..node import Node


__all__ = (
    "Player",
    "BasePlayer",
    "PlayerConnectionState",
    "FrameworkLiteral",
)

_log = logging.getLogger(__name__)


_factory: PlayerFactory = PlayerFactory()


class Player(BasePlayer):
    """
    A dynamic proxy class for ReLink players.

    Automatically resolves the appropriate :class:`~relink.player.BasePlayer`
    implementation for the detected or configured Discord library backend
    (``discord.py``, ``disnake``, or ``py-cord``) at instantiation time.

    The framework is resolved from the ``RELINK_FRAMEWORK`` environment variable,
    falling back to ``"discord.py"`` if unset.

    There are two primary ways to create a player:

    1. **Class-pass** — pass the class itself to the voice channel's ``connect``
       method. The library will instantiate it directly::

           player = await voice_channel.connect(cls=Player)

    2. **Instance-pass** — construct a pre-configured instance and pass it
       instead. The library will call ``player(client, channel)`` which hits
       the concrete adapter's :meth:`__call__`::

           player = Player(node=some_node, volume=80)
           await voice_channel.connect(cls=player)

    Parameters
    ----------
    node : :class:`~relink.node.Node` | None
        The Lavalink node to associate with this player. If ``None``, an
        available node is resolved from the client's node pool at connection
        time.
    queue_mode : :class:`~relink.enums.QueueMode`
        The initial queue looping mode. Defaults to ``QueueMode.NORMAL``.
    autoplay_settings : :class:`~relink.models.settings.AutoPlaySettings` | None
        AutoPlay configuration. ``None`` uses the default configuration.
    history_settings : :class:`~relink.models.settings.HistorySettings` | None
        History configuration. ``None`` uses the default configuration.
        History must be enabled when AutoPlay is active.
    volume : :class:`int` | None
        Initial volume in the range ``0``–``1000``. Defaults to ``100``.
    paused : :class:`bool` | None
        Whether the player should start in a paused state. Defaults to
        ``False``.
    filters : :class:`~relink.models.filters.Filters` | None
        Initial audio filters. Defaults to an empty
        :class:`~relink.models.filters.Filters` instance.

    Attributes
    ----------
    guild
        The guild this player is attached to. The concrete type depends on
        the underlying Discord library (e.g. ``discord.Guild``,
        ``disnake.Guild``).
    channel
        The voice channel this player is currently connected to. The concrete
        type depends on the underlying Discord library.
    client
        The Discord client instance driving this player. The concrete type
        depends on the underlying Discord library.
    """

    def __new__(
        cls,
        *args: Any,
        node: Node | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
    ) -> Any:
        env_framework = os.getenv("RELINK_FRAMEWORK", "discord.py")
        framework = cast(FrameworkLiteral, env_framework)
        actual_class = _factory.get_player(framework)

        return actual_class(
            *args,
            node=node,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
            volume=volume,
            paused=paused,
            filters=filters,
        )

    def __init__(
        self,
        *args: Any,
        node: Node | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
    ) -> None:
        """
        Shadow init to satisfy type checkers.
        The actual initialization happens in __new__ via the factory.
        """
        pass

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        """Standardizes issubclass(DpyPlayer, Player) -> True."""
        return issubclass(subclass, BasePlayer)

    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Standardizes isinstance(vc_instance, Player) -> True."""
        return isinstance(instance, BasePlayer)

    def __call__(self, client: Any, channel: Any) -> Any:
        raise NotImplementedError("Player is a proxy; this is never called directly.")

    async def on_voice_server_update(self, data: Any) -> None: ...

    async def on_voice_state_update(self, data: Any) -> None: ...
