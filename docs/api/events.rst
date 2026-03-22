.. currentmodule:: relink

Events
======

Track
-----

Track Start
+++++++++++

.. function:: on_relink_track_start(player: relink.Player, payload: relink.gateway.TrackStartEvent)

   Called when a track starts playing.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that is playing the track.
   payload: :class:`relink.gateway.TrackStartEvent`
       The event payload containing information about the track that started playing.

.. autoclass:: relink.gateway.TrackStartEvent()

Track End
+++++++++

.. function:: on_relink_track_end(player: relink.Player, payload: relink.gateway.TrackEndEvent)

   Called when a track ends.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was playing the track.
   payload: :class:`relink.gateway.TrackEndEvent`
       The event payload containing information about the track that finished playing and the reason it ended.

.. autoclass:: relink.gateway.TrackEndEvent()

Track Exception
+++++++++++++++

.. function:: on_relink_track_exception(player: relink.Player, payload: relink.gateway.TrackExceptionEvent)

   Called when an exception occurs while playing a track.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was playing the track.
   payload: :class:`relink.gateway.TrackExceptionEvent`
       The event payload containing information about the track that caused the exception and the exception.

.. autoclass:: relink.gateway.TrackExceptionEvent()

Track Stuck
+++++++++++

.. function:: on_relink_track_stuck(player: relink.Player, payload: relink.gateway.TrackStuckEvent)

   Called when a track gets stuck while playing.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was playing the track.
   payload: :class:`relink.gateway.TrackStuckEvent`
       The event payload containing information about the track that got stuck and the threshold that was exceeded.

.. autoclass:: relink.gateway.TrackStuckEvent()

Node
----

Node Ready
++++++++++

.. function:: on_relink_node_ready(payload: relink.gateway.ReadyEvent)

   Called when a node is ready.

   Parameters
   ----------
   payload: :class:`relink.gateway.ReadyEvent`
       The event payload containing information about the node that is ready.

.. autoclass:: relink.gateway.ReadyEvent()

Node Close
++++++++++

.. function:: on_relink_node_close(node: relink.Node)

   Called when a node is closed.

   Parameters
   ----------
   node: :class:`relink.Node`
       The node that was closed.

Player
------

Player Update
+++++++++++++

.. function:: on_relink_player_update(player: relink.Player, payload: relink.gateway.PlayerUpdateEvent)

   Called when a player is updated.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was updated.
   payload: :class:`relink.gateway.PlayerUpdateEvent`
       The event payload containing information about the player's current state.

.. autoclass:: relink.gateway.PlayerUpdateEvent()

Miscellaneous
-------------

Unknown Event
+++++++++++++

.. function:: on_relink_unknown_event(player: relink.Player, payload: dict[str, Any])

   Called when an unknown event is received. This can be from plugins/extensions on Lavalink.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that received the unknown event.
   payload: :class:`dict`
       The raw event payload that was received.
