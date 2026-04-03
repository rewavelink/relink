.. currentmodule:: relink

.. _whats_new:

Changelog
=========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.


`Unreleased`_
---------------

These changes are available on the `main` branch, but have not yet been released.

Added
~~~~~

- Added :meth:`relink.Queue.put_at` to insert items at specific positions in the queue.
- Added :meth:`relink.Queue.remove` to remove items from the queue by value.
- Added :meth:`relink.Queue.remove_wait` to remove items from the queue by value, asynchronously.
- Added :meth:`relink.Node.send` for sending raw requests to the node yourself.

Changed
~~~~~~~

- :attr:`relink.models.Playable.extras` is mutable now. You may store any additional data you want in there, and it will be preserved across the library

Fixed
~~~~~

- Removed the unused `orjson` dependency.

Deprecated
~~~~~~~~~~

Removed
~~~~~~~

Miscellaneous
~~~~~~~~~~~~~

- Improved exception handling while doing HTTP requests. You should now get more detailed error messages when something goes wrong.


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



.. _unreleased: https://github.com/rewavelink/relink/compare/v1.0.1...HEAD