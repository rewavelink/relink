"""
sonolink.rest.schemas
~~~~~~~~~~~~~~~~~~~

Submodule containing all the schemas used in the rest module.

:copyright: (c) 2026-present SonoLink Development Team
:license: MIT
"""

from .filters import *
from .info import *
from .planner import *
from .player import *
from .playlist import *
from .session import *
from .track import *

__all__ = (
    "PlayerFilters",
    "EqualizerFilter",
    "KaraokeFilter",
    "TimescaleFilter",
    "TremoloFilter",
    "VibratoFilter",
    "RotationFilter",
    "DistortionFilter",
    "ChannelMixFilter",
    "LowPassFilter",
    "InfoResponse",
    "VersionObject",
    "GitObject",
    "PluginObject",
    "StatsResponse",
    "MemoryObject",
    "CPUObject",
    "FrameStatsObject",
    "VersionResponse",
    "DetailsObject",
    "IPBlockObject",
    "FailingAddressObject",
    "RoutePlannerStatusResponse",
    "UnmarkFailedAddressRequest",
    "UnmarkFailedAddressResponse",
    "UnmarkAllFailedAddressesResponse",
    "Player",
    "PlayerState",
    "PlayerVoiceState",
    "UpdatePlayerRequest",
    "UpdatePlayerTrackRequest",
    "GetPlayersResponse",
    "GetPlayerResponse",
    "UpdatePlayerResponse",
    "DestroyPlayerResponse",
    "PlaylistInfo",
    "UpdateSessionRequest",
    "UpdateSessionResponse",
    "Track",
    "TrackInfo",
    "TrackLoadingResponse",
    "PlaylistData",
    "TrackDecodeResponse",
    "TracksDecodeResponse",
)
