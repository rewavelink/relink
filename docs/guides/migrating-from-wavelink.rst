.. currentmodule:: relink

Migrating From Wavelink
=======================

This guide is for users coming from `Wavelink <https://github.com/PythonistaGuild/Wavelink>`_.
ReLink is a fork in lineage and overall design direction, but it is a rewrite rather than a
drop-in compatibility layer.

What stays familiar
-------------------

* Lavalink remains the backend.
* All three supported Discord libraries (discord.py, py-cord, disnake) use a custom ``discord.VoiceProtocol`` for voice integration.
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
   * - ``wavelink.Filters``
     - :class:`relink.models.Filters`

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

   async def setup_hook() -> None:
       await rl_client.start()

.. note::
   :meth:`relink.Client.start` should be called once your Discord client is ready,
   typically in :meth:`discord:discord.Client.setup_hook` (discord.py), :func:`pycord:discord.on_connect` (py-cord)
   or :func:`disnake:disnake.on_connect` (disnake)
   rather than in the ``on_ready`` event.
   
Settings
--------

ReLink introduces a settings system with no direct Wavelink equivalent. Settings are
dataclass-like objects passed at node or player creation time, giving you structured control
over behavior that Wavelink left to ad-hoc configuration:

* :class:`relink.models.InactivitySettings` — controls how long a player waits before
  disconnecting when the channel is inactive, and what counts as inactive.
* :class:`relink.models.CacheSettings` — configures the node-level LFU search result cache.
* :class:`relink.models.AutoPlaySettings` — configures autoplay mode, search provider,
  discovery count, and seed limits.
* :class:`relink.models.HistorySettings` — enables or limits the track history that
  ``previous`` and autoplay depend on.

.. code-block:: python

   from relink.models.settings import AutoPlaySettings, CacheSettings, HistorySettings, InactivitySettings
   from relink.gateway.enums import AutoPlayMode, InactivityMode

   rl_client.create_node(
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

   player = rl_client.get_best_node().create_player(
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

In Wavelink 3, the documented search flow is usually:

.. code-block:: python

   # Wavelink
   tracks = await wavelink.Playable.search(query)
   if not tracks:
       return

   if isinstance(tracks, wavelink.Playlist):
       track = tracks.tracks[0]
   else:
       track = tracks[0]

In ReLink, searching returns a wrapper object that makes the result type explicit:

.. code-block:: python

   # ReLink
   result = await rl_client.search_track(query)
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result
   rest = []

   if isinstance(data, list):
       play_track = data[0]
   elif isinstance(data, relink.models.Playlist):
       play_track = data.tracks[0]
       rest = data.tracks[1:]
   else:
       play_track = data

:class:`relink.models.SearchResult` covers all possible outcomes: a single track, a playlist,
a search result list, an empty result, or an error result.

Players and voice connection
----------------------------

You still connect through Discord with:

.. code-block:: python

   player = await voice_channel.connect(cls=relink.Player)

If you need to pre-configure a player with volume, filters, queue mode, autoplay, or history
settings before connecting, you can either instantiate :class:`relink.Player` directly or use
:meth:`relink.Node.create_player` — both are equivalent:

.. code-block:: python

   from relink.models import Filters, Karaoke

   player = relink.Player(
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

ReLink does not expose a ``playing`` property. The common pattern is to call
:meth:`relink.Player.play` directly when nothing is currently playing, and put remaining
tracks into the queue. Queue progression after a track ends is handled automatically:

.. code-block:: python

   if not vc.current:
       await vc.play(play_track)
   else:
       rest = [play_track, *rest]

   for track in rest:
       await vc.queue.put_wait(track)

When a track ends, ReLink automatically calls :meth:`relink.Player.skip` internally, which
pulls the next track from the queue, falls back to autoplay if the queue is empty, and stops
the player if neither applies. You do not need to drive this manually.

Filters
-------

ReLink applies filters with the same player method name, but the type is different:

.. code-block:: python

   from relink.models import Filters

   filters = Filters()
   await player.set_filters(filters, seek=True)

See :doc:`/guides/filters` for the full filter reference.

Events
------

Wavelink has documented public event names such as ``on_wavelink_node_ready`` and
``on_wavelink_track_start`` in its docs.

ReLink dispatches events through the underlying Discord client using the ``relink_``
prefix. The available events are:

* :func:`on_relink_node_ready` — a node has connected and is ready to use.
* :func:`on_relink_node_close` — a node connection was closed.
* :func:`on_relink_player_update` — periodic position and state sync from the node.
* :func:`on_relink_track_start` — a track has started playing.
* :func:`on_relink_track_end` — a track finished, was stopped, or was replaced.
* :func:`on_relink_track_exception` — a track encountered a playback error.
* :func:`on_relink_track_stuck` — a track stalled and could not continue.
* :func:`on_relink_unknown_event` — an unrecognized event type was received from the node.

When migrating, keep playback flow explicit in commands and services first, then reintroduce
event-driven logic where still needed.

Autoplay
--------

Wavelink exposes an ``auto_queue`` concept in its public docs. ReLink's autoplay is configured
through :class:`relink.models.AutoPlaySettings` at player creation time and toggled via
:attr:`relink.Player.autoplay`, which accepts an :class:`relink.AutoPlayMode` value:

* :attr:`relink.AutoPlayMode.DISABLED` — autoplay is completely disabled. The player stops when the queue empties.
* :attr:`relink.AutoPlayMode.PARTIAL` — ReLink manages progression autonomously but does not fill the queue with recommended tracks.
* :attr:`relink.AutoPlayMode.ENABLED` — when the queue empties, ReLink discovers related tracks and fills the queue automatically. Tracks added to the standard queue are treated as priority.

The search provider used for discovery is configured via :class:`relink.SearchProvider` in
:class:`relink.models.AutoPlaySettings`:

* :attr:`relink.SearchProvider.YOUTUBE` — YouTube Radio mix based on the track identifier.
* :attr:`relink.SearchProvider.SPOTIFY` — Spotify recommendations based on the track identifier.
* :attr:`relink.SearchProvider.DEEZER` — Deezer track or artist radio based on the identifier.

.. warning::
   Autoplay uses the track history as its seed. Ensure :class:`relink.models.HistorySettings`
   has history enabled, otherwise autoplay will have no reference track to discover from.

State helpers
-------------

Wavelink exposes ``player.playing`` and similar helpers. ReLink does not have a ``playing``
property. The public player state is:

* :attr:`relink.Player.current` — the track currently playing, or ``None``.
* :attr:`relink.Player.paused` — whether the player is paused.
* :attr:`relink.Player.position` — the current playback position in milliseconds.
* :attr:`relink.Player.volume` — the current volume, between 0 and 1000.
* :attr:`relink.Player.queue` — the :class:`relink.Queue` holding upcoming and historical tracks.
* :attr:`relink.Player.autoplay` — the current :class:`relink.AutoPlayMode` for this player.

Useful references
-----------------

* `Wavelink repository <https://github.com/PythonistaGuild/Wavelink>`_
* `Wavelink migrating guide <https://wavelink.readthedocs.io/en/v3.1.0/migrating.html>`_
* `Wavelink API reference <https://wavelink.readthedocs.io/en/v3.4.0/wavelink.html>`_
