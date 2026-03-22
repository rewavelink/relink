.. currentmodule:: relink

Gateway API
===========

The gateway layer contains the queue, enum, error, and event-related runtime types.
The top-level :class:`relink.Client`, :class:`relink.Node`, and :class:`relink.Player`
classes are documented on :doc:`/api/core`.

Voice state
-----------

.. autoclass:: relink.PlayerConnectionState
   :members:   


Websocket payloads
------------------

.. autoclass:: relink.gateway.schemas.PlayerState
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
