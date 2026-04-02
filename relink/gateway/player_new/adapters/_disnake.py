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

import logging
from typing import TYPE_CHECKING, Self, overload

import disnake
from disnake.types.voice import GuildVoiceState
from disnake.types.gateway import VoiceServerUpdateEvent

from relink import _registry
from relink.gateway.enums import AutoPlayMode, QueueMode
from relink.models.filters import Filters
from relink.models.track import Playable

from .._base import BasePlayer

if TYPE_CHECKING:
    from relink.gateway.node import Node
    from relink.gateway.queue.queue import Queue
    from relink.models.settings import AutoPlaySettings, HistorySettings

_log = logging.getLogger(__name__)
MISSING = disnake.utils.MISSING


__all__ = ("DisnakePlayer",)


class DisnakePlayer(BasePlayer, disnake.VoiceProtocol):
    """
    A disnake implementation of :class:`~relink.player.base_player.BasePlayer`.

    This class satisfies the :class:`disnake.VoiceProtocol` contract expected
    by disnake's voice connection machinery, whilst delegating all Lavalink
    playback logic to the handlers initialised by :class:`BasePlayer`.

    There are two primary ways to create a player:

    1. **Class-pass** — pass the class itself to
       :meth:`disnake.abc.Connectable.connect`. disnake will instantiate it
       by calling ``Player(client, channel)``::

           player = await voice_channel.connect(cls=Player)

    2. **Instance-pass** — construct a pre-configured instance and pass it
       instead. disnake will call ``player(client, channel)`` which hits
       :meth:`__call__`::

           player = Player(node=some_node, volume=80)
           await voice_channel.connect(cls=player)

    Parameters
    ----------
    node : :class:`~relink.node.Node` | None
        The Lavalink node to associate with this player. If ``None``, an
        available node is resolved from the client's node pool at connection
        time.
    queue_mode : :class:`~relink.enums.QueueMode`
        The initial queue looping mode. Defaults to ``QueueMode.NORMAL``.
    autoplay_settings : :class:`~relink.models.settings.AutoPlaySettings` | None
        AutoPlay configuration. ``None`` uses the default configuration.
    history_settings : :class:`~relink.models.settings.HistorySettings` | None
        History configuration. ``None`` uses the default configuration.
        History must be enabled when AutoPlay is active.
    volume : :class:`int` | None
        Initial volume in the range ``0``–``1000``. Defaults to ``100``.
    paused : :class:`bool` | None
        Whether the player should start in a paused state. Defaults to
        ``False``.
    filters : :class:`~relink.models.filters.Filters` | None
        Initial audio filters. Defaults to an empty
        :class:`~relink.models.filters.Filters` instance.

    Attributes
    ----------
    guild : :class:`disnake.Guild`
        The guild this player is attached to.
    channel : :class:`disnake.VoiceChannel` | :class:`disnake.StageChannel`
        The voice channel this player is currently connected to.
    client : :class:`disnake.Client`
        The disnake client driving this player.
    """

    channel: disnake.abc.Connectable
    client: disnake.Client

    _guild: disnake.Guild | None

    @overload
    def __init__(
        self,
        *,
        node: Node | None = ...,
        queue_mode: QueueMode = ...,
        autoplay_settings: AutoPlaySettings | None = ...,
        history_settings: HistorySettings | None = ...,
        volume: int | None = ...,
        paused: bool | None = ...,
        filters: Filters | None = ...,
    ) -> None: ...

    @overload
    def __init__(
        self,
        client: disnake.Client,
        channel: disnake.abc.Connectable,
    ) -> None: ...

    def __init__(
        self,
        client: disnake.Client = MISSING,
        channel: disnake.abc.Connectable = MISSING,
        *,
        node: Node | None = None,
        queue_mode: QueueMode = QueueMode.NORMAL,
        autoplay_settings: AutoPlaySettings | None = None,
        history_settings: HistorySettings | None = None,
        volume: int | None = None,
        paused: bool | None = None,
        filters: Filters | None = None,
    ) -> None:
        super().__init__(
            node=node,
            queue_mode=queue_mode,
            autoplay_settings=autoplay_settings,
            history_settings=history_settings,
            volume=volume,
            paused=paused,
            filters=filters,
        )

        self._guild = None

        if client is not MISSING and channel is not MISSING:
            disnake.VoiceProtocol.__init__(self, client=client, channel=channel)
            if isinstance(channel, disnake.abc.GuildChannel):
                self._guild = channel.guild
            self._ready = True

    def __call__(
        self,
        client: disnake.Client,
        channel: disnake.abc.Connectable,
    ) -> Self:
        """
        Called by disnake when a pre-configured **instance** is passed to
        :meth:`disnake.abc.Connectable.connect`.

        Binds the disnake ``VoiceProtocol`` attributes, resolves the guild
        from the channel, and registers the player with its node.

        Parameters
        ----------
        client : :class:`disnake.Client`
            The disnake client instance.
        channel : :class:`disnake.abc.Connectable`
            The voice channel being connected to.

        Returns
        -------
        :class:`DisnakePlayer`
            This player instance, fully initialised.
        """
        disnake.VoiceProtocol.__init__(self, client=client, channel=channel)

        if isinstance(channel, (disnake.VoiceChannel, disnake.StageChannel)):
            self._guild = channel.guild

        self._ensure_node()
        return self

    @property
    def autoplay(self) -> AutoPlayMode:
        """The current :class:`~relink.enums.AutoPlayMode` for this player."""
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
        """The currently playing track, or ``None`` if the player is idle."""
        return self._queue.current_track

    @property
    def filters(self) -> Filters:
        """The :class:`~relink.models.filters.Filters` currently applied to this player."""
        return self._filters

    @property
    def guild(self) -> disnake.Guild:
        """
        The :class:`disnake.Guild` this player is associated with.

        Raises
        ------
        RuntimeError
            If the player has not yet been attached to a guild.
        """
        if self._guild is None:
            raise RuntimeError("Player is not yet attached to a guild.")
        return self._guild

    @property
    def node(self) -> Node:
        """
        The :class:`~relink.node.Node` this player is currently attached to.

        Raises
        ------
        RuntimeError
            If the player is not attached to a node.
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
        """
        The estimated current playback position in milliseconds.

        Interpolated from the last state update received from the Lavalink
        node. Returns the last known position when paused or not yet started.
        """
        import time

        if self._paused or self._last_update == 0:
            return self._last_position

        delta = int((time.monotonic() - self._last_update) * 1000)
        return self._last_position + delta

    @property
    def queue(self) -> Queue:
        """The :class:`~relink.queue.queue.Queue` associated with this player."""
        return self._queue

    @property
    def volume(self) -> int:
        """The current volume of the player as an integer between ``0`` and ``1000``."""
        return self._volume

    async def connect(
        self,
        *,
        timeout: float = 10.0,
        reconnect: bool = False,
        self_deaf: bool = False,
        self_mute: bool = False,
    ) -> None:
        """
        Connect this player to its assigned voice channel.

        Called automatically by disnake after the player is instantiated.
        Manual invocation is not normally required.

        Parameters
        ----------
        timeout : :class:`float`
            Seconds to wait for the Discord gateway handshake before raising.
            Defaults to ``10.0``.
        reconnect : :class:`bool`
            Whether to attempt reconnection on failure. Defaults to ``False``.
        self_deaf : :class:`bool`
            Whether to join the channel self-deafened. Defaults to ``False``.
        self_mute : :class:`bool`
            Whether to join the channel self-muted. Defaults to ``False``.
        """
        await self._lifecycle_handler.connect(
            timeout=timeout,
            reconnect=reconnect,
            self_deaf=self_deaf,
            self_mute=self_mute,
        )

    async def disconnect(self, *, force: bool = False) -> None:
        """
        Disconnect this player, destroy it on the Lavalink node, and clean up
        all internal state.

        Parameters
        ----------
        force : :class:`bool`
            If ``True``, proceeds even if the player is not currently connected.
            Defaults to ``False``.
        """
        await self._lifecycle_handler.disconnect(force=force)

    async def move_to(self, node: Node, /) -> None:
        """
        Migrate this player to a different Lavalink node without interrupting
        playback.

        Parameters
        ----------
        node : :class:`~relink.node.Node`
            The destination node.
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
        Begin playback of the specified track.

        Parameters
        ----------
        track : :class:`~relink.models.track.Playable`
            The track to play.
        start : :class:`int`
            Start position in milliseconds. Defaults to ``0``.
        end : :class:`int` | None
            End position in milliseconds. ``None`` plays to completion.
        volume : :class:`int` | None
            Per-track volume override. ``None`` uses the current player volume.
        paused : :class:`bool` | None
            Start in a paused state. ``None`` preserves the current pause state.

        Returns
        -------
        :class:`~relink.models.track.Playable`
            The track dispatched to the Lavalink node.
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
        Stop the currently playing track.

        Parameters
        ----------
        clear_queue : :class:`bool`
            Remove all pending tracks from the queue. Defaults to ``False``.
        clear_history : :class:`bool`
            Clear the playback history. Defaults to ``False``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.stop(
            clear_queue=clear_queue,
            clear_history=clear_history,
        )

    async def pause(self, value: bool = True, /) -> None:
        """
        Set the pause state of the player.

        Parameters
        ----------
        value : :class:`bool`
            ``True`` to pause, ``False`` to resume. Defaults to ``True``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.pause(value)

    async def resume(self) -> None:
        """
        Resume playback if the player is currently paused.

        Alias for ``await player.pause(False)``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.resume()

    async def skip(self) -> Playable | None:
        """
        Skip the currently playing track and advance to the next one in the
        queue.

        Returns
        -------
        :class:`~relink.models.track.Playable` | None
            The track now playing, or ``None`` if the player stopped.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        QueueEmpty
            If the queue is empty and AutoPlay yields no results.
        """
        return await self._playback_handler.skip()

    async def previous(self) -> Playable:
        """
        Return to the most recently played track in the history.

        Returns
        -------
        :class:`~relink.models.track.Playable`
            The historical track now playing.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        HistoryEmpty
            If there is no previous track in the history.
        """
        return await self._playback_handler.previous()

    async def seek(self, position: int, /) -> None:
        """
        Seek to a position within the current track.

        Parameters
        ----------
        position : :class:`int`
            Target position in milliseconds.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.seek(position)

    async def set_volume(self, value: int, /) -> None:
        """
        Set the player's output volume.

        Parameters
        ----------
        value : :class:`int`
            Volume level in the range ``0``–``1000``.

        Raises
        ------
        ValueError
            If ``value`` is outside the range ``0``–``1000``.
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.set_volume(value)

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
            The filters to apply.
        seek : :class:`bool`
            If ``True``, seek to the current position immediately after
            applying filters to force the new chain to take effect without
            an audible delay. Defaults to ``False``.

        Raises
        ------
        RuntimeError
            If the player is not connected to a node or an active session.
        """
        await self._playback_handler.set_filters(filters.payload, seek=seek)

    async def on_voice_server_update(self, data: VoiceServerUpdateEvent) -> None:
        """
        Handle a ``VOICE_SERVER_UPDATE`` payload from the Discord gateway.

        Provides the voice server token and endpoint to the Lavalink node so
        it can establish or re-establish the audio stream.

        Parameters
        ----------
        data : :class:`disnake.types.voice.VoiceServerUpdate`
            The raw payload received from the Discord gateway.
        """
        await self._events_handler.on_voice_server_update(data)

    async def on_voice_state_update(self, data: GuildVoiceState) -> None:
        """
        Handle a ``VOICE_STATE_UPDATE`` payload from the Discord gateway.

        Provides the session ID and channel ID required for the voice
        connection handshake with the Lavalink node.

        Parameters
        ----------
        data : :class:`disnake.types.voice.GuildVoiceState`
            The raw payload received from the Discord gateway.
        """
        await self._events_handler.on_voice_state_update(data)

    def _ensure_node(self) -> Node:
        node = self._node

        if node is None:
            if self.client is MISSING:
                raise RuntimeError("Cannot ensure Node without a Client.")

            rl_client = _registry.clients.get(self.client)
            if rl_client is None:
                raise RuntimeError(
                    f"No relink.Client is associated with {self.client!r}"
                )

            node = rl_client.get_best_node()
            self._node = node

        if self.guild.id not in node._players:
            node._add_player(self)

        return node
