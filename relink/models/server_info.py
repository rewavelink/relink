"""
MIT License

Copyright (c) 2019-2025 PythonistaGuild, EvieePy; 2025-present ReWaveLink Development Team.

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

import datetime
from typing import TYPE_CHECKING

from relink.utils import cached_property

from .base import BaseModel

if TYPE_CHECKING:
    from ..rest.schemas.info import (
        InfoResponse as ServerInfoPayload,
        VersionObject,
        GitObject,
        PluginObject,
    )


# TODO: maybe add Model-like classes for version, git, and plugins?

class ServerInfo(BaseModel["ServerInfoPayload"]):
    """
    Represents a Lavalink server's metadata & stats information.

    This class wraps the raw :class:`relink.rest.schemas.InfoResponse` schema and provides
    a high-level interface for accessing Lavalink servers stats and metadata.
    """

    __slots__ = ("_cs_build_time",)

    @property
    def version(self) -> VersionObject:
        """A struct denoting the version of this node."""
        return self._data.version

    @cached_property("_cs_build_time")
    def build_time(self) -> datetime.datetime:
        """A datetime.datetime object representing the timestamp on which the Lavalink
        jar was built.
        """
        return datetime.datetime.fromtimestamp(self._data.build_time, tz=datetime.timezone.utc)

    @property
    def git(self) -> GitObject:
        """A struct denoting the git version of the Lavalink server."""
        return self._data.git

    @property
    def jvm(self) -> str:
        """The JVM version used to run the Lavalink server."""
        return self._data.jvm

    @property
    def lavaplayer(self) -> str:
        """The Lavaplayer version being used by the Lavalink server."""
        return self._data.lavaplayer

    @property
    def source_managers(self) -> list[str]:
        """The enabled source managers of the Lavalink server."""
        return self._data.source_managers

    @property
    def filters(self) -> list[str]:
        """The enabled filters of the Lavalink server."""
        return self._data.filters

    @property
    def plugins(self) -> list[PluginObject]:
        """A list of structs denoting the available plugins of the Lavalink server."""
        return self._data.plugins
