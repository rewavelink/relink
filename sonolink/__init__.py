"""
sonolink
~~~~~~

A high-performance Lavalink v4 wrapper for Python, inspired by WaveLink.

:copyright: (c) 2026-present SonoLink Development Team
:license: MIT
"""

from . import gateway, models, rest, utils
from ._version import __version__, version_info
from .gateway import *
from .network.errors import *
from .rest import *
from .utils import *
from ._registry import get_client

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
    "PlayerConnectionState",
    "NodeStatus",
    "TrackEndReason",
    "TrackExceptionSeverity",
    "QueueMode",
    "AutoPlayMode",
    "InactivityMode",
    "SearchProvider",
    "NodeError",
    "InvalidNodePassword",
    "NodeURINotFound",
    "QueueEmpty",
    "HistoryEmpty",
    "Queue",
    "History",
    "ExceptionSeverity",
    "TrackLoadResult",
    "TrackSourceType",
    "RoutePlannerType",
    "IPBlockType",
    "ErrorResponseType",
    "HTTPException",
    "WebSocketError",
    "cached_property",
    "get_client",
)
