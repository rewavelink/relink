Migrating From Wavelink
=======================

This guide is for users coming from `Wavelink <https://github.com/PythonistaGuild/Wavelink>`_.
ReLink is a fork in lineage and overall design direction, but it is a rewrite rather than a
drop-in compatibility layer.

What stays familiar
-------------------

Some of the main concepts are still recognizable:

* Lavalink remains the backend.
* ``discord.py`` voice integration still uses a custom ``discord.VoiceProtocol``.
* The main runtime objects are still a client-level coordinator, nodes, players, queues,
  tracks, playlists, and filters.

What changes
------------

The migration is mostly about replacing the old global Wavelink entry points with explicit ReLink
objects and adapting to different return types.

Concept mapping
---------------

.. list-table::
   :header-rows: 1

   * - Wavelink
     - ReLink
   * - ``wavelink.Pool``
     - :class:`relink.Client`
   * - ``wavelink.Node``
     - :class:`relink.Node`
   * - ``wavelink.Player``
     - :class:`relink.Player`
   * - ``wavelink.Playable.search(...)``
     - :meth:`relink.Client.search_track`
   * - ``wavelink.Pool.fetch_tracks(...)``
     - :meth:`relink.Node.search_track`
   * - ``wavelink.Search``
     - :class:`relink.models.SearchResult`
   * - ``wavelink.Queue``
     - :class:`relink.Queue`
   * - ``wavelink.Filters``
     - ``relink.rest.schemas.PlayerFilters``

Connection lifecycle
--------------------

In Wavelink, node management is centered on the class-level pool API.
The Wavelink docs show connecting with ``wavelink.Pool.connect(...)`` after building
``wavelink.Node(...)`` objects.

In ReLink, the equivalent flow is explicit and instance-based:

.. code-block:: python

   import relink

   rl_client = relink.Client(bot)

   rl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )

   @bot.event
   async def on_ready() -> None:
       await rl_client.start()

The important change is that there is no global pool singleton. Your ``relink.Client`` instance
is the coordinator.

Searching
---------

This is the biggest day-to-day API difference.

In Wavelink 3, the documented search flow is usually:

.. code-block:: python

   tracks = await wavelink.Playable.search(query)

That returns either ``list[wavelink.Playable]`` or ``wavelink.Playlist``.

In ReLink, searching returns a wrapper object:

.. code-block:: python

   result = await rl_client.search_track(query)

   if result.is_error():
       ...
   elif result.is_empty() or result.result is None:
       ...
   else:
       data = result.result

:class:`relink.models.SearchResult` makes the result type explicit:

* single track,
* playlist,
* search result list,
* empty result,
* error result.

That means a Wavelink migration usually needs a small result-normalization helper.

Searching before and after
--------------------------

.. code-block:: python

   # Wavelink
   tracks = await wavelink.Playable.search(query)
   if not tracks:
       return

   if isinstance(tracks, wavelink.Playlist):
       track = tracks.tracks[0]
   else:
       track = tracks[0]

.. code-block:: python

   # ReLink
   result = await rl_client.search_track(query)
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result
   if isinstance(data, list):
       track = data[0]
   elif hasattr(data, "tracks"):
       track = data.tracks[0]
   else:
       track = data

Players and voice connection
----------------------------

This part should feel familiar. You still connect through Discord with:

.. code-block:: python

   player = await voice_channel.connect(cls=relink.Player)

The player is still the object you work with for queueing and playback.

Playback flow
-------------

In Wavelink, many bots check ``player.playing`` and then call ``player.play(track)``.

In ReLink, the common explicit check is against :attr:`relink.Player.current`:

.. code-block:: python

   player.queue.put(track)

   if player.current is None:
       await player.play(player.queue.get())

This is a good migration point to simplify command logic around queue-first behavior.

Queues
------

Both libraries expose a player-owned queue, but do not assume the queue APIs are identical.

ReLink queue features that map well from Wavelink are:

* ``put`` / ``put_wait``
* ``get``
* ``previous``
* ``shuffle``
* ``swap``
* ``history``
* ``mode``

The main migration rule is simple: port queue behavior deliberately rather than assuming each
old Wavelink helper exists under the same name.

Filters
-------

Wavelink documents ``wavelink.Filters`` as the main filter object.

ReLink applies filters with the same player method name, but the type is different:

.. code-block:: python

   from relink.rest.schemas import PlayerFilters

   filters = PlayerFilters()
   await player.set_filters(filters, seek=True)

If your Wavelink bot has a filter utility layer, this is usually one of the first places to
adapt type imports and constructors.

Events
------

Wavelink has documented public event names such as ``on_wavelink_node_ready`` and
``on_wavelink_track_start`` in its docs.

ReLink should be treated differently here: do not assume the Wavelink event surface or listener
names carry over. When migrating, keep playback flow explicit in commands and services first,
then reintroduce higher-level event abstractions intentionally where your bot still needs them.

Autoplay and state helpers
--------------------------

Wavelink exposes features such as ``player.playing`` and an ``auto_queue`` concept in its public
docs.

ReLink exposes different public state:

* :attr:`relink.Player.current`
* :attr:`relink.Player.paused`
* :attr:`relink.Player.position`
* :attr:`relink.Player.volume`
* :attr:`relink.Player.queue`

For migration work, rely on those documented properties instead of looking for a one-to-one copy
of Wavelink's state helpers.

Recommended migration order
---------------------------

1. Replace Pool setup with one :class:`relink.Client` attached to your Discord client.
2. Swap search code from ``Playable.search`` to ``Client.search_track``.
3. Normalize search results into a single ``track`` selection step.
4. Port queue and playback flow using :class:`relink.Player`.
5. Update filter construction and imports.
6. Revisit event-driven logic last.

Useful references
-----------------

* `Wavelink repository <https://github.com/PythonistaGuild/Wavelink>`_
* `Wavelink migrating guide <https://wavelink.readthedocs.io/en/v3.1.0/migrating.html>`_
* `Wavelink API reference <https://wavelink.readthedocs.io/en/v3.4.0/wavelink.html>`_
