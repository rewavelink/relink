.. currentmodule:: sonolink

Events
======

Track
-----

Track Start
+++++++++++

.. function:: on_sonolink_track_start(player: sonolink.Player, payload: sonolink.gateway.TrackStartEvent)

   Called when a track starts playing.

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player that is playing the track.
   payload: :class:`sonolink.gateway.TrackStartEvent`
       The event payload containing information about the track that started playing.

.. autoclass:: sonolink.gateway.TrackStartEvent()

Track End
+++++++++

.. function:: on_sonolink_track_end(player: sonolink.Player, payload: sonolink.gateway.TrackEndEvent)

   Called when a track ends.

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player that was playing the track.
   payload: :class:`sonolink.gateway.TrackEndEvent`
       The event payload containing information about the track that finished playing and the reason it ended.

.. autoclass:: sonolink.gateway.TrackEndEvent()

Track Exception
+++++++++++++++

.. function:: on_sonolink_track_exception(player: sonolink.Player, payload: sonolink.gateway.TrackExceptionEvent)

   Called when an exception occurs while playing a track.

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player that was playing the track.
   payload: :class:`sonolink.gateway.TrackExceptionEvent`
       The event payload containing information about the track that caused the exception and the exception.

.. autoclass:: sonolink.gateway.TrackExceptionEvent()

Track Stuck
+++++++++++

.. function:: on_sonolink_track_stuck(player: sonolink.Player, payload: sonolink.gateway.TrackStuckEvent)

   Called when a track gets stuck while playing.

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player that was playing the track.
   payload: :class:`sonolink.gateway.TrackStuckEvent`
       The event payload containing information about the track that got stuck and the threshold that was exceeded.

.. autoclass:: sonolink.gateway.TrackStuckEvent()

Node
----

Node Ready
++++++++++

.. function:: on_sonolink_node_ready(payload: sonolink.gateway.ReadyEvent)

   Called when a node is ready.

   Parameters
   ----------
   payload: :class:`sonolink.gateway.ReadyEvent`
       The event payload containing information about the node that is ready.

.. autoclass:: sonolink.gateway.ReadyEvent()

Node Close
++++++++++

.. function:: on_sonolink_node_close(node: sonolink.Node)

   Called when a node is closed.

   Parameters
   ----------
   node: :class:`sonolink.Node`
       The node that was closed.

Node Stats
++++++++++

.. function:: on_sonolink_stats_receive(node: sonolink.Node, payload: sonolink.gateway.StatsEvent)

   Called when the node receives ``stats`` OP from Lavalink.

   .. versionadded:: 1.1.0

   Parameters
   ----------
   node: :class:`sonolink.Node`
       The node that sent the statistics.
   payload: :class:`sonolink.gateway.StatsEvent`
       The event payload containing information about the node's resource usage,
       player counts, and uptime.

.. autoclass:: sonolink.gateway.StatsEvent()

Player
------

Player Update
+++++++++++++

.. function:: on_sonolink_player_update(player: sonolink.Player, payload: sonolink.gateway.PlayerUpdateEvent)

   Called when a player is updated.

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player that was updated.
   payload: :class:`sonolink.gateway.PlayerUpdateEvent`
       The event payload containing information about the player's current state.

.. autoclass:: sonolink.gateway.PlayerUpdateEvent()

WebSocket Closed
++++++++++++++++

.. function:: on_sonolink_websocket_closed(player: sonolink.Player, payload: sonolink.gateway.WebSocketClosedEvent)

   Called when the voice WebSocket connection to Lavalink is closed.

   .. versionadded:: 1.1.0

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player whose voice WebSocket was closed.
   payload: :class:`sonolink.gateway.WebSocketClosedEvent`
       The event payload containing the close code, reason, and whether the
       close was initiated by the remote end.

.. autoclass:: sonolink.gateway.WebSocketClosedEvent()

Miscellaneous
-------------

Unknown Event
+++++++++++++

.. function:: on_sonolink_unknown_event(player: sonolink.Player, payload: dict[str, Any])

   Called when an unknown event is received. This can be from plugins/extensions on Lavalink.

   Parameters
   ----------
   player: :class:`sonolink.Player`
       The player that received the unknown event.
   payload: :class:`dict`
       The raw event payload that was received.
