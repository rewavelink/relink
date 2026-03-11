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

    :ivar DISCONNECTED: The node is not connected to Lavalink.
    :ivar CONNECTED: The node is connected to Lavalink.
    :ivar CONNECTING: The node is in the process of connecting to Lavalink.
    """

    DISCONNECTED = 1
    CONNECTED = 2
    CONNECTING = 3


class TrackEndReason(StrEnum):
    """Represents a TrackEndEvent's :attr:`TrackEndEvent.reason`.

    :ivar FINISHED: The track finished playing.
    :ivar LOAD_FAILED: The track failed to load.
    :ivar STOPPED: The track was stopped.
    :ivar REPLACED: The track was replaced.
    :ivar CLEANUP: The track was cleaned up.
    """

    FINISHED = "finished"
    LOAD_FAILED = "loadFailed"
    STOPPED = "stopped"
    REPLACED = "replaced"
    CLEANUP = "cleanup"

    @property
    def can_start_next(self) -> bool:
        """Whether the next track can start playing."""
        return self not in (
            TrackEndReason.STOPPED,
            TrackEndReason.REPLACED,
            TrackEndReason.CLEANUP,
        )


class TrackExceptionSeverity(StrEnum):
    """Represents a TrackException's error severity.

    :ivar COMMON: The cause is known and expected, indicates that there
        is nothing wrong with the library itself.
    :ivar SUSPICIOUS: The cause might not be exactly known, but is possibly
        caused by outside factors. For example when an outside service responds
        in a format that we do not expect.
    :ivar FAULT: The probable cause is an issue with the library or there is
        no way to tell what the cause might be. This is the default level and
        other levels are used in cases where the thrower has more in-depth
        knowledge about the error.
    """

    COMMON = "common"
    SUSPICIOUS = "suspicious"
    FAULT = "fault"


class QueueMode(StrEnum):
    """Enum representing the various modes on :class:`wavelink.Queue`

    :ivar NORMAL: Normal queue mode. Tracks are played in the order they were added.
    :ivar LOOP: Loop the current track indefinitely. The next track will not be played until the current track is stopped or replaced.
    :ivar LOOP_ALL: Loop the entire queue indefinitely. Once the queue is empty, it will be refilled with the tracks in the
        history (if enabled) and playback will continue. If history is not enabled, the queue will simply start over
        with the original tracks.
    """

    NORMAL = "normal"
    LOOP = "loop"
    LOOP_ALL = "loop_all"
