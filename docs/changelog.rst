.. currentmodule:: relink

.. _whats_new:

Changelog
=========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

`Unreleased`_
---------------

This section contains changes that have been merged into the `main` branch, but have not yet been released.

Added
~~~~~~

Changed
~~~~~~~

Fixed
~~~~~

Deprecated
~~~~~~~~~~

Removed
~~~~~~~

Miscellaneous
~~~~~~~~~~~~~

.. _vp1p1p0:

v1.1.0 -- 2026-04-04
---------------------

Added
~~~~~~

- Added compatibility with `discord.py`, `py-cord`, and `disnake`, including
  framework-specific client and player adapters. See
  :ref:`Framework Compatibility <framework-compatibility>`.
- Added new examples for `py-cord` and `disnake`, and reorganized the existing
  `discord.py` examples into their own directory.
- Added :meth:`relink.Queue.put_at` to insert items at specific positions in the queue.
- Added :meth:`relink.Queue.remove` to remove items from the queue by value.
- Added :meth:`relink.Queue.remove_wait` to remove items from the queue by value, asynchronously.
- Added :meth:`relink.Node.send` for sending raw requests to the node yourself.

Changed
~~~~~~~

- `relink.Client` no longer depends on `discord.py` directly. Install any
  supported framework separately, and ReLink will detect it automatically or
  accept it explicitly via the ``framework=`` parameter.
- :attr:`relink.models.Playable.extras` is mutable now. You may store any
  additional data you want in there, and it will be preserved across the library.
- :meth:`relink.Node.create_player` now returns the appropriate player type for
  the active Discord framework.

Fixed
~~~~~

- Improved HTTP exception handling and error messages, including Lavalink
  responses that omit a ``message`` field.
- Fixed several documentation issues, including inherited member rendering,
  index build failures, and file watching outside the ``docs`` directory.

Deprecated
~~~~~~~~~~

Removed
~~~~~~~

- Removed the unused `orjson` dependency from the optional ``speed`` extra.

Miscellaneous
~~~~~~~~~~~~~

- Added this changelog page to the documentation.
- Refreshed the documentation branding, banner assets, and installation guidance.


.. _vp1p0p1:

v1.0.1 -- 2026-03-31
--------------------

Bug Fixes
~~~~~~~~~

- HTTP error responses now raise :exc:`HTTPException` instead of breaking silently.

Miscellaneous
~~~~~~~~~~~~~

- Updated filters usage in the migration guide.

.. _vp1p0p0:

v1.0.0 - 2026-03-29
--------------------

Initial release.



.. _unreleased: https://github.com/rewavelink/relink/compare/v1.1.0...HEAD
