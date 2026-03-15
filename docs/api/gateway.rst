Gateway API
===========

The gateway layer contains the queue, enum, error, and event-related runtime types.
The top-level :class:`relink.Client`, :class:`relink.Node`, and :class:`relink.Player`
classes are documented on :doc:`core`.

Voice state
-----------

.. autoclass:: relink.PlayerConnectionState
   :members:
   

Queue
-----

.. autoclass:: relink.History
   :members:
   

.. autoclass:: relink.Queue
   :members:
   

Enums
-----

.. autoclass:: relink.NodeStatus()
   :members:

.. autoclass:: relink.TrackEndReason()
   :members:

.. autoclass:: relink.TrackExceptionSeverity()
   :members:

.. autoclass:: relink.QueueMode()
   :members:

.. autoclass:: relink.AutoPlayMode()
   :members:

.. autoclass:: relink.InactivityMode()
   :members:

.. autoclass:: relink.SearchProvider()
   :members:

Errors
------

.. autoexception:: relink.InvalidNodePassword
   :members:

.. autoexception:: relink.NodeURINotFound
   :members:

.. autoexception:: relink.QueueEmpty
   :members:

.. autoexception:: relink.HistoryEmpty
   :members:

More gateway types
------------------

.. toctree::
   :maxdepth: 1

   gateway.schemas
