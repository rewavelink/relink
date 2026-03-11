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
from typing import TYPE_CHECKING, Annotated, Self, overload

import discord
from discord.types.voice import GuildVoiceState, VoiceServerUpdate

from relink.rest.schemas.filters import PlayerFilters
from relink.rest.schemas.player import (
    PlayerVoiceState,
    UpdatePlayerRequest,
    UpdatePlayerTrackRequest,
)

from ..models.track import Playable
from .enums import QueueMode
from .queue.queue import Queue
from .schemas.receive import PlayerState

if TYPE_CHECKING:
    from .node import Node

_log = logging.getLogger(__name__)
MISSING = discord.utils.MISSING


class PlayerConnectionState:
    """
    Represents the voice connection state for a :class:`Player`.

    This class is intended to be subclassed if you need to store
    extra metadata during the Discord handshake.
    """

    __slots__ = ("token", "endpoint", "session_id", "channel_id")

    def __init__(self) -> None:
        self.token: str | None = None
        self.endpoint: str | None = None
        self.session_id: str | None = None
        self.channel_id: str | None = None

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
        to fetch an available node from the :class:`NodePool` during the connection process.

    Attributes
    ----------
    guild_id: :class:`int`
        The ID of the guild this player is connected to.
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
        "guild_id",
        "_connection",
        "_filters",
        "_last_position",
        "_last_update",
        "_node",
        "_paused",
        "_queue",
        "_ready",
        "_volume",
    )

    guild_id: int
    _connection: PlayerConnectionState
    _filters: PlayerFilters
    _last_position: Annotated[int, "ms"]
    _last_update: Annotated[float, "time.monotonic"]
    _node: Node | None
    _paused: bool
    _queue: Queue
    _ready: bool
    _volume: int

    def __repr__(self) -> str:
        return (
            f"<Player guild_id={self.guild_id} ready={self._ready} node={self._node!r}>"
        )

    @overload
    def __init__(self, *, node: Node) -> None: ...

    @overload
    def __init__(
        self,
        client: discord.Client,
        channel: discord.VoiceChannel | discord.StageChannel,
    ) -> None: ...

    def __init__(
        self,
        client: discord.Client = MISSING,
        channel: discord.VoiceChannel | discord.StageChannel = MISSING,
        *,
        node: Node | None = None,
    ) -> None:
        self.guild_id = 0
        self._node = node
        self._connection = self.get_connection_state()

        self._filters = PlayerFilters()
        self._queue: Queue = Queue()
        self._paused = False
        self._volume = 100

        self._last_position = 0
        self._last_update = 0.0

        if client is not MISSING and channel is not MISSING:
            self.guild_id = channel.guild.id
            self._ready = True
        else:
            self._ready = False

    def __call__(
        self,
        client: discord.Client,
        channel: discord.VoiceChannel | discord.StageChannel,
    ) -> Self:
        super().__init__(client, channel)

        self.guild_id = channel.guild.id

        if self._node:
            self._node._add_player(self)

        return self

    @property
    def current(self) -> Playable | None:
        """The currently playing track, or None if nothing is playing."""
        return self._queue.current_track

    @property
    def filters(self) -> PlayerFilters:
        """The currently applied filters for this player."""
        return self._filters

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
            raise RuntimeError(f"Player {self.guild_id} is not attached to a node.")
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
        try:
            if self._node is None:
                return

            self._node._remove_player(self.guild_id)

            if self._node._resume_session is None:
                return

            await self._node._manager.destroy_player(
                session_id=self._node._resume_session, guild_id=str(self.guild_id)
            )

            _log.info(
                "Player %s: Disconnected and removed from Node %r.",
                self.guild_id,
                self._node.id,
            )

        except Exception as exc:
            _log.warning(
                "Player %s: Error during disconnect cleanup: %s",
                self.guild_id,
                exc,
                exc_info=True,
            )

        finally:
            self._queue.reset()
            await super().disconnect(force=force)

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

        if self._node is node:
            return

        old_node = self._node
        self._node = node

        if old_node:
            old_node._remove_player(self.guild_id)
        node._add_player(self)

        await self._dispatch_voice_update()
        assert node._resume_session is not None

        track_payload = (
            UpdatePlayerTrackRequest(encoded=self.current.encoded)
            if self.current
            else None
        )
        data = UpdatePlayerRequest(
            track=track_payload,
            position=self.position,
            volume=self._volume,
            paused=self._paused,
            filters=self._filters,
        )

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        if old_node and old_node._resume_session:
            try:
                await old_node._manager.destroy_player(
                    session_id=old_node._resume_session, guild_id=str(self.guild_id)
                )
            except Exception as exc:
                _log.warning(
                    "Player %s: Failed to destroy player on old node during migration. Error: %s",
                    self.guild_id,
                    exc,
                    exc_info=True,
                )

        _log.info(
            "Player %s: Successfully migrated to Node %r.",
            self.guild_id,
            node.id,
        )

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
        node = self.node
        assert node._resume_session is not None

        volume = volume if volume is not None else self._volume
        paused = paused if paused is not None else self._paused

        track_payload = UpdatePlayerTrackRequest(encoded=track.encoded)
        data = UpdatePlayerRequest(
            track=track_payload,
            position=start,
            endtime=end,
            volume=volume,
            paused=paused,
        )

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        self._volume = volume
        self._paused = paused
        self._last_position = start
        self._last_update = time.monotonic()
        self._queue.current_track = track

        self._stop_inactivity_timer()
        return track

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
        node = self.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(track=None)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        self._last_position = 0
        self._last_update = 0.0
        self._queue.current_track = None

        if clear_queue:
            self._queue.clear()
            self._queue.mode = QueueMode.NORMAL

        if clear_history:
            self._queue.clear_history()

        _log.debug("Player %s: Stopped playback and reset state.", self.guild_id)
        self._check_inactivity()

    async def pause(self, value: bool = True, /) -> None:
        """
        Sets the pause state of the player.

        Parameters
        ----------
        value: :class:`bool`
            Whether to pause (True) or resume (False) the player.
        """
        node = self.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(paused=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        self._paused = value
        _log.debug("Player %s: Set paused state to %s", self.guild_id, value)

    async def resume(self) -> None:
        """Resumes the player if it is paused. Alias for ``pause(False)``."""
        await self.pause(False)

    async def previous(self) -> None:
        """
        Returns to the previous track in the history.

        This retrieves the most recently played track from the history,
        pushes the current track back to the front of the queue,
        and begins playback of the historical track.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        HistoryEmpty
            There is no previous track in the history to return to.
        """

        track = self._queue.previous()
        await self.play(track)

    async def skip(self) -> None:
        """
        Skips to the next track in the queue.

        Raises
        ------
        RuntimeError
            The player is not connected to a node or session.
        QueueEmpty
            The queue is empty and there is no track to skip to.
        """
        next_track = self._queue.get()
        await self.play(next_track)

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

        node = self.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(position=position)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        self._last_position = position
        self._last_update = time.monotonic()

        _log.debug("Player %s: Seeked to %dms", self.guild_id, position)

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
        if not 0 <= value <= 1000:
            raise ValueError("Volume must be between 0 and 1000.")

        node = self.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(volume=value)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        self._volume = value
        _log.debug("Player %s: Set volume to %d.", self.guild_id, value)

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

        node = self.node
        assert node._resume_session is not None

        data = UpdatePlayerRequest(filters=filters)

        await node._manager.update_player(
            session_id=node._resume_session,
            guild_id=str(self.guild_id),
            data=data,
        )

        self._filters = filters

        if seek:
            await self.seek(self.position)

        _log.debug(
            "Player %s: Successfully applied filters: %r",
            self.guild_id,
            filters,
        )

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
        self._connection.token = data.get("token")
        self._connection.endpoint = data.get("endpoint")

        # The endpoint might be None; Lavalink needs a string or it will fail.
        # Thus we wait for a non-None endpoint before dispatching.
        if self._connection.endpoint:
            await self._dispatch_voice_update()

    def _update_state(self, state: PlayerState, /) -> None:
        self._last_position = state.position
        self._last_update = time.monotonic()

        _log.debug(
            "Player %s: Synced position to %dms (connected %s)",
            self.guild_id,
            state.position,
            state.connected,
        )

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
        self._connection.session_id = data.get("session_id")
        self._connection.channel_id = str(data.get("channel_id"))

        await self._dispatch_voice_update()
        self._check_inactivity()

    async def _dispatch_voice_update(self) -> None:
        if not self._connection.is_complete or not self._node:
            return

        assert self._connection.token is not None
        assert self._connection.endpoint is not None
        assert self._connection.session_id is not None
        assert self._node._resume_session is not None

        voice_state = PlayerVoiceState(
            token=self._connection.token,
            endpoint=self._connection.endpoint,
            session_id=self._connection.session_id,
        )

        request_data = UpdatePlayerRequest(voice=voice_state)

        try:
            await self._node._manager.update_player(
                session_id=self._node._resume_session,
                guild_id=str(self.guild_id),
                data=request_data,
            )
            _log.debug(
                "Player %s: Successfully dispatched voice update to Node %r.",
                self.guild_id,
                self._node.id,
            )
        except Exception as exc:
            _log.error(
                "Player %s: Failed to dispatch voice update to Node %r. Error: %s",
                self.guild_id,
                self._node.id,
                exc,
                exc_info=True,
            )

    def _check_inactivity(self) -> None:
        guild = self.client.get_guild(self.guild_id)

        if guild is None or guild.me.voice is None:
            return

        channel = guild.me.voice.channel
        if not channel:
            return

        members = [member for member in channel.members if not member.bot]

        is_alone = len(members) == 0
        is_idle = self.current is None

        if is_alone or is_idle:
            self._start_inactivity_timer()
        else:
            self._stop_inactivity_timer()

    def _start_inactivity_timer(self) -> None:
        node = self._node

        if node is None or self.guild_id in node._waiting_to_disconnect:
            return

        timeout = node._inactive_player_timeout
        if timeout is None:
            return

        task = asyncio.create_task(self._inactivity_timeout(timeout))
        task.add_done_callback(
            lambda _: node._waiting_to_disconnect.pop(self.guild_id, None)
        )
        node._waiting_to_disconnect[self.guild_id] = task
        _log.debug("Player %s: Started inactivity timer (%ds).", self.guild_id, timeout)

    def _stop_inactivity_timer(self) -> None:
        if self._node is None:
            return

        task = self._node._waiting_to_disconnect.pop(self.guild_id, None)

        if task is None:
            return

        task.cancel()
        _log.debug("Player %s: Activity detected, cancelled timer.", self.guild_id)

    async def _inactivity_timeout(self, timeout: int) -> None:
        await asyncio.sleep(timeout)
        _log.info("Player %s: Disconnecting due to inactivity.", self.guild_id)
        await self.disconnect()
