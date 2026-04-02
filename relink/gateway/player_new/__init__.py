import os
from typing import Any, cast

from ._base import BasePlayer
from ._factory import FrameworkLiteral, PlayerFactory

__all__ = (
    "Player",
    "BasePlayer",
    "FrameworkLiteral",
)


class Player(BasePlayer):
    """
    A dynamic proxy class for ReLink players.
    """

    def __new__(cls, *args: Any, **kwargs: Any) -> Any:
        env_framework = os.getenv("RELINK_FRAMEWORK", "discord.py")
        framework = cast(FrameworkLiteral, env_framework)

        factory = PlayerFactory()
        actual_class = factory.get_player(framework)

        instance = object.__new__(actual_class)
        instance.__init__(*args, **kwargs)

        return instance

    @classmethod
    def __subclasscheck__(cls, subclass: type) -> bool:
        """Standardizes issubclass(DpyPlayer, Player) -> True."""
        return issubclass(subclass, BasePlayer)

    @classmethod
    def __instancecheck__(cls, instance: Any) -> bool:
        """Standardizes isinstance(vc_instance, Player) -> True."""
        return isinstance(instance, BasePlayer)
