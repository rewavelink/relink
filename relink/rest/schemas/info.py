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
    """
    Represents the Lavalink Info response payload.

    Returned by the ``/v4/info`` REST endpoint and describes the running node.

    :attr version: Version metadata of the Lavalink server.
    :attr build_time: Build timestamp in Unix milliseconds.
    :attr git: Git repository information for this build.
    :attr jvm: JVM version used to run Lavalink.
    :attr lavaplayer: Embedded Lavaplayer version.
    :attr source_managers: Enabled source managers.
    :attr filters: Names of supported audio filters.
    :attr plugins: Installed Lavalink plugins.
    """

    version: VersionObject
    build_time: int = msgspec.field(name="buildTime")
    git: GitObject
    jvm: str
    lavaplayer: str
    source_managers: list[str] = msgspec.field(name="sourceManagers")
    filters: list[str]
    plugins: list[PluginObject]


class VersionObject(msgspec.Struct, kw_only=True, frozen=True):
    """
    Represents Lavalink version metadata.

    :attr semver: Full semantic version string.
    :attr major: Major version number.
    :attr minor: Minor version number.
    :attr patch: Patch version number.
    :attr pre_release: Pre-release identifier if present.
    :attr build: Optional build metadata string.
    """

    semver: str
    major: int
    minor: int
    patch: int
    pre_release: str | None = msgspec.field(name="preRelease", default=None)
    build: str | None = None


class GitObject(msgspec.Struct, kw_only=True, frozen=True):
    """
    Represents Git metadata for the Lavalink build.

    :attr branch: Git branch name.
    :attr commit: Commit hash.
    :attr commit_time: Commit timestamp in Unix milliseconds.
    """

    branch: str
    commit: str
    commit_time: int = msgspec.field(name="commitTime")


class PluginObject(msgspec.Struct, kw_only=True, frozen=True):
    """
    Represents an installed Lavalink plugin.

    :attr name: Plugin name.
    :attr version: Plugin version string.
    """

    name: str
    version: str


class StatsResponse(msgspec.Struct, kw_only=True):
    """
    Represents the Lavalink Stats response payload.

    Returned periodically over WebSocket and via ``/v4/stats``.

    :attr players: Total number of players.
    :attr playing_players: Number of actively playing players.
    :attr uptime: Node uptime in milliseconds.
    :attr memory: JVM memory usage statistics.
    :attr cpu: CPU usage statistics.
    :attr frame_stats: Optional audio frame statistics.
    """

    players: int
    playing_players: int = msgspec.field(name="playingPlayers")
    uptime: int
    memory: MemoryObject
    cpu: CPUObject
    frame_stats: FrameStatsObject | None = msgspec.field(
        name="frameStats", default=None
    )


class MemoryObject(msgspec.Struct, kw_only=True):
    """
    Represents JVM memory usage statistics.

    :attr free: Free memory in bytes.
    :attr used: Used memory in bytes.
    :attr allocated: Allocated memory in bytes.
    :attr reservable: Maximum reservable memory in bytes.
    """

    free: int
    used: int
    allocated: int
    reservable: int


class CPUObject(msgspec.Struct, kw_only=True):
    """
    Represents CPU usage statistics.

    :attr cores: Number of available CPU cores.
    :attr system_load: System CPU load as a fraction.
    :attr lavalink_load: CPU load caused by Lavalink.
    """

    cores: int
    system_load: float = msgspec.field(name="systemLoad")
    lavalink_load: float = msgspec.field(name="lavalinkLoad")


class FrameStatsObject(msgspec.Struct, kw_only=True):
    """
    Represents audio frame delivery statistics.

    :attr sent: Number of frames successfully sent.
    :attr nulled: Number of frames that were missing audio data.
    :attr deficit: Frame deficit relative to the expected rate
        (3000 frames/player). Negative means excess frames,
        positive means insufficient frames.
    """

    sent: int
    nulled: int
    deficit: int


VersionResponse = Annotated[str, "x.y.z format"]
