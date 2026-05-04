.. currentmodule:: sonolink

Moving From Lavaplay.py
=======================

This guide is for migrating from `Lavaplay.py <https://github.com/HazemMeqdad/lavaplay.py>`_ to SonoLink.

It walks through the main differences between SonoLink and Lavaplay, so you can get a feel for what
changes and what stays familiar.

What stays familiar
-------------------

* Lavalink remains the backend
* SonoLink suppors discord.py, py-cord, disnake, and nextcord via a custom
  ``discord.VoiceProtocol`` for voice integration.
* The main runtime objects are still a coordinator, nodes, players, tracks, playlists, and filters.

What changes
------------

Lavaplay is library-independent, which essentially means it does not require any library to run with,
this also means that all objects are controlled by Lavaplay and not the library you are using. On the
other hand, SonoLink, even though it is library-dependent, allows all objects to be managed by the library
you use.

For instance, ``discord.py`` provides a voice connection cache and management, and due to Lavaplay being library
independent, it can not interfere with ``discord.py``'s voice connection's cache unless done manually either with
a subclass, or manually injecting the voice connection. This essentially results on utility objects, functions,
and properties such as ``Context.voice_client`` being ``None`` when a client is in fact connected.

Being library-independent is useful when you are not using any library, or just using a library that does not
have any LavaLink support specifically for it. Or just simply prefer full control over Lavalink and separate it from
any library.

Concept mapping
---------------

.. list-table::
    :header-rows: 1

    * - Lavaplay
      - SonoLink
    * - ``lavaplay.Lavalink``
      - :class:`sonolink.Client`
    * - ``lavaplay.Node``
      - :class:`sonolink.Node`
    * - ``lavaplay.Player``
      - :class:`sonolink.Player`
    * - ``lavaplay.Node.search_youtube`` / ``lavaplay.Node.search_soundcloud`` / ``lavaplay.Node.search_youtube_music`` / ``lavaplay.Node.get_track`` / ``lavaplay.Node.auto_search_track``
      - :meth:`sonolink.Client.search_track` / :meth:`sonolink.Node.search_track`
    * - ``lavaplay.Track``
      - :class:`sonolink.models.Playable`
    * - ``lavaplay.Playlist``
      - :class:`sonolink.models.Playlist`
    * - ``lavaplay.TrackLoadFailed``
      - :attr:`sonolink.models.SearchResult.exception`
    * - ``lavaplay.Filters``
      - :class:`sonolink.models.Filters`
    * - ``lavaplay.Player.filters``
      - :meth:`sonolink.Player.set_filters`

Connection lifecycle
--------------------

In Lavaplay, you create a ``Lavalink`` instance, and then create a ``Node`` with ``Lavalink.create_node``:

.. code-block:: python

    # Lavaplay.py
    lavalink = Lavalink()
    node = lavalink.create_node(
        host="127.0.0.1",
        port=2333,
        password="youshallnotpass",
        user_id=0,
    )

    # in any function, either a library's on_ready or just a set up:
    node.connect()

In SonoLink, this is essentially the same, but with some changes:

.. code-block:: python

    # SonoLink
    sl_client = sonolink.Client(bot)

    sl_client.create_node(
        uri="http://127.0.0.1:2333",
        password="youshallnotpass",
        id="main",
    )

    async def setup_hook() -> None:
        await sl_client.start()

.. note::
    :meth:`sonolink.Client.start` should be called in :meth:`discord:discord.Client.setup_hook`
    (discord.py), :func:`pycord:discord.on_connect` (py-cord),
    :func:`disnake:disnake.on_connect` (disnake), or :func:`nextcord:nextcord.on_connect`
    (nextcord) - not in ``on_ready``.

Node management
---------------

Lavaplay only allows for one node to be created per process, so its management resides only in one
``Node`` class, which is the player's are bound to.

SonoLink handles all nodes internally, but still allows for node selection per player, exposing
:meth:`sonolink.Node.create_player`, similar to Lavaplay's ``Node.create_player``.

.. code-block:: python

    node = sl_client.get_node(id="main")
    player = node.create_player(...)

For most bots, the automatic node selection SonoLink offers is sufficient and you will not need to call this function
directly.

Players and voice connection
----------------------------

Lavaplay does not directly expose a ``discord.VoiceProtocol``, but instead relies on you providing the required data to
connect and update the player, either via a custom ``discord.VoiceProtocol`` subclass, or receiving raw events.

.. code-block:: python

    # Lavaplay.py
    player = lavalink.create_player(ctx.guild.id)
    await ctx.guild.change_voice_state(
        channel=ctx.author.voice.channel,
    )

    async def on_voice_server_update(data):
        await player.raw_voice_server_update(data)

    # other methods required, such as voice_state_update

In SonoLink, players are created through the standard Discord ``VoiceProtocol`` interface:

.. code-block:: python

    # SonoLink
    player = await voice_channel.connect(cls=sonolink.Player)

If you need to pre-configure a player before connecting:

.. code-block:: python

    player = sonolink.Player(
        node=node,
        volume=100,
    )

    await voice_channel.connect(cls=player)

See :doc:`/guides/players` for the full player reference.

Searching and loading tracks
----------------------------

In Lavaplay.py, searching is done through any ``Node.search_X`` method, or ``Node.get_tracks``,
which returns a list of ``Track``s, a ``PlayList``, or a ``TrackLoadFailed``.

.. code-block:: python

    # Lavaplay.py
    result = await node.get_tracks(query)

    if not result or isinstance(result, TrackLoadFailed):
        return

    if isinstance(result, PlayList):
        track = result.tracks[0]
    else:
        track = result[0]

In SonoLink, searching is done through :meth:`sonolink.Client.search_track` (or its equivalent in
node: :meth:`sonolink.Node.search_track`). This method returns a :class:`sonolink.models.SearchResult`
wrapper. If you want to provide a source, you can either do it passing a prefix to ``query``, or passing
a :class:`sonolink.TrackSourceType` enum member or string.

.. code-block:: python

    # SonoLink
    result = await sl_client.search_track(query, source=sonolink.TrackSourceType.SOUNDCLOUD)
    if result.is_error() or result.is_empty() or result.result is None:
        return

    data = result.result

    if isinstance(data, list):
        track = data[0]
    elif isinstance(data, sonolink.models.Playlist):
        track = data.tracks[0]
    else:
        track = data

:class:`sonolink.models.SearchResult` covers all possible outcomes: a single track, a
playlist, a search result list, an empty result, or an error.

Tracks
------

Lavaplay.py provides the ``lavaplay.Track`` model for individual tracks. The SonoLink equivalent is
:class:`sonolink.models.Playable`. SonoLink tracks additionally carry :class:`sonolink.models.Album`
and :class:`sonolink.models.Artist` metadata when the source provides it.

Playback
--------

SonoLink's :class:`sonolink.Player` exposes almost the same methods as Lavaplay.py's ``Player`` class.
With the following main differences:

* unlike Lavaplay.py, :attr:`sonolink.Player.queue` is a :class:`sonolink.Queue` object, which also provides
history-backed navigation, autoplay integration, and additional configuration via :class:`~sonolink.models.AutoPlaySettings`
and :class:`~sonolink.models.HistorySettings`. This also implies tracks are added via :meth:`~sonolink.Queue.put` rather than
``player.queue.append``, and moves all queue-related methods under :attr:`sonolink.Player.queue`.
* Lavaplay.py offers the ``player.play`` and ``player.play_playlist`` methods, the former has a direct SonoLink equivalent,
:meth:`~sonolink.Player.play`, while the latter does not and requires manual iteration through the playlist tracks and
calling ``play`` on each of them.
* in SonoLink, pausing and resuming are splitted into two different methods: :meth:`~sonolink.Player.pause` and :meth:`~sonolink.Player.resume`,
unlike Lavaplay.py in which you had to call ``player.pause(True/False)``.

See :doc:`/guides/players` for the full playback reference.

Filters
-------

In Lavaplay.py, filters are all encapsulated in the ``Filters`` class, offering methods such as ``Filters.equalizer``
or ``Filters.karaoke`` to update or set a new filter, and updated using ``player.filters(filters)``.

.. code-block:: python

    # Lavaplay.py
    filters = lavaplay.Filters()
    filters.equalizer([(0, 0.5)])  # update band 0 to 0.5Hz freq

    await player.filters(filters)

In SonoLink, we have a similar approach, the :class:`~sonolink.models.Filters` class takes as arguments all filters you
want to update, then, you can call :meth:`~sonolink.Player.set_filters` to update it. The ``seek`` parameter optionally
restarts the current track position after applying:

.. code-block:: python
    # SonoLink
    filters = sonolink.models.Filters(
        equalizer=[
            sonolink.models.Equalizer(
                band=0,
                gain=0.5,
            ),
        ],
    )

    await player.set_filters(filters)

See :doc:`/guides/filters` for the full filter reference.

Events
------

Lavaplay.py uses their ``@node.listener`` decorator on each ``Node`` instance to attach and handle events, in which you may pass
the event model, or the event name:

.. code-block:: python

    # Lavaplay.py
    @node.listener(lavaplay.TrackStartEvent)
    async def on_track_start(event: lavaplay.TrackStartEvent) -> None:
        print("New track started playing:", event.track.title)

    @node.listener("TrackEndEvent")
    async def on_track_end(event: lavaplay.TrackEndEvent) -> None:
        print("Track finished playing:", event.track.title)

SonoLink instead dispatches events through your library's client with the ``sonolink_`` prefix, passing a typed
payload object alongside the player. You register handles as standard Discord event listeners:

.. code-block:: python

    # SonoLink
    @bot.event
    async def on_sonolink_track_start(player: sonolink.Player, payload: sonolink.gateway.TrackStartEvent) -> None:
        print("New track started playing:", payload.track.title)

    @bot.event
    async def on_sonolink_track_end(player: sonolink.Player, payload: sonolink.gateway.TrackEndEvent) -> None:
        print("Track finished playing:", payload.track.title)

The event name mapping is:

.. list-table::
    :header-rows: 1

    * - Lavaplay.py event class or name
      - SonoLink event
    * - ``ReadyEvent``
      - :func:`on_sonolink_node_ready(payload) <on_sonolink_node_ready>`
    * - ``TrackStartEvent``
      - :func:`on_sonolink_track_start(player, payload) <on_sonolink_track_start>`
    * - ``TrackEndEvent``
      - :func:`on_sonolink_track_end(player, payload) <on_sonolink_track_end>`
    * - ``StatsUpdateEvent``
      - :func:`on_sonolink_stats`
