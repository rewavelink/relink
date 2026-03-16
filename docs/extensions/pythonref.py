from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from docutils import nodes
    from sphinx.addnodes import pending_xref
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment


def _resolve_unqualified_python_reference(
    app: Sphinx,
    env: BuildEnvironment,
    node: pending_xref,
    contnode: nodes.TextElement,
) -> nodes.reference | None:
    """Resolve unqualified Python references to a unique public object name."""
    if node.get("refdomain") != "py":
        return None

    target: str | None = node.get("reftarget")
    if not target or "." in target:
        return None

    py_domain = env.domains.get("py")
    if py_domain is None:
        return None

    matches = [
        obj[0]
        for obj in py_domain.get_objects()
        if obj[0] == target or obj[0].endswith(f".{target}")
    ]
    matches = list(dict.fromkeys(matches))
    if not matches:
        return None

    public_matches = sorted(matches, key=lambda name: (name.count("."), len(name)))
    shortest_depth = public_matches[0].count(".")
    best_matches = [
        name for name in public_matches if name.count(".") == shortest_depth
    ]

    if len(best_matches) != 1:
        return None

    return py_domain.resolve_xref(
        env,
        node["refdoc"],
        app.builder,
        node["reftype"],
        best_matches[0],
        node,
        contnode,
    )


def setup(app: Sphinx) -> dict[str, bool]:
    app.connect("missing-reference", _resolve_unqualified_python_reference)
    return {"parallel_read_safe": True}
