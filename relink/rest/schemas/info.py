"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

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
from typing import Annotated

import msgspec


class InfoResponse(msgspec.Struct, kw_only=True):
    """Represents the Info Response structure payload."""

    version: VersionObject
    build_time: int = msgspec.field(name="buildTime")
    git: GitObject
    jvm: str
    lavaplayer: str
    source_managers: list[str] = msgspec.field(name="sourceManagers")
    filters: list[str]
    plugins: list[PluginObject]


class VersionObject(msgspec.Struct, kw_only=True, frozen=True):
    """Represents the Version Object structure payload"""

    semver: str
    major: int
    minor: int
    patch: int
    pre_release: str | None = msgspec.field(name="preRelease", default=None)
    build: str | None = None


class GitObject(msgspec.Struct, kw_only=True, frozen=True):
    """Represents the Git Object structure payload"""

    branch: str
    commit: str
    commit_time: int = msgspec.field(name="commitTime")


class PluginObject(msgspec.Struct, kw_only=True, frozen=True):
    """Represents the Plugin Object structure payload"""

    name: str
    version: str


class StatsResponse(msgspec.Struct, kw_only=True):
    """Represents the Stats Response structure payload."""

    players: int
    playing_players: int = msgspec.field(name="playingPlayers")
    uptime: int
    memory: MemoryObject
    cpu: CPUObject
    frame_stats: FrameStatsObject | None = msgspec.field(
        name="frameStats", default=None
    )  # Optional; may be missing for some endpoints


class MemoryObject(msgspec.Struct, kw_only=True):
    """Represents a MemoryObject structure payload."""

    free: int
    used: int
    allocated: int
    reservable: int


class CPUObject(msgspec.Struct, kw_only=True):
    """Represents a CPUObject structure payload."""

    cores: int
    system_load: float = msgspec.field(name="systemLoad")
    lavalink_load: float = msgspec.field(name="lavalinkLoad")


class FrameStatsObject(msgspec.Struct, kw_only=True):
    """Represents a FrameStatsObject structure payload."""

    sent: int
    nulled: int
    deficit: int  # Frames deficit relative to expected 3000/player (1 every 20 ms); negative = too many, positive = too few


VersionResponse = Annotated[str, "x.y.z format"]
