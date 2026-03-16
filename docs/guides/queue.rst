.. currentmodule:: relink

Queue Management
================


Queue basics
------------

Every :class:`relink.Player` has a :attr:`relink.Player.queue` object. The queue tracks:

* queued items waiting to play,
* the current track,
* playback history,
* loop mode.

Adding tracks
-------------

You can add one track, many tracks, or a playlist:

.. code-block:: python

   player.queue.put(track)
   player.queue.put(track_list)
   player.queue.put(playlist)

To serialize concurrent inserts, use :meth:`relink.Queue.put_wait`.

Starting playback from the queue
--------------------------------

The queue does not auto-play by itself. A common pattern is:

.. code-block:: python

   player.queue.put(track)

   if player.current is None:
       await player.play(player.queue.get())

Queue modes
-----------

The queue supports :class:`relink.QueueMode`:

* ``NORMAL`` plays and removes tracks in order.
* ``LOOP`` repeats the current track.
* ``LOOP_ALL`` rebuilds the queue from history once the queue empties.

History
-------

History is owned by :attr:`relink.Queue.history`. It is controlled by
:class:`relink.models.HistorySettings`.

Use history when you want features such as:

* :meth:`relink.Player.previous`
* loop-all playback
* smarter autoplay logic

Useful queue methods
--------------------

Some of the most useful queue methods are:

* :meth:`relink.Queue.get`
* :meth:`relink.Queue.pop`
* :meth:`relink.Queue.previous`
* :meth:`relink.Queue.shuffle`
* :meth:`relink.Queue.swap`
* :meth:`relink.Queue.reset`
