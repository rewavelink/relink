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

import asyncio
import logging
import time
from typing import TYPE_CHECKING, Annotated, Any, Self, overload

import discord
from discord.types.voice import GuildVoiceState, VoiceServerUpdate

from relink import _registry
from relink.models.settings import AutoPlaySettings, HistorySettings
from relink.rest.schemas.filters import PlayerFilters

from ...models.track import Playable
from ..enums import AutoPlayMode
from ..queue.queue import Queue
from ..schemas.receive import PlayerState
from ._autoplay import AutoPlayHandler
from ._events import EventsHandler
from ._inactivity import InactivityHandler
from ._lifecycle import LifecycleHandler
from ._playback import PlaybackHandler

if TYPE_CHECKING:
    from ..node import Node

_log = logging.getLogger(__name__)
MISSING = discord.utils.MISSING


__all__ = (
    "Player",
    "PlayerConnectionState",
)


class PlayerConnectionState:
    """
    Represents the voice connection state for a :class:`Player`.

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


class Player(discord.VoiceProtocol):
    """
    Represents a :class:`discord.VoiceProtocol` implementation for Lavalink.

    This class handles the voice connection handshake between Discord and a Lavalink :class:`Node`.
    It is responsible for dispatching voice server and state updates to the node to establish
    and maintain the audio stream.

    There are two primary ways to initialize a player:

    1. Creating an instance manually and passing it to :meth:`discord.abc.Connectable.connect`:

        .. code-block:: python3

            player = relink.Player(node=some_node)
            await voice_channel.connect(cls=player)

    2. Passing the class directly to :meth:`discord.abc.Connectable.connect`:

        .. code-block:: python3

            # This will use the default NodePool to find an available node
            await voice_channel.connect(cls=relink.Player)

    Parameters
    ----------
    node: :class:`Node` | :data:`None`
        The node to associate this player with. If ``None``, the player will attempt
        to fetch an available node from the :class:`Client` during the connection process.

    Attributes
    ----------
    guild: :class:`discord.Guild`
        The guild this player is attached to.
    filters: :class:`PlayerFilters`
        The currently applied filters for this player.
    paused: :class:`bool`
        Whether the player is currently paused.
    position: :class:`int`
        The current position of the player in milliseconds.
    volume: :class:`int`
        The current volume of the player (0-1000).
    queue: :class:`Queue`
        The track queue associated with this player. This handles both upcoming
        tracks and playback history.
    current: :class:`Playable` | :data:`None`
        The currently playing track, or ``None`` if nothing is playing.
    node: :class:`Node`
        The node this player is currently attached to.
    """

    __slots__ = (
        "_autoplay_handler",
        "_connection",
        "_events_handler",
        "_filters",
        "_guild",
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
    _filters: PlayerFilters
    _guild: discord.Guild | None
    _last_position: Annotated[int, "ms"]
    _last_update: Annotated[float, "time.monotonic"]
    _node: Node | None
    _paused: bool
    _queue: Queue
    _ready: bool
    _volume: int

    def __repr__(self) -> str:
        return (
            f"<Player guild_id={self.guild.id} ready={self._ready} node={self._node!r}>"
        )

    @overload
    def __init__(
        self,
        *,
        node: Node | None = ...,
        autoplay_settings: AutoPlaySettings | None = ...,
        history_settings: HistorySettings | None = ...,
        volume: int | None = ...,
        paused: bool | None = ...,
        filters: PlayerFilters | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> None: ...

    def __init__(
        self,
        client: discord.Client = MISSING,
        channel: discord.abc.Connectable = MISSING,
        *,
        node: Node | None = None,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: PlayerFilters | None = None,
    ) -> None:
        self._guild = None
        self._node = node
        self._connection = self.get_connection_state()

        self._filters = PlayerFilters()
        self._queue = Queue(history_settings=history_settings)
        self._paused = False
        self._volume = 100

        self._last_position = 0
        self._last_update = 0.0

        self._autoplay_handler = AutoPlayHandler(self, settings=autoplay_settings)
        self._events_handler = EventsHandler(self)
        self._inactivity_handler = InactivityHandler(self)
        self._lifecycle_handler = LifecycleHandler(self)
        self._playback_handler = PlaybackHandler(self)

        if client is not MISSING and channel is not MISSING:
            super().__init__(client=client, channel=channel)
            if isinstance(channel, discord.abc.GuildChannel):
                self._guild = channel.guild
            self._ready = True
        else:
            self.client = MISSING
            self.channel = MISSING
            self._ready = False

    def __call__(
        self,
        client: discord.Client,
        channel: discord.abc.Connectable,
    ) -> Self:
        super().__init__(client, channel)

        if isinstance(channel, (discord.VoiceChannel, discord.StageChannel)):
            self._guild = channel.guild

        self._ensure_node()
        return self

    @property
    def autoplay(self) -> AutoPlayMode:
        """The current AutoPlay mode for this player."""
        return self._autoplay_handler._settings.mode

    @autoplay.setter
    def autoplay(self, value: AutoPlayMode) -> None:
        if not self._queue._history._settings.enabled:
            raise RuntimeError(
                f"Player {self.guild.id} has disabled history, which is required for AutoPlay."
            )
        self._autoplay_handler._settings.mode = value

    @property
    def current(self) -> Playable | None:
        """The currently playing track, or None if nothing is playing."""
        return self._queue.current_track

    @property
    def filters(self) -> PlayerFilters:
        """The currently applied filters for this player."""
        return self._filters

    @property
    def guild(self) -> discord.Guild:
        """The :class:`discord.Guild` this player is associated with."""
        if self._guild is None:
            raise RuntimeError("Player is not yet attached to a guild.")
        return self._guild

    @property
    def node(self) -> Node:
        """
        The :class:`Node` this player is currently attached to.

        Raises
        ------
        RuntimeError
            The player is not currently attached to a node.
        """

        if self._node is None:
            raise RuntimeError(f"Player {self.guild.id} is not attached to a node.")
        return self._node

    @property
    def paused(self) -> bool:
        """Whether the player is currently paused."""
        return self._paused

    @property
    def position(self) -> int:
        """The current position of the player in milliseconds."""
        if self._paused or self._last_update == 0:
            return self._last_position

        delta = int((time.monotonic() - self._last_update) * 1000)
        return self._last_position + delta

    @property
    def queue(self) -> Queue:
        """The :class:`Queue` associated with this player, handling upcoming tracks and history."""
        return self._queue

    @property
    def volume(self) -> int:
        """The current volume of the player as an integer between 0 and 1000."""
        return self._volume

    def get_connection_state(self) -> PlayerConnectionState:
        """
        Returns the connection state handler for this player.

        This can be overridden by subclasses to implement custom behavior
        or use a custom :class:`PlayerConnectionState` implementation.

        Returns
        -------
        :class:`PlayerConnectionState`
            The connection state instance for this player.
        """
        return PlayerConnectionState()

    async def connect(
        self,
        *,
        timeout: float = 10,
        reconnect: bool = False,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        """
        Connects this player to the voice channel.

        This method is usually not called manually, but automatically called by ``discord.py``.
        """
        await self._lifecycle_handler.connect(
            timeout=timeout,
            reconnect=reconnect,
            self_deaf=self_deaf,
            self_mute=self_mute,
        )

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Disconnects the player, destroys it on the Lavalink node, and cleans up state.

        This method handles the unregistration of the player from the :class:`Node`
        and sends a destruction request to the Lavalink server.

        Parameters
        ----------
        force: :class:`bool`
            Whether to force the disconnection even if the player is not currently connected.
            Defaults to ``False``.
        """
        await self._lifecycle_handler.disconnect(force=force)

    async def move_to(self, node: Node, /) -> None:
        """
        Moves this player to a different Lavalink node seamlessly.

        This method handles the migration of the player state, filters,
        and voice connection to the new node.

        Parameters
        ----------
        node: :class:`Node`
            The destination node to move this player to.
        """

        await self._lifecycle_handler.move_to(node)

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
        Plays the specified track on this player.

        Parameters
        ----------
        playable: :class:`Playable` | :class:`str`
            The track to play. Can be a Playable object or a base64 encoded track string.
        start: :class:`int`
            The position in milliseconds to start playback at. Defaults to 0.
        end: :class:`int` | :data:`None`
            The position in milliseconds to end playback at. Defaults to None.
        volume: :class:`int` | :data:`None`
            The volume to set for this playback. Defaults to the current player volume.
        paused: :class:`bool` | :data:`None`
            Whether to start the track in a paused state. Defaults to the current player state.
        add_to_history: :class:`bool`
            Whether to add the currently playing track to the history before playing the new track.

            Defaults to ``True``.

        Returns
        -------
        :class:`Playable`
            The track that was requested for playback.
        """
        return await self._playback_handler.play(
            track,
            start=start,
            end=end,
            volume=volume,
            paused=paused,
        )

    async def stop(
        self,
        /,
        *,
        clear_queue: bool = False,
        clear_history: bool = False,
    ) -> None:
        """
        Stops the current track and clears the player state.

        This method sends a request to Lavalink to stop playback and resets
        the internal position tracking, current track, and queue state.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        """
        await self._playback_handler.stop(
            clear_queue=clear_queue,
            clear_history=clear_history,
        )

    async def pause(self, value: bool = True, /) -> None:
        """
        Sets the pause state of the player.

        Parameters
        ----------
        value: :class:`bool`
            Whether to pause (True) or resume (False) the player.
        """
        await self._playback_handler.pause(value)

    async def resume(self) -> None:
        """Resumes the player if it is paused. Alias for ``pause(False)``."""
        await self._playback_handler.resume()

    async def previous(self) -> Playable:
        """
        Returns to the previous track in the history.

        This retrieves the most recently played track from the history,
        pushes the current track back to the front of the queue,
        and begins playback of the historical track.

        Returns
        -------
        :class:`Playable`
            The previous track from history which is now playing.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        HistoryEmpty
            There is no previous track in the history to return to.
        """

        return await self._playback_handler.previous()

    async def skip(self) -> Playable | None:
        """
        Skips to the next track in the queue.

        Returns
        -------
        :class:`Playable` | None
            The next track from the queue or history which is now playing,
            or None if the player stopped and autoplay is empty.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        QueueEmpty
            The queue is empty and there is no track to skip to.
        """
        return await self._playback_handler.skip()

    async def seek(self, position: int, /) -> None:
        """
        Seeks to a specific position in the current track.

        Parameters
        ----------
        position: :class:`int`
            The position to seek to in milliseconds.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        """

        await self._playback_handler.seek(position)

    async def set_volume(self, value: int, /) -> None:
        """
        Sets the player's volume.

        Parameters
        ----------
        value: :class:`int`
            The volume to set. Must be between 0 and 1000.

        Raises
        ------
        ValueError
            The volume provided was not between 0 and 1000.
        RuntimeError
            The player is not currently connected to a node or session.
        """
        await self._playback_handler.set_volume(value)

    async def set_filters(
        self,
        filters: PlayerFilters,
        /,
        *,
        seek: bool = False,
    ) -> None:
        """
        Sets the filters for this player.

        Parameters
        ----------
        filters: :class:`PlayerFilters`
            The filters to apply.
        seek: :class:`bool`
            Whether to seek to the current position to apply filters immediately.
            Defaults to ``False``.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        """

        await self._playback_handler.set_filters(filters, seek=seek)

    async def on_voice_server_update(self, data: VoiceServerUpdate) -> None:
        """
        Processes the ``VOICE_SERVER_UPDATE`` payload from Discord.

        This provides the voice token and the endpoint needed for Lavalink
        to connect to the voice server.

        Parameters
        ----------
        data: :class:`discord.types.voice.VoiceServerUpdate`
            The raw payload data received from the Discord Gateway.
        """
        await self._events_handler.on_voice_server_update(data)

    async def on_voice_state_update(self, data: GuildVoiceState) -> None:
        """
        Processes the ``VOICE_STATE_UPDATE`` payload from Discord.

        This provides the session ID and channel ID needed for the
        voice connection handshake.

        Parameters
        ----------
        data: :class:`discord.types.voice.GuildVoiceState`
            The raw payload data received from the Discord Gateway.
        """
        await self._events_handler.on_voice_state_update(data)

    def _ensure_node(self) -> Node:
        if self._node:
            return self._node

        if self.client is MISSING:
            raise RuntimeError("Cannot ensure Node without a Client.")

        rl_client = _registry.clients.get(self.client)

        if rl_client is None:
            raise RuntimeError(f"No relink.Client is associated with {self.client!r}.")

        self._node = rl_client.get_best_node()
        if self.guild.id not in self._node._players:
            self._node._add_player(self)
        return self._node

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
