.. currentmodule:: sonolink

Moving From Wavelink
=====================

This guide is for anyone moving over from `Wavelink <https://github.com/PythonistaGuild/Wavelink>`_.

It walks through the main differences between SonoLink and Wavelink 3.x, so you can get a feel for what
changes and what stays familiar.

What stays familiar
-------------------

* Lavalink remains the backend.
* SonoLink supports discord.py, py-cord, and disnake, each using a custom ``discord.VoiceProtocol`` for voice integration.
* The main runtime objects are still a client-level coordinator, nodes, players, queues,
  tracks, playlists, and filters.

What changes
------------

Most of the work comes down to replacing Wavelink's top-level helper APIs with explicit SonoLink objects and
adjusting for the return types used in Wavelink 3.x.

Concept mapping
---------------

.. list-table::
   :header-rows: 1

   * - Wavelink
     - SonoLink
   * - ``wavelink.Pool``
     - :class:`sonolink.Client`
   * - ``wavelink.Node``
     - :class:`sonolink.Node`
   * - ``wavelink.Player``
     - :class:`sonolink.Player`
   * - ``wavelink.Playable.search(...)``
     - :meth:`sonolink.Client.search_track`
   * - ``wavelink.Pool.fetch_tracks(...)``
     - :meth:`sonolink.Node.search_track`
   * - ``wavelink.Search``
     - :class:`sonolink.models.SearchResult`
   * - ``wavelink.Filters``
     - :class:`sonolink.models.Filters`

Connection lifecycle
--------------------

In Wavelink, node management is centered on the class-level pool API.
The Wavelink docs show connecting with ``wavelink.Pool.connect(...)`` after building
``wavelink.Node(...)`` objects.

In SonoLink, the equivalent flow is explicit and instance-based:

.. code-block:: python

   import sonolink

   sl_client = sonolink.Client(bot)
   
   sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       id="main",
   )

   async def setup_hook() -> None:
       await sl_client.start()

.. note::
   :meth:`sonolink.Client.start` should be called once your Discord client is ready,
   typically in :meth:`discord:discord.Client.setup_hook` (discord.py), :func:`pycord:discord.on_connect` (py-cord)
   or :func:`disnake:disnake.on_connect` (disnake)
   rather than in the ``on_ready`` event.
   
Settings
--------

SonoLink introduces a settings system with no direct Wavelink equivalent. Settings are
dataclass-like objects passed at node or player creation time, giving you structured control
over behavior that Wavelink left to ad-hoc configuration:

* :class:`sonolink.models.InactivitySettings` — controls how long a player waits before
  disconnecting when the channel is inactive, and what counts as inactive.
* :class:`sonolink.models.CacheSettings` — configures the node-level LFU search result cache.
* :class:`sonolink.models.AutoPlaySettings` — configures autoplay mode, search provider,
  discovery count, and seed limits.
* :class:`sonolink.models.HistorySettings` — enables or limits the track history that
  ``previous`` and autoplay depend on.

.. code-block:: python

   from sonolink.models.settings import AutoPlaySettings, CacheSettings, HistorySettings, InactivitySettings
   from sonolink.gateway.enums import AutoPlayMode, InactivityMode

   sl_client.create_node(
       uri="http://localhost:2333",
       password="youshallnotpass",
       inactivity_settings=InactivitySettings(
           timeout=300,
           mode=InactivityMode.ALL_BOTS,
       ),
       cache_settings=CacheSettings(
           enabled=True,
           max_items=1000,
       ),
   )

   player = sl_client.get_best_node().create_player(
       autoplay_settings=AutoPlaySettings(
           mode=AutoPlayMode.ENABLED,
           discovery_count=10,
       ),
       history_settings=HistorySettings(
           enabled=True,
           max_items=100,
       ),
   )

Searching
---------

In Wavelink, the search flow is usually:

.. code-block:: python

   # Wavelink
   tracks = await wavelink.Playable.search(query)
   if not tracks:
       return

   if isinstance(tracks, wavelink.Playlist):
       track = tracks.tracks[0]
   else:
       track = tracks[0]

In SonoLink, searching returns a wrapper object that makes the result type explicit:

.. code-block:: python

   # SonoLink
   result = await sl_client.search_track(query)
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result
   rest = []

   if isinstance(data, list):
       play_track = data[0]
   elif isinstance(data, sonolink.models.Playlist):
       play_track = data.tracks[0]
       rest = data.tracks[1:]
   else:
       play_track = data

:class:`sonolink.models.SearchResult` covers all possible outcomes: a single track, a playlist,
a search result list, an empty result, or an error result.

Players and voice connection
----------------------------

You still connect through Discord with:

.. code-block:: python

   player = await voice_channel.connect(cls=sonolink.Player)

If you need to pre-configure a player with volume, filters, queue mode, autoplay, or history
settings before connecting, you can either instantiate :class:`sonolink.Player` directly or use
:meth:`sonolink.Node.create_player` — both are equivalent:

.. code-block:: python

   from sonolink.models import Filters, Karaoke

   player = sonolink.Player(
       node=node,
       volume=100,
       filters=Filters(
           karaoke=Karaoke(level=0.5),
       ),
   )

   # or

   player = node.create_player(
       volume=100,
       filters=Filters(
           karaoke=Karaoke(level=0.5),
       ),
   )

   await voice_channel.connect(cls=player)

See :doc:`/guides/players` for the full player reference.

Playback flow
-------------

SonoLink does not expose a ``playing`` property. The common pattern is to call
:meth:`sonolink.Player.play` directly when nothing is currently playing, and put remaining
tracks into the queue. Queue progression after a track ends is handled automatically:

.. code-block:: python

   if not vc.current:
       await vc.play(play_track)
   else:
       rest = [play_track, *rest]

   for track in rest:
       await vc.queue.put_wait(track)

When a track ends, SonoLink automatically calls :meth:`sonolink.Player.skip` internally, which
pulls the next track from the queue, falls back to autoplay if the queue is empty, and stops
the player if neither applies. You do not need to drive this manually.

Filters
-------

SonoLink applies filters with the same player method name, but the type is different:

.. code-block:: python

   from sonolink.models import Filters

   filters = Filters()
   await player.set_filters(filters, seek=True)

See :doc:`/guides/filters` for the full filter reference.

Events
------

Wavelink has event names such as ``on_wavelink_node_ready`` and
``on_wavelink_track_start`` that are dispatched through the underlying Discord client.

SonoLink does the same, but with the `_sonolink_` prefix instead of ``_wavelink_``. 
The event system is otherwise similar, with the same dispatch mechanism and handler signature.

The available events are:

* :func:`on_sonolink_node_ready` — a node has connected and is ready to use.
* :func:`on_sonolink_node_close` — a node connection was closed.
* :func:`on_sonolink_player_update` — periodic position and state sync from the node.
* :func:`on_sonolink_track_start` — a track has started playing.
* :func:`on_sonolink_track_end` — a track finished, was stopped, or was replaced.
* :func:`on_sonolink_track_exception` — a track encountered a playback error.
* :func:`on_sonolink_track_stuck` — a track stalled and could not continue.
* :func:`on_sonolink_unknown_event` — an unrecognized event type was received from the node.

When moving, keep playback flow explicit in commands and services first, then reintroduce
event-driven logic where still needed.

Autoplay
--------

Wavelink exposes an ``auto_queue`` concept SonoLink's autoplay is configured
through :class:`sonolink.models.AutoPlaySettings` at player creation time and toggled via
:attr:`sonolink.Player.autoplay`, which accepts an :class:`sonolink.AutoPlayMode` value:

* :attr:`sonolink.AutoPlayMode.DISABLED` — autoplay is completely disabled. The player stops when the queue empties.
* :attr:`sonolink.AutoPlayMode.PARTIAL` — SonoLink manages progression autonomously but does not fill the queue with recommended tracks.
* :attr:`sonolink.AutoPlayMode.ENABLED` — when the queue empties, SonoLink discovers related tracks and fills the queue automatically. Tracks added to the standard queue are treated as priority.

The search provider used for discovery is configured via :class:`sonolink.SearchProvider` in
:class:`sonolink.models.AutoPlaySettings`:

* :attr:`sonolink.SearchProvider.YOUTUBE` — YouTube Radio mix based on the track identifier.
* :attr:`sonolink.SearchProvider.SPOTIFY` — Spotify recommendations based on the track identifier.
* :attr:`sonolink.SearchProvider.DEEZER` — Deezer track or artist radio based on the identifier.

.. warning::
   Autoplay uses the track history as its seed. Ensure :class:`sonolink.models.HistorySettings`
   has history enabled, otherwise autoplay will have no reference track to discover from.

State helpers
-------------

Wavelink exposes ``player.playing`` and similar helpers. SonoLink does not have a ``playing``
property. The public player state is:

* :attr:`sonolink.Player.current` — the track currently playing, or ``None``.
* :attr:`sonolink.Player.paused` — whether the player is paused.
* :attr:`sonolink.Player.position` — the current playback position in milliseconds.
* :attr:`sonolink.Player.volume` — the current volume, between 0 and 1000.
* :attr:`sonolink.Player.queue` — the :class:`sonolink.Queue` holding upcoming and historical tracks.
* :attr:`sonolink.Player.autoplay` — the current :class:`sonolink.AutoPlayMode` for this player.

Useful references
-----------------

* `Wavelink repository <https://github.com/PythonistaGuild/Wavelink>`_
* `Wavelink migrating guide <https://wavelink.readthedocs.io/en/v3.4.1/migrating.html>`_
* `Wavelink API reference <https://wavelink.readthedocs.io/en/v3.4.1/wavelink.html>`_
