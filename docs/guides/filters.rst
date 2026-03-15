Filters And Playback State
==========================

Applying filters
----------------

Player filters are represented by :class:`relink.rest.schemas.PlayerFilters`.
Apply them with :meth:`relink.Player.set_filters`:

.. code-block:: python

   from relink.rest.schemas import PlayerFilters

   filters = PlayerFilters()
   await player.set_filters(filters, seek=True)

Why ``seek=True`` matters
-------------------------

Some Lavalink filters become audible only after playback position changes. Passing
``seek=True`` reapplies the current position so users hear the change immediately.

Other playback state
--------------------

The player also exposes:

* :attr:`relink.Player.paused`
* :attr:`relink.Player.position`
* :attr:`relink.Player.volume`
* :attr:`relink.Player.current`

These properties are useful for status embeds and command responses.
