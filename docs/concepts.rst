.. currentmodule:: relink

Core Concepts
=============


Client
------

:class:`relink.Client` is the top-level coordinator. It is responsible for:

* storing nodes,
* selecting the best connected node,
* routing internal events,
* exposing convenience helpers like :meth:`relink.Client.search_track`.

Node
----

:class:`relink.Node` represents a single Lavalink connection. A node handles:

* websocket connection state,
* REST requests,
* server stats,
* player registration for each guild,
* optional search-result caching.

If you use more than one node, :meth:`relink.Client.get_best_node` chooses the connected
node with the lowest Lavalink penalty.

Player
------

:class:`relink.Player` is a ``discord.py`` voice protocol. It manages:

* the Discord voice handshake,
* the active queue and history,
* the current track state,
* pause, seek, skip, stop, volume, and filters.

Because it is a voice protocol, the normal entry point is:

.. code-block:: python

   await voice_channel.connect(cls=relink.Player)

Queue and History
-----------------

Each player owns a :class:`relink.Queue`. The queue tracks:

* upcoming items,
* the current track,
* optional playback history,
* queue modes such as normal looping and loop-all.

History is important if you want ``previous()`` or autoplay-like behavior that depends on
recent tracks.

Search results
--------------

Track searches return :class:`relink.models.SearchResult`, not just a list. The result can be:

* a single track,
* a playlist,
* a list of search matches,
* an empty result,
* an error result.

Your bot code should inspect the result before assuming it contains a track list.

Settings objects
----------------

ReLink uses typed settings models to configure behavior:

* :class:`relink.models.CacheSettings`
* :class:`relink.models.HistorySettings`
* :class:`relink.models.InactivitySettings`
* :class:`relink.models.AutoPlaySettings`

Use these when creating nodes or players instead of hard-coding behavior in command code.
