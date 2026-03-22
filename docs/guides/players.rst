.. currentmodule:: relink

Working With Players
====================


Connecting a player
-------------------

For most bots, the simplest way to create a player is to pass :class:`relink.Player`
to ``discord.py`` when connecting to a voice channel:

.. code-block:: python

   player = await voice_channel.connect(cls=relink.Player)

When you connect this way, the player will:

* use the :class:`relink.Client` attached to your Discord client,
* choose the best available connected node,
* complete the Discord voice handshake for you.

This is usually the easiest place to start because it keeps player creation
short and predictable.

If you need to configure the player before connecting, create it first, either by using an
instance or by using :meth:`relink.Node.create_player`, and then pass the configured instance
as ``cls`` to :meth:`discord.abc.Connectable.connect`. This is useful when you want custom
defaults such as volume, filters, autoplay, or history settings.

.. code-block:: python

   player = relink.Player(
      node=node,
      volume=100,
      filters=relink.rest.schemas.PlayerFilters(
         karaoke=relink.rest.schemas.KaraokeFilter(
            level=0.5,
         ),
      ),
   )

   # or

   player = node.create_player(
      volume=100,
      filters=relink.rest.schemas.PlayerFilters(
         karaoke=relink.rest.schemas.KaraokeFilter(
            level=0.5,
         ),
      ),
   )

   await voice_channel.connect(cls=player)

Reusing an existing player
--------------------------

In command handlers, ``ctx.voice_client`` is usually the active voice connection.
If your bot connected with :class:`relink.Player`, that value will normally already
be the player you want:

.. code-block:: python

   player = ctx.voice_client
   if not isinstance(player, relink.Player):
       player = await ctx.author.voice.channel.connect(cls=relink.Player)

Playback controls
-----------------

The main playback methods on :class:`relink.Player` are:

* :meth:`relink.Player.play`
* :meth:`relink.Player.stop`
* :meth:`relink.Player.pause`
* :meth:`relink.Player.resume`
* :meth:`relink.Player.skip`
* :meth:`relink.Player.previous`
* :meth:`relink.Player.seek`
* :meth:`relink.Player.set_volume`
* :meth:`relink.Player.set_filters`

All of these methods act on the current player attached to a guild. In practice,
that means they are the methods you will call from command handlers, button
callbacks, or playback services.

:meth:`relink.Player.play`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.play` to start a specific track right away.

.. code-block:: python

   track = result.result[0]
   await player.play(track)

``play`` starts the track you pass to it immediately. It does not automatically
pick the next track from the queue for you.

It is the direct "play this now" call, and it also accepts optional keyword
arguments such as ``start``, ``end``, ``volume``, and ``paused`` when you need
more control over playback.

:meth:`relink.Player.stop`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.stop` to end the current track and clear the active
playback state.

.. code-block:: python

   await player.stop()

This is useful when you want playback to end without immediately starting another track.
By default, this stops the current track but leaves the queue and history intact.

If you want a more complete reset, you can also clear queued and historical tracks:

.. code-block:: python

   await player.stop(clear_queue=True, clear_history=True)

This is a good fit for commands such as ``stop``, ``leave``, ``clear``, or admin-side
"reset player" actions.

:meth:`relink.Player.pause` and :meth:`relink.Player.resume`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.pause` to pause playback and
:meth:`relink.Player.resume` to continue it later.

.. code-block:: python

   await player.pause()
   await player.resume()

These methods simply change the state of the current track. The paused state is
also available through :attr:`relink.Player.paused` if you want to show playback
status in an embed or avoid repeating a pause or resume action.

If it fits your control flow better, ``await player.pause(False)`` is equivalent
to calling ``resume()``.

:meth:`relink.Player.skip`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.skip` to move forward to the next track.

.. code-block:: python

   next_track = await player.skip()

``skip`` is queue-aware:

* if there is another track in the queue, it starts that track,
* if autoplay is enabled, autoplay may provide the next track,
* if neither applies, playback stops.

This makes it a better choice than manually calling ``stop()`` when your intent is
"go to whatever should play next".

:meth:`relink.Player.previous`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.previous` to return to the most recent track in history.

.. code-block:: python

   previous_track = await player.previous()

This is meant to behave like a real "back" button, not just replay the current
song. When possible, it pulls the last track from history, pushes the current
track back to the front of the queue, and starts the previous track.

That means ``previous`` depends on queue history being available. If there is no playback
history yet, it will fail rather than guessing what "previous" should mean.

:meth:`relink.Player.seek`
^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.seek` to jump to a specific position in the current track.
The position is expressed in milliseconds.

.. code-block:: python

   await player.seek(60_000)  # 1 minute

``seek`` also matters outside dedicated seek commands, because some Lavalink
behavior, especially filter application, may only become audible after playback
position changes.

:meth:`relink.Player.set_volume`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.set_volume` to change the player's output volume.

.. code-block:: python

   await player.set_volume(75)

ReLink volume values use the Lavalink range of ``0`` to ``1000``:

* ``100`` is the normal default volume,
* values below ``100`` reduce volume,
* values above ``100`` amplify audio and may sound harsh or clip at higher levels.

:meth:`relink.Player.set_filters`
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Use :meth:`relink.Player.set_filters` to apply Lavalink filters such as karaoke,
timescale, equalizer, tremolo, or rotation.

.. code-block:: python

   from relink.rest.schemas import PlayerFilters, TimescaleFilter

   filters = PlayerFilters(timescale=TimescaleFilter(speed=1.1))
   await player.set_filters(filters, seek=True)

Filters are grouped into a single :class:`relink.rest.schemas.PlayerFilters`
object and then applied in one call.

The ``seek=True`` part is often important. Some filters are not immediately
audible until playback position changes, so seeking to the current position
makes the effect audible right away.

For more information on filters, go to `the filters guide <filters.html>`_.

Playing tracks
^^^^^^^^^^^^^^

A common playback flow is:

1. search for a track,
2. add it to the queue,
3. start playback only if nothing is currently playing.

.. code-block:: python

   result = await rl_client.search_track("never gonna give you up")
   if result.is_error() or result.is_empty() or result.result is None:
       return

   data = result.result
   if isinstance(data, list):
       track = data[0]
   elif isinstance(data, relink.models.Playlist):
       track = data.tracks[0]
   else:
       track = data

   player.queue.put(track)

   if player.current is None:
       await player.play(player.queue.get())

This pattern is a good default because it works just as well for a simple play
command as it does for a larger queue-driven music flow.

Moving between nodes
--------------------

If you run multiple Lavalink nodes, you can migrate a player with:

.. code-block:: python

   await player.move_to(other_node)

This is mainly useful for operational workflows such as:

* draining a busy or unhealthy node,
* moving guilds away from a node before maintenance,
* redistributing load across multiple Lavalink instances.

You probably will not need this in day-to-day command logic, but it becomes
very useful in larger bots and multi-node deployments.

Disconnecting cleanly
---------------------

Use :meth:`relink.Player.disconnect` instead of only disconnecting the Discord voice client.
This ensures the Lavalink-side player is destroyed and ReLink can clean up its internal state
for that guild.

In practice, this is as simple as:

.. code-block:: python

   vc = ctx.voice_client
   await vc.disconnect()

If ``vc`` is a :class:`relink.Player`, this will call the player implementation and perform
the full cleanup. This is the recommended way to handle leave or disconnect commands.
