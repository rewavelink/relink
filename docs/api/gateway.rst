.. currentmodule:: relink

Gateway API
===========


The gateway layer contains the queue, enum, error, and event-related runtime types.
The top-level :class:`relink.Client`, :class:`relink.Node`, and :class:`relink.Player`
classes are documented on :doc:`core`.

Voice state
-----------

.. autoclass:: relink.PlayerConnectionState
   :members:
   


   

Playback event payloads
-----------------------

.. autoclass:: relink.gateway.schemas.TrackStartEvent
   :members:
   

.. autoclass:: relink.gateway.schemas.TrackEndEvent
   :members:
   

.. autoclass:: relink.gateway.schemas.TrackException
   :members:
   

.. autoclass:: relink.gateway.schemas.TrackExceptionEvent
   :members:
   

.. autoclass:: relink.gateway.schemas.TrackStuckEvent
   :members:
   

Websocket payloads
------------------

.. autoclass:: relink.gateway.schemas.ReadyEvent
   :members:
   

.. autoclass:: relink.gateway.schemas.PlayerState
   :members:
   

.. autoclass:: relink.gateway.schemas.PlayerUpdateEvent
   :members:
   

.. autoclass:: relink.gateway.schemas.MemoryStats
   :members:
   

.. autoclass:: relink.gateway.schemas.CPUStats
   :members:
   

.. autoclass:: relink.gateway.schemas.FrameStats
   :members:
   

.. autoclass:: relink.gateway.schemas.StatsEvent
   :members:
   

.. autoclass:: relink.gateway.schemas.WebSocketClosedEvent
   :members:
   



Gateway Events API
------------------

Router
++++++

.. autoclass:: relink.gateway.events.router.EventRouter
   :members:
   
Event wrappers
++++++++++++++++

.. autoclass:: relink.gateway.events.raw_models.ReadyEvent
   :members:
   

.. autoclass:: relink.gateway.events.raw_models.PlayerUpdateEvent
   :members:
   

.. autoclass:: relink.gateway.events.raw_models.StatsEvent
   :members:
   

.. autoclass:: relink.gateway.events.raw_models.WSCloseEvent
   :members:
   
