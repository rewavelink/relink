.. currentmodule:: relink

Searching Tracks
================


Basic search
------------

Use :meth:`relink.Client.search_track` for most bot commands:

.. code-block:: python

   result = await rl_client.search_track("never gonna give you up")

Search providers
----------------

You can pass a source explicitly with :class:`relink.TrackSourceType`:

.. code-block:: python

   from relink.rest import TrackSourceType

   result = await rl_client.search_track(
       "never gonna give you up",
       source=TrackSourceType.YouTubeMusic,
   )

Handling result types
---------------------

``SearchResult.result`` changes shape depending on the load type:

* single track: :class:`relink.models.Playable`
* playlist: :class:`relink.models.Playlist`
* search results: ``list[Playable]``
* empty or error: ``None``

Typical handling looks like this:

.. code-block:: python

   result = await rl_client.search_track(query)
   if result.is_error():
       raise RuntimeError(result.exception)

   if result.is_empty() or result.result is None:
       return None

   data = result.result
   if isinstance(data, list):
       return data[0]
   if hasattr(data, "tracks"):
       return data.tracks[0]
   return data

Node-level searching
--------------------

If you want to target one specific node, use :meth:`relink.Node.search_track` directly.

Caching
-------

Nodes keep an LFU cache for search results. Configure it with
:class:`relink.models.CacheSettings` when creating the node if you want to tune or disable
that behavior.
