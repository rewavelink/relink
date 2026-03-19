"""
relink
~~~~~~

An async-prepared, high performance, Lavalink wrapper for discord.py.

:copyright: (c) 2019-2026 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team
:license: MIT
"""

from ._version import __version__, version_info
from .gateway.client import Client
from .gateway.node import Node
from .gateway.player import Player
from . import gateway, models, rest, utils

__all__ = (
    "__version__",
    "version_info",
    "Client",
    "Node",
    "Player",
    "gateway",
    "models",
    "rest",
    "utils",
)
