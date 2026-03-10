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

from enum import Enum, StrEnum


class NodeStatus(Enum):
    """Represents the connection status of a node.

    :ivar disconnected: The node is not connected to Lavalink.
    :ivar connected: The node is connected to Lavalink.
    :ivar connecting: The node is in the process of connecting to Lavalink.
    """

    disconnected = 1
    connected = 2
    connecting = 3


class TrackEndReason(StrEnum):
    """Represents a TrackEndEvent's :attr:`TrackEndEvent.reason`.

    :ivar finished: The track finished playing.
    :ivar load_failed: The track failed to load.
    :ivar stopped: The track was stopped.
    :ivar replaced: The track was replaced.
    :ivar cleanup: The track was cleaned up.
    """

    finished = "finished"
    load_failed = "loadFailed"
    stopped = "stopped"
    replaced = "replaced"
    cleanup = "cleanup"

    @property
    def can_start_next(self) -> bool:
        """Whether the next track can start playing."""
        return self not in (
            TrackEndReason.stopped,
            TrackEndReason.replaced,
            TrackEndReason.cleanup,
        )


class TrackExceptionSeverity(StrEnum):
    """Represents a TrackException's error severity.

    :ivar common: The cause is known and expected, indicates that there
        is nothing wrong with the library itself.
    :ivar suspicious: The cause might not be exactly known, but is possibly
        caused by outside factors. For example when an outside service responds
        in a format that we do not expect.
    :ivar fault: The probable cause is an issue with the library or there is
        no way to tell what the cause might be. This is the default level and
        other levels are used in cases where the thrower has more in-depth
        knowledge about the error.
    """

    common = "common"
    suspicious = "suspicious"
    fault = "fault"


class QueueMode(StrEnum):
    """Enum representing the various modes on :class:`wavelink.Queue`

    :ivar normal: Normal queue mode. Tracks are played in the order they were added.
    :ivar loop: Loop the current track indefinitely. The next track will not be played until the current track is stopped or replaced.
    :ivar loop_all: Loop the entire queue indefinitely. Once the queue is empty, it will be refilled with the tracks in the
        history (if enabled) and playback will continue. If history is not enabled, the queue will simply start over
        with the original tracks.
    """

    normal = "normal"
    loop = "loop"
    loop_all = "loop_all"
