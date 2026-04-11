.. _version_guarantees:

Version Guarantees
==================

SonoLink follows `semantic versioning <https://semver.org/>`_ — in short, if a release breaks
something in your existing code, the major version number will reflect that.

In practice, things aren't always black and white. Lavalink can change behaviour between
versions, the Discord libraries SonoLink supports each have their own release cadences, and Python
itself introduces new changes throughout new versions. So it helps to be explicit about what "breaking"
actually means here.

.. important::

    These guarantees only cover **publicly documented** parts of the library. If it isn't in the
    docs, it isn't part of the public API — and it may change without notice.

Breaking Changes
----------------

The following are considered breaking and will trigger a major version bump:

- Removing or renaming a public function, class, or parameter without a compatibility alias.
- Changing what a public function accepts or returns in a way that breaks existing call sites.
- Altering the signature of a documented event (e.g. adding or removing positional arguments).
- Changing a default parameter value in a way that alters existing behaviour.
- Moving a public class or function to a different module without a re-export in the original location.
- Removing or changing a documented attribute on a public class.
- Raising a different exception type than what is documented.

Non-Breaking Changes
--------------------

The following are **not** considered breaking and may occur in any release:

- Internal refactors that do not affect public behaviour.
- Dependency upgrades, including major version bumps of Lavalink or the Discord libraries.
- Bug fixes that correct unintended or undocumented behaviour.
- Additions to ``__slots__`` or other internal data class internals.
- Documentation updates or corrections.
- Changes to private, underscored attributes or helpers.
- Adding a new optional parameter with a default value to an existing function.
- Adding new public classes, functions, or attributes that did not previously exist.
- Changing log messages or other output not considered part of the public API.
- Changing type annotations as long as runtime behaviour is unaffected.
