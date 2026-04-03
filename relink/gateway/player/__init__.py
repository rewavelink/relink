import logging
import os
from typing import TYPE_CHECKING, Any, cast

from ._base import BasePlayer, PlayerConnectionState
from ._factory import FrameworkLiteral, PlayerFactory
from ..enums import QueueMode

if TYPE_CHECKING:
    from ..node import Node
    from ...models.settings import AutoPlaySettings, HistorySettings

    from ...models.filters import Filters

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
        *,
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
            node=node,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
            volume=volume,
            paused=paused,
            filters=filters,
        )

        return instance

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        """Standardizes issubclass(DpyPlayer, Player) -> True."""
        return issubclass(subclass, BasePlayer)

    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Standardizes isinstance(vc_instance, Player) -> True."""
        return isinstance(instance, BasePlayer)
