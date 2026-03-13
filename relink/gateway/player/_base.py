from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from . import Player

__all__ = ()

_log = logging.getLogger("relink.gateway.player")


class HandlerBase:
    def __init__(self, player: Player, /) -> None:
        self._player: Player = player
