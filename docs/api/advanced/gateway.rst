.. currentmodule:: sonolink

Gateway API
===========

The gateway layer contains the queue, enum, error, and event-related runtime types.
The top-level :class:`sonolink.Client`, :class:`sonolink.Node`, and :class:`sonolink.Player`
classes are documented on :doc:`/api/core`.

Voice state
-----------

.. autoclass:: sonolink.PlayerConnectionState
   :members:   


Websocket payloads
------------------

.. autoclass:: sonolink.gateway.schemas.PlayerState
   :members:

.. autoclass:: sonolink.gateway.schemas.MemoryStats
   :members:

.. autoclass:: sonolink.gateway.schemas.CPUStats
   :members:
   
.. autoclass:: sonolink.gateway.schemas.FrameStats
   :members:

.. autoclass:: sonolink.gateway.schemas.StatsEvent
   :members:

.. autoclass:: sonolink.gateway.schemas.WebSocketClosedEvent
   :members:   

Library adapters
----------------

These classes are the concrete :class:`~sonolink.Player` implementations for each
supported Discord library. You will not normally instantiate them directly —
:class:`~sonolink.Player` resolves the correct adapter automatically at runtime via
the ``RELINK_FRAMEWORK`` environment variable. They are documented here for
completeness and for users who need to type-annotate their voice channel references
precisely.

All three classes inherit the full public API of :class:`~sonolink.player.BasePlayer`
(playback, queue, filters, volume, etc.) in addition to the members listed below.

.. autoclass:: sonolink.gateway.player._base.BasePlayer
   :members:

.. autoclass:: sonolink.gateway.player.adapters._dpy.DpyPlayer
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: sonolink.gateway.player.adapters._disnake.DisnakePlayer
   :members:
   :inherited-members:
   :show-inheritance:

.. autoclass:: sonolink.gateway.player.adapters._pycord.PycordPlayer
   :members:
   :inherited-members:
   :show-inheritance:
