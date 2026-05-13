.. currentmodule:: sonolink
.. _whats_new:

Changelog
=========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

.. _vp1p1p0:

v1.1.0 - 2026-05-09
-------------------

**Added**
~~~~~~~~~

- Added support for `Nextcord <https://github.com/nextcord/nextcord>`_ via :class:`NextcordPlayer <.adapters._nextcord.NextcordPlayer>`.

  See the `Nextcord examples <https://github.com/sonolink/sonolink/tree/main/examples/nextcord>`_ for usage.
- Added :func:`sonolink.get_client <sonolink._registry.get_client>` for retrieving the active client instance.
- Added :meth:`Client.get_node` to retrieve a specific node from the client.
- Added three new events:

  - :func:`on_sonolink_websocket_closed` (:class:`WebSocketClosedEvent`)
  - :func:`on_sonolink_stats_receive` (:class:`StatsEvent`)
  - :func:`on_sonolink_player_disconnect` (:class:`PlayerDisconnectEvent`)

- Added :meth:`Player.update` to quickly update multiple player settings at once.
  :attr:`Player.autoplay_settings`, :attr:`Player.history_settings`, and :attr:`Player.queue_mode`
  are now exposed and can be set directly.
- Added :attr:`TrackSourceType.DEEZER` as a supported track source.
- Added :attr:`Queue.count` and :attr:`History.count` properties.
- Added :attr:`Queue.autoplay_tracks` and :meth:`Queue.put_autoplay` to fix autoplay queue priority
  via a dedicated stream. :attr:`Playable.autoplay` is also now exposed.
- Added :exc:`AutoPlaySeedMissing`, a specific error raised when autoplay has no seed tracks to
  generate from.
- Added framework-specific import and mismatch exceptions:

  - :exc:`FrameworkClientMismatch`
  - :exc:`FrameworkImportError`

- Added a :doc:`Getting Started </guides/getting-started>` guide.
- Added four new migration guides:

  - `Mafic <https://sonolink.readthedocs.io/en/latest/guides/migrations/mafic.html>`_
  - `Lavalink.py <https://sonolink.readthedocs.io/en/latest/guides/migrations/lavalink.py.html>`_
  - `Lavaplay.py <https://sonolink.readthedocs.io/en/latest/guides/migrations/lavaplay.py.html>`_
  - `Pomice <https://sonolink.readthedocs.io/en/latest/guides/migrations/pomice.html>`_

  The existing `WaveLink <https://sonolink.readthedocs.io/en/latest/guides/migrations/wavelink.html>`_ guide has also been updated.

- Added a `py.typed <https://typing.python.org/en/latest/spec/distributing.html#packaging-typed-libraries>`_ marker file for improved typing compatibility with type checkers.
- Added two new keyword arguments to :meth:`Client.create_node`: ``host`` and ``port`` for
  specifying the node URI in parts as an alternative to the single ``uri`` string; ``uri``
  is now optional to allow for this.
- Added a `Code of Conduct <https://github.com/sonolink/sonolink/blob/main/.github/CODE_OF_CONDUCT.md>`_ for project community guidelines.

**Changed**
~~~~~~~~~~~

- :class:`WSCloseEvent` has been renamed to :class:`WebSocketClosedEvent`.
- :meth:`get_best_node` now prefers nodes with known stats over nodes with no reported stats.
- Swapped :exc:`asyncio.TimeoutError` with the built-in :exc:`TimeoutError` throughout.
- Cleaned up documentation for all enums.

**Removed**
~~~~~~~~~~~

- Removed the fallback to ``discord.py`` as the default framework.
- Removed the unused ``value`` argument from :meth:`Player.pause`.
  :meth:`Player.resume` is no longer an alias for unpausing — it must be called explicitly to
  resume playback.

**Fixed**
~~~~~~~~~

- Fixed incorrect generics on the :class:`PycordPlayer <.adapters._pycord.PycordPlayer>`.
- Fixed ``force`` parameter handling in :meth:`Player.disconnect <._base.BasePlayer.disconnect>`.
- Fixed the library raising :class:`QueueEmpty <sonolink.QueueEmpty>` when skipping tracks for the user interally. 

**Miscellaneous**
~~~~~~~~~~~~~~~~~

- :class:`sonolink.gateway.Node <sonolink.gateway.node.Node>` has been split into multiple components internally for
  better separation of concerns and maintainability. This is not a breaking change as the
  public API remains the same, but it should improve code readability and future extensibility.
- Formatted the project with `Ruff <https://docs.astral.sh/ruff/>`_ for consistent code style and linting.

.. _vp1p0p1:

v1.0.1 - 2026-04-12
-------------------

**Fixed**
~~~~~~~~~
- Inconsistent environment variable usage across code and documentation
- Fixed performance and memory issue in PlayerFactory caused by repeated metadata scans:

  - Reduced connection time (~11x faster)
  - Reduced memory peak (~12x lower)
  - Eliminated repeated expensive ``importlib.metadata.packages_distributions()`` calls

.. _vp1p0p0:

v1.0.0 - 2026-04-11
-------------------

Initial release. For more information on what this added, consider referring to the API Reference or the examples.



.. _unreleased: https://github.com/sonolink/sonolink/compare/v1.0.1..HEAD
