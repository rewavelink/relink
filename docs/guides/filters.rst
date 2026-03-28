.. currentmodule:: relink

Filters And Playback State
==========================


Applying filters
----------------

Lavalink filters are grouped into a single :class:`relink.models.Filters` object.
You build that object first, then apply it with :meth:`relink.Player.set_filters`:

.. code-block:: python

   from relink.models import Filters, Timescale

   filters = Filters(
      timescale=Timescale(speed=1.1),
   )
   await player.set_filters(filters, seek=True)

This keeps filter changes explicit. Instead of calling a separate method for
every effect, you describe the filter state you want and send it to the player
in one request.

How filter payloads work
------------------------

:class:`relink.models.Filters` mirrors the filter payload Lavalink
expects. Each attribute represents one filter family:

* ``volume``
* ``equalizer``
* ``karaoke``
* ``timescale``
* ``tremolo``
* ``vibrato``
* ``rotation``
* ``distortion``
* ``channel_mix``
* ``low_pass``
* ``plugin_filters``

The important detail is that filter updates are partial. If you only provide
``timescale``, ReLink sends only that part of the filter payload. This makes it
easy to build focused commands such as ``nightcore``, ``bassboost``, or
``lowpass`` without rebuilding every other filter each time.

In practice, this means you should think about filters as player state. If your
bot lets users stack effects, you will usually want to keep track of the
current :attr:`relink.Player.filters`, update the parts you care about, and
then apply the combined result.

Setting filters cleanly
-----------------------

A simple pattern is to build a fresh filter object for the exact effect you
want:

.. code-block:: python

   from relink.models import Filters, Rotation

   filters = Filters(
      rotation=Rotation(rotation_hz=0.2),
   )

   await player.set_filters(filters, seek=True)

If your bot supports multiple effects at once, it is usually better to compose
them in a single ``Filters`` object:

.. code-block:: python

   from relink.models import (
      Filters,
      Rotation,
      Timescale,
      Tremolo,
   )

   filters = Filters(
      timescale=Timescale(speed=1.1, pitch=1.1),
      rotation=Rotation(rotation_hz=0.2),
      tremolo=Tremolo(frequency=4.0, depth=0.3),
   )

   await player.set_filters(filters, seek=True)

This keeps the applied state easy to reason about and avoids spreading one
audio change across several unrelated command branches.

Merging and combining filters
-----------------------------

If you need to layer effects on top of an existing filter state without
replacing everything, :meth:`relink.models.Filters.merge` and
:meth:`relink.models.Filters.combine` let you do that cleanly.

``merge`` updates the current instance in place, preferring values from the
other filter where both define the same effect:

.. code-block:: python

   from relink.models import Filters, Rotation, Timescale

   filters = Filters(timescale=Timescale(speed=1.1, pitch=1.1))
   extra = Filters(rotation=Rotation(rotation_hz=0.2))
   
   filters.merge(extra)
   await player.set_filters(filters, seek=True)

``combine`` does the same thing but returns a new ``Filters`` instance and
leaves both inputs unchanged:

.. code-block:: python

   from relink.models import Filters, Rotation, Timescale

   base = Filters(timescale=Timescale(speed=1.1, pitch=1.1))
   extra = Filters(rotation=Rotation(rotation_hz=0.2))

   merged = base.combine(extra)
   await player.set_filters(merged, seek=True)

Both methods also support the ``|`` and ``|=`` operators as shorthand:

.. code-block:: python

   # equivalent to combine (returns new instance)
   merged = base | extra

   # equivalent to merge (mutates in place)
   base |= extra

A practical case for these methods is when your bot tracks the player's current
filter state and a command needs to add or override one effect without touching
the others:

.. code-block:: python

   current = player.filters
   nightcore = Filters(timescale=Timescale(speed=1.2, pitch=1.2))

   await player.set_filters(current | nightcore, seek=True)

This preserves any active equalizer, rotation, or other effects while applying
the timescale change on top.

Why ``seek=True`` matters
-------------------------

Some Lavalink filters do not become audible the moment the filter payload is
updated. In those cases, the effect becomes clear only after playback position
changes.

Passing ``seek=True`` tells ReLink to apply the filters and then seek to the
player's current position. In effect, playback jumps to the same timestamp it
was already on, which nudges Lavalink to reprocess the stream with the updated
filter state.

That matters because without the extra seek:

* a filter may appear to do nothing at first,
* the effect may only become audible after the next manual seek,
* the change may not be obvious until the next track starts.

With ``seek=True``, users hear the effect immediately in most cases, which is
usually the behavior you want for interactive music commands.

There is a tradeoff: a seek is still a seek, even when it targets the current
position. Depending on the source and backend behavior, that can produce a very
small audible interruption. For most bots, that tradeoff is worth it because the
filter change feels instant and predictable.

As a practical rule:

* use ``seek=True`` when the command is meant to change how the current track
  sounds right now,
* use ``seek=False`` when you are preparing filter state ahead of time or when
  avoiding even a tiny playback jump matters more than immediate feedback.

Available filters
-----------------

``volume``
^^^^^^^^^^

``Filters.volume`` is a linear volume multiplier from ``0.0`` to ``5.0``. ``1.0``
means unchanged volume.

.. code-block:: python

   from relink.models import Filters

   filters = Filters(volume=0.8)
   await player.set_filters(filters, seek=True)

This is different from :meth:`relink.Player.set_volume`, which uses Lavalink's
player volume scale of ``0`` to ``1000``. Filter volume is part of the filter
pipeline, while ``set_volume`` changes the player's main output level.

If you only want a straightforward volume command, :meth:`relink.Player.set_volume`
is usually the clearer choice. Filter volume is more useful when volume is part
of a larger filter preset.

``equalizer``
^^^^^^^^^^^^^

``Filters.equalizer`` lets you shape specific frequency bands. Lavalink provides 15
bands, covering roughly ``25 Hz`` through ``16000 Hz``.

.. code-block:: python

   from relink.models import Equalizer, Filters

   filters = Filters(
      equalizer=[
         Equalizer(band=0, gain=0.15),
         Equalizer(band=1, gain=0.15),
         Equalizer(band=2, gain=0.10),
      ],
   )

   await player.set_filters(filters, seek=True)

This is the filter you would reach for when building presets such as bass boost,
treble boost, vocal emphasis, or a custom EQ command. Small changes usually
sound better than extreme ones, especially when multiple bands are boosted at once.

``karaoke``
^^^^^^^^^^^

``Filters.karaoke`` reduces content in a target frequency region. It is commonly used
for vocal reduction.

.. code-block:: python

   from relink.models import Karaoke, Filters

   filters = Filters(
      karaoke=Karaoke(
         level=0.8,
         mono_level=0.8,
      ),
   )

   await player.set_filters(filters, seek=True)

This effect depends heavily on the track itself. It can reduce centered vocals
in some songs, but it will not cleanly remove vocals from every mix.

``timescale``
^^^^^^^^^^^^^

``Filters.timescale`` changes playback speed, pitch, and rate.

.. code-block:: python

   from relink.models import Filters, Timescale

   filters = Filters(
      timescale=Timescale(speed=1.1, pitch=1.1),
   )

   await player.set_filters(filters, seek=True)

This is the filter behind effects such as nightcore, slowed, vaporwave, or
"chipmunk" style playback. The three values work together:

* ``speed`` changes how fast the track plays,
* ``pitch`` changes perceived pitch,
* ``rate`` changes internal playback rate.

If you are building named presets, keep the combinations deliberate. Small
changes often sound more musical than aggressive ones.

``tremolo``
^^^^^^^^^^^

``Filters.tremolo`` rapidly oscillates output volume.

.. code-block:: python

   from relink.models import Filters, Tremolo

   filters = Filters(
      tremolo=Tremolo(frequency=4.0, depth=0.5),
   )

   await player.set_filters(filters, seek=True)

This creates a pulsing effect. ``frequency`` controls how fast the pulsing is,
and ``depth`` controls how strong it is.

``vibrato``
^^^^^^^^^^^

``Filters.vibrato`` rapidly oscillates pitch.

.. code-block:: python

   from relink.models import Filters, Vibrato

   filters = Filters(
      vibrato=Vibrato(frequency=6.0, depth=0.3),
   )

   await player.set_filters(filters, seek=True)

This creates a wavering pitch effect. It is usually more noticeable on vocals,
synths, and sustained notes than on heavily percussive audio.

``rotation``
^^^^^^^^^^^^

``Filters.rotation`` rotates audio across stereo channels.

.. code-block:: python

   from relink.models import Filters, Rotation

   filters = Filters(
      rotation=Rotation(rotation_hz=0.2),
   )

   await player.set_filters(filters, seek=True)

This effect is sometimes described as an "8D" or stereo spinning effect. It is
most noticeable with headphones or any setup where left and right channels are
clearly separated.

``distortion``
^^^^^^^^^^^^^^

``PlayerFilters.distortion`` applies wave-shaping changes that can alter the
tone dramatically.

.. code-block:: python

   from relink.models import Distortion, Filters

   filters = Filters(
      distortion=Distortion(
         sin_scale=0.2,
         cos_scale=0.2,
         scale=1.0,
      ),
   )

   await player.set_filters(filters, seek=True)

This is one of the easiest filters to overdo. Very small changes can produce
large audible differences, so it is best to tune it gradually and test with
real tracks.

``channel_mix``
^^^^^^^^^^^^^^^

``PlayerFilters.channel_mix`` controls how left and right input channels are
mixed into the output channels.

.. code-block:: python

   from relink.models import ChannelMix, Filters

   filters = Filters(
      channel_mix=ChannelMix(
         left_to_left=0.5,
         left_to_right=0.5,
         right_to_left=0.5,
         right_to_right=0.5,
      ),
   )

   await player.set_filters(filters, seek=True)

This is useful for stereo experiments, channel balancing, or creating dual-mono
output. A value of ``0.5`` for all four coefficients is a common dual-mono setup.

``low_pass``
^^^^^^^^^^^^

``Filters.low_pass`` suppresses higher frequencies while preserving lower ones.

.. code-block:: python

   from relink.models import LowPass, Filters

   filters = Filters(
      low_pass=LowPass(smoothing=20.0),
   )

   await player.set_filters(filters, seek=True)

This can create a muffled, distant, underwater, or "radio through a wall"
style sound depending on the settings and the source material.

``plugin_filters``
^^^^^^^^^^^^^^^^^^

``Filters.plugin_filters`` is reserved for Lavalink plugin-defined filters.
ReLink passes this payload through as-is.

.. code-block:: python

   from relink.models import Filters

   filters = Filters(
      plugin_filters={
         "some-plugin": {
            "strength": 0.75,
         }
      }
   )

   await player.set_filters(filters, seek=True)

The shape of this payload depends entirely on the Lavalink plugin you are using.
If you expose plugin filters in your bot, document them separately so users know
which keys and values are valid.

Choosing between presets and custom control
-------------------------------------------

There are two common ways to expose filters in a bot:

* named presets such as ``nightcore``, ``bassboost``, ``vaporwave``, or ``8d``,
* direct user controls such as ``/speed 1.1`` or ``/eq band:3 gain:0.15``.

Presets are easier to use and easier to support. Direct controls are more
flexible, but they also need clearer validation and better explanations of what
the values mean.

If you are not sure which direction to take, start with presets. They keep the
interface simple and let you tune combinations that sound good in practice.

Other playback state
--------------------

The player also exposes:

* :attr:`relink.Player.paused`
* :attr:`relink.Player.position`
* :attr:`relink.Player.volume`
* :attr:`relink.Player.current`
* :attr:`relink.Player.filters`

These properties are useful for status embeds, command responses, and effect
toggles that need to inspect the current player state before applying changes.
