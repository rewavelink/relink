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

Library adapters
----------------

These classes are the concrete :class:`~relink.Player` implementations for each
supported Discord library. You will not normally instantiate them directly —
:class:`~relink.Player` resolves the correct adapter automatically at runtime via
the ``RELINK_FRAMEWORK`` environment variable. They are documented here for
completeness and for users who need to type-annotate their voice channel references
precisely.

All three classes inherit the full public API of :class:`~relink.player.BasePlayer`
(playback, queue, filters, volume, etc.) in addition to the members listed below.

.. autoclass:: relink.gateway.player._base.BasePlayer
   :members:

.. autoclass:: relink.gateway.player.adapters._dpy.DpyPlayer
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __call__

.. autoclass:: relink.gateway.player.adapters._disnake.DisnakePlayer
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __call__

.. autoclass:: relink.gateway.player.adapters._pycord.PycordPlayer
   :members:
   :inherited-members:
   :show-inheritance:
   :special-members: __call__
