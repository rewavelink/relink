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


class Player(BasePlayer):
    """
    A dynamic proxy class for ReLink players.
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

        factory = PlayerFactory()
        actual_class = factory.get_player(framework)

        instance = object.__new__(actual_class)
        instance.__init__(
            *args,
            node=node,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
            volume=volume,
            paused=paused,
            filters=filters,
        )

        return instance

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

    def __call__(self, client: Any, channel: Any) -> Player:
        raise NotImplementedError("Player is a proxy; this is never called directly.")

    async def on_voice_server_update(self, data: Any) -> None: ...

    async def on_voice_state_update(self, data: Any) -> None: ...
