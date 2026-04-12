.. currentmodule:: sonolink

.. _whats_new:

Changelog
=========

This page keeps a detailed human friendly rendering of what's new and changed
in specific versions.

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
