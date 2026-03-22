Events
======

Track
------

Track Start
+++++++++++

.. function:: on_relink_track_start(player: relink.Player, payload: TrackStartEvent)

   Called when a track starts playing.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that is playing the track.
   payload: :class:`TrackStartEvent`
       The event payload containing information about the track that started playing.

.. autoclass:: relink.gateway.schemas.TrackStartEvent()

Track End
++++++++++

.. function:: on_relink_track_end(player: relink.Player, payload: TrackEndEvent)

   Called when a track ends.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was playing the track.
   payload: :class:`TrackEndEvent`
       The event payload containing information about the track that finished playing and the reason it ended.

.. autoclass:: relink.gateway.schemas.TrackEndEvent()

Track Exception
++++++++++++++++

.. function:: on_relink_track_exception(player: relink.Player, payload: TrackExceptionEvent)

   Called when an exception occurs while playing a track.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was playing the track.
   payload: :class:`TrackExceptionEvent`
       The event payload containing information about the track that caused the exception and the exception.


.. autoclass:: relink.gateway.schemas.TrackExceptionEvent()

Track Stuck
++++++++++++

.. function:: on_relink_track_stuck(player: relink.Player, payload: TrackStuckEvent)

   Called when a track gets stuck while playing.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was playing the track.
   payload: :class:`TrackStuckEvent`
       The event payload containing information about the track that got stuck and the threshold that was exceeded.

.. autoclass:: relink.gateway.schemas.TrackStuckEvent()

Node
-----

Node Close
+++++++++++

.. function:: on_relink_node_close(node: relink.Node)
    
   Called when a node is closed.

   Parameters
   ----------
   node: :class:`relink.Node`
       The node that was closed.

Node Ready
+++++++++++

.. function:: on_relink_node_ready(payload: ReadyEvent)

   Called when a node is ready.

   Parameters
   ----------
   payload: :class:`ReadyEvent`
       The event payload containing information about the node that is ready.


.. autoclass:: relink.gateway.schemas.ReadyEvent()

Player
------

Player Update
++++++++++++++

.. function:: on_relink_player_update(player: relink.Player, payload: PlayerUpdateEvent)

   Called when a player is updated.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that was updated.
   payload: :class:`PlayerUpdateEvent`
       The event payload containing information about the player's current state.

.. autoclass:: relink.gateway.schemas.PlayerUpdateEvent()

Miscellaneous
--------------

Unknown Event
+++++++++++++++

.. function:: on_relink_unknown_event(player: relink.Player, payload: dict[str, Any])

   Called when an unknown event is received. This can be from plugins/extensions on lavalink etc.

   Parameters
   ----------
   player: :class:`relink.Player`
       The player that received the unknown event.
   payload: dict[str, Any]
       The raw event payload that was received.
