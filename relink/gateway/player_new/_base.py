"""
MIT License

Copyright (c) 2019-2026 PythonistaGuild, EvieePy; 2026-present ReWaveLink Development Team.

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

import abc
import asyncio
from typing import TYPE_CHECKING, Annotated, Any

from handlers._autoplay import AutoPlayHandler
from handlers._events import EventsHandler
from handlers._incativity import InactivityHandler
from handlers._lifecycle import LifecycleHandler
from handlers._playback import PlaybackHandler

if TYPE_CHECKING:
    from relink.gateway.schemas.receive import PlayerState
    from relink.models.filters import Filters
    from relink.models.settings import AutoPlaySettings, HistorySettings
    from relink.models.track import Playable

    from ..enums import AutoPlayMode, QueueMode
    from ..node import Node
    from ..queue.queue import Queue

__all__ = ("BasePlayer",)


class PlayerConnectionState:
    """
    Represents the voice connection state for a :class:`BasePlayer`.

    This class is intended to be subclassed if you need to store
    extra metadata during the Discord handshake.
    """

    __slots__ = (
        "token",
        "endpoint",
        "session_id",
        "channel_id",
        "_connected_flag",
    )

    def __init__(self) -> None:
        self.token: str | None = None
        self.endpoint: str | None = None
        self.session_id: str | None = None
        self.channel_id: str | None = None
        self._connected_flag: asyncio.Event = asyncio.Event()

    @property
    def is_complete(self) -> bool:
        """Indicates if all gateway data has been received."""
        return all((self.token, self.endpoint, self.session_id, self.channel_id))


class BasePlayer(abc.ABC):
    """
    Abstract base class that defines the interface for a Lavalink player.

    This class is library-agnostic and is intended to be subclassed to provide
    concrete implementations compatible with ``discord.py``, ``disnake``, or ``py-cord``.
    Each library-specific subclass is responsible for implementing the voice protocol
    integration (e.g., inheriting from the appropriate ``VoiceProtocol`` class) and
    fulfilling the abstract methods defined here.

    The public API exposed by this class remains consistent across all three
    Discord library backends, allowing shared business logic, extensions, and
    third-party integrations to target ``BasePlayer`` without coupling to any
    specific library.

    Parameters
    ----------
    node : :class:`~relink.node.Node` | None
        The Lavalink node to associate this player with. If ``None``, the player
        will attempt to resolve an available node at connection time.
    queue_mode : :class:`~relink.enums.QueueMode`
        The initial queue looping mode. Defaults to ``QueueMode.NORMAL``.
    autoplay_settings : :class:`~relink.models.settings.AutoPlaySettings` | None
        Configuration for the AutoPlay feature. If ``None``, a default
        configuration is used.
    history_settings : :class:`~relink.models.settings.HistorySettings` | None
        Configuration for queue history. If ``None``, a default configuration
        is used. History must be enabled if AutoPlay is used.
    volume : :class:`int` | None
        The initial volume of the player (0–1000). Defaults to ``100``.
    paused : :class:`bool` | None
        Whether the player should start in a paused state. Defaults to ``False``.
    filters : :class:`~relink.models.filters.Filters` | None
        The initial set of audio filters to apply. If ``None``, an empty
        :class:`~relink.models.filters.Filters` instance is used.

    Attributes
    ----------
    guild
        The guild this player is attached to. The concrete type depends on the
        underlying Discord library (e.g., ``discord.Guild``, ``disnake.Guild``,
        or ``pycord``'s equivalent).
    channel
        The voice channel this player is currently connected to. The concrete
        type depends on the underlying Discord library.
    client
        The Discord client instance driving this player. The concrete type
        depends on the underlying Discord library.
    """

    __slots__ = (
        "_autoplay_handler",
        "_connection",
        "_events_handler",
        "_filters",
        "_inactivity_handler",
        "_last_position",
        "_last_update",
        "_lifecycle_handler",
        "_node",
        "_paused",
        "_playback_handler",
        "_queue",
        "_ready",
        "_volume",
    )

    _connection: PlayerConnectionState
    _filters: Filters
    _last_position: Annotated[int, "ms"]
    _last_update: Annotated[float, "time.monotonic"]
    _node: Node | None
    _paused: bool
    _queue: Queue
    _ready: bool
    _volume: int

    def __init__(
        self,
        *,
        node: Node | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
    ) -> None:
        self._node = node
        self._connection = self.get_connection_state()

        self._filters = filters or Filters()
        self._queue = Queue(mode=queue_mode, history_settings=history_settings)
        self._paused = paused or False
        self._volume = volume if volume is not None else 100

        self._last_position: int = 0
        self._last_update: float = 0.0

        self._autoplay_handler: AutoPlayHandler = AutoPlayHandler(
            self, settings=autoplay_settings
        )
        self._events_handler: EventsHandler = EventsHandler(self)
        self._inactivity_handler: InactivityHandler = InactivityHandler(self)
        self._lifecycle_handler: LifecycleHandler = LifecycleHandler(self)
        self._playback_handler: PlaybackHandler = PlaybackHandler(self)

        self._ready: bool = False

    @abc.abstractmethod
    def __call__(self, client: Any, channel: Any) -> BasePlayer: ...

    @property
    @abc.abstractmethod
    def autoplay(self) -> AutoPlayMode:
        """
        The current :class:`~relink.enums.AutoPlayMode` for this player.

        When AutoPlay is enabled, the player will automatically fetch and enqueue
        related tracks when the queue is exhausted.

        Raises
        ------
        RuntimeError
            When setting, if the player's history is disabled (history is required
            for AutoPlay to function).
        """
        ...

    @autoplay.setter
    @abc.abstractmethod
    def autoplay(self, value: AutoPlayMode) -> None: ...

    @property
    @abc.abstractmethod
    def current(self) -> Playable | None:
        """
        The track that is currently playing, or ``None`` if the player is idle.

        Returns
        -------
        :class:`~relink.models.track.Playable` | None
        """
        ...

    @property
    @abc.abstractmethod
    def filters(self) -> Filters:
        """
        The :class:`~relink.models.filters.Filters` currently applied to this player.

        To apply new filters, use :meth:`set_filters` rather than mutating this
        object directly, so that the updated state is dispatched to the Lavalink node.

        Returns
        -------
        :class:`~relink.models.filters.Filters`
        """
        ...

    @property
    @abc.abstractmethod
    def guild(self) -> Any:
        """
        The guild this player is associated with.

        The concrete return type is the guild class of the underlying Discord
        library (e.g. ``discord.Guild``, ``disnake.Guild``).

        Raises
        ------
        RuntimeError
            If the player has not yet been attached to a guild.
        """
        ...

    @property
    @abc.abstractmethod
    def node(self) -> Node:
        """
        The :class:`~relink.node.Node` this player is currently attached to.

        Raises
        ------
        RuntimeError
            If the player is not currently attached to a node.
        """
        ...

    @property
    @abc.abstractmethod
    def paused(self) -> bool:
        """
        Whether the player is currently paused.

        Returns
        -------
        :class:`bool`
        """
        ...

    @property
    @abc.abstractmethod
    def position(self) -> int:
        """
        The estimated current playback position in milliseconds.

        When the player is paused or has not yet started, this returns the last
        known position. Otherwise, it is calculated by interpolating the time
        elapsed since the last state update received from the Lavalink node.

        Returns
        -------
        :class:`int`
            Position in milliseconds.
        """
        ...

    @property
    @abc.abstractmethod
    def queue(self) -> Queue:
        """
        The :class:`~relink.queue.queue.Queue` associated with this player.

        The queue manages both upcoming tracks and playback history. Tracks can
        be added with ``queue.put()`` / ``queue.put_wait()`` and inspected or
        manipulated via the queue's public API.

        Returns
        -------
        :class:`~relink.queue.queue.Queue`
        """
        ...

    @property
    @abc.abstractmethod
    def volume(self) -> int:
        """
        The current volume of the player as an integer in the range ``0``–``1000``.

        ``100`` represents the default (unmodified) volume. Values above ``100``
        amplify the audio and may introduce distortion.

        Returns
        -------
        :class:`int`
        """
        ...

    @abc.abstractmethod
    async def play(
        self,
        track: Playable,
        /,
        *,
        start: int = 0,
        end: int | None = None,
        volume: int | None = None,
        paused: bool | None = None,
    ) -> Playable:
        """
        Begin playback of the specified track.

        If a track is already playing, it is stopped and the currently playing
        track is added to history (if history is enabled) before the new track
        starts.

        Parameters
        ----------
        track : :class:`~relink.models.track.Playable`
            The track to play.
        start : :class:`int`
            The position in milliseconds at which to begin playback.
            Defaults to ``0``.
        end : :class:`int` | None
            The position in milliseconds at which to stop playback.
            If ``None``, the track plays to completion. Defaults to ``None``.
        volume : :class:`int` | None
            Override the player volume for this track only. If ``None``,
            the current player volume is used. Defaults to ``None``.
        paused : :class:`bool` | None
            If ``True``, the track begins in a paused state. If ``None``,
            the player's current pause state is preserved. Defaults to ``None``.

        Returns
        -------
        :class:`~relink.models.track.Playable`
            The track that was dispatched to the Lavalink node for playback.
        """
        ...

    @abc.abstractmethod
    async def stop(
        self,
        /,
        *,
        clear_queue: bool = False,
        clear_history: bool = False,
    ) -> None:
        """
        Stop the currently playing track.

        This sends a stop request to the Lavalink node and resets the player's
        internal position tracking and current track reference.

        Parameters
        ----------
        clear_queue : :class:`bool`
            If ``True``, all pending tracks in the queue are removed.
            Defaults to ``False``.
        clear_history : :class:`bool`
            If ``True``, the playback history is cleared. Defaults to ``False``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        ...

    @abc.abstractmethod
    async def pause(self, value: bool = True, /) -> None:
        """
        Set the pause state of the player.

        Parameters
        ----------
        value : :class:`bool`
            Pass ``True`` to pause or ``False`` to resume playback.
            Defaults to ``True``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        ...

    @abc.abstractmethod
    async def resume(self) -> None:
        """
        Resume playback if the player is currently paused.

        This is a convenience alias for ``await player.pause(False)``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        ...

    @abc.abstractmethod
    async def skip(self) -> Playable | None:
        """
        Skip the currently playing track and advance to the next one in the queue.

        If the queue is empty and AutoPlay is enabled, a related track may be
        fetched automatically. If neither a queued nor an AutoPlay track is
        available, playback stops and ``None`` is returned.

        Returns
        -------
        :class:`~relink.models.track.Playable` | None
            The track that began playing after the skip, or ``None`` if the
            player stopped due to an empty queue with no AutoPlay fallback.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        QueueEmpty
            If the queue is empty and AutoPlay is disabled or yields no results.
        """
        ...

    @abc.abstractmethod
    async def previous(self) -> Playable:
        """
        Return to the most recently played track in the history.

        The current track is pushed back to the front of the queue so it can
        be reached again via :meth:`skip`. The historical track then begins
        playing immediately.

        Returns
        -------
        :class:`~relink.models.track.Playable`
            The historical track that is now playing.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        HistoryEmpty
            If there is no previous track in the history.
        """
        ...

    @abc.abstractmethod
    async def seek(self, position: int, /) -> None:
        """
        Seek to an arbitrary position within the current track.

        Parameters
        ----------
        position : :class:`int`
            The target position in milliseconds. Must be within the bounds
            of the current track's duration.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        ...

    @abc.abstractmethod
    async def set_volume(self, value: int, /) -> None:
        """
        Set the player's output volume.

        Parameters
        ----------
        value : :class:`int`
            The desired volume level, in the range ``0``–``1000``.
            ``100`` is the default (unmodified) level.

        Raises
        ------
        ValueError
            If ``value`` is outside the range ``0``–``1000``.
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        ...

    @abc.abstractmethod
    async def set_filters(
        self,
        filters: Filters,
        /,
        *,
        seek: bool = False,
    ) -> None:
        """
        Apply a new set of audio filters to this player.

        Parameters
        ----------
        filters : :class:`~relink.models.filters.Filters`
            The :class:`~relink.models.filters.Filters` instance to apply.
        seek : :class:`bool`
            If ``True``, the player seeks to the current position immediately
            after applying filters. This forces Lavalink to process the audio
            through the new filter chain without a audible delay.
            Defaults to ``False``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        ...

    @abc.abstractmethod
    async def on_voice_server_update(self, data: Any) -> None:
        """
        Handle a ``VOICE_SERVER_UPDATE`` payload from the Discord gateway.

        This provides the voice server token and endpoint required by the
        Lavalink node to establish or re-establish the audio stream. This
        method should be called by the library-specific subclass in response
        to the corresponding gateway event.

        The ``data`` dictionary is passed as a raw mapping so that this base
        class remains decoupled from any specific library's type aliases.
        Subclasses may cast it to the appropriate typed dict for their library
        (e.g., ``discord.types.voice.VoiceServerUpdate``,
        ``disnake.types.voice.VoiceServerUpdate``).

        Parameters
        ----------
        data : Any
            The raw ``VOICE_SERVER_UPDATE`` payload received from the Discord
            gateway.
        """
        ...

    @abc.abstractmethod
    async def on_voice_state_update(self, data: Any) -> None:
        """
        Handle a ``VOICE_STATE_UPDATE`` payload from the Discord gateway.

        This provides the session ID and channel ID required for the voice
        connection handshake with the Lavalink node. This method should be
        called by the library-specific subclass in response to the
        corresponding gateway event.

        The ``data`` dictionary is passed as a raw mapping so that this base
        class remains decoupled from any specific library's type aliases.
        Subclasses may cast it to the appropriate typed dict for their library
        (e.g., ``discord.types.voice.GuildVoiceState``,
        ``disnake.types.voice.GuildVoiceState``).

        Parameters
        ----------
        data : Any
            The raw ``VOICE_STATE_UPDATE`` payload received from the Discord
            gateway.
        """
        ...

    @abc.abstractmethod
    def get_connection_state(self) -> Any:
        """
        Return the connection state handler for this player.

        The default implementation in library-specific subclasses should return
        a ``PlayerConnectionState`` instance (or an equivalent subclass), which
        tracks the gateway handshake data (token, endpoint, session ID, channel
        ID) needed to establish the Lavalink voice session.

        This method exists as a hook so that advanced users can override it to
        inject a custom connection state class with additional metadata relevant
        to their use case.

        Returns
        -------
        Any
            A connection state object. Library-specific subclasses should narrow
            this return type to their concrete ``PlayerConnectionState`` class.
        """
        ...

    async def _dispatch_event(self, data: dict[str, Any]) -> None:
        await self._events_handler._dispatch_event(data)

    def _update_state(self, state: PlayerState, /) -> None:
        self._events_handler._update_state(state)

    async def _dispatch_voice_update(self) -> None:
        await self._events_handler._dispatch_voice_update()

    def _check_inactivity(self) -> None:
        self._inactivity_handler._check_inactivity()

    def _start_inactivity_timer(self) -> None:
        self._inactivity_handler._start_inactivity_timer()

    def _stop_inactivity_timer(self) -> None:
        self._inactivity_handler._stop_inactivity_timer()

    async def _inactivity_timeout(self, timeout: int) -> None:
        await self._inactivity_handler._inactivity_timeout(timeout)
