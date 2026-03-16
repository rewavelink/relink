import datetime
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from relink import __version__

if TYPE_CHECKING:
    from docutils import nodes
    from sphinx.addnodes import pending_xref
    from sphinx.application import Sphinx
    from sphinx.environment import BuildEnvironment

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


# -- Project information --
project = "relink"
author = "vmphase, Soheab, DA-344"
copyright = f"{datetime.date.today().year}, {author}"
release = __version__

# -- General configuration --
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.intersphinx",
    "sphinx_copybutton",
]

# Intersphinx link to standard Python docs
intersphinx_mapping = {
    "python": ("https://docs.python.org/3", None),
}

templates_path = ["_templates"]
exclude_patterns = [
    "_build",
    "api/network.rst",
    "api/rest.http.rst",
    "api/gateway.events.rst",
    "api/utils.rst",
]
add_module_names = False
nitpick_ignore_regex = [
    ("py:class", r"discord(\..+)?"),
    ("py:meth", r"discord\.abc\.Connectable\.connect"),
    ("py:class", r"aiohttp\.ClientSession"),
    ("py:class", r"curl_cffi\.AsyncSession"),
    ("py:class", r"msgspec\.Struct"),
    ("py:class", r"(N|D|P|T|T_co|~P|SessionType|WSErrorType|type\[N\])"),
    ("py:class", r"dict\[str"),
    ("py:class", r"relink\.errors\.ReLinkException"),
    ("py:class", r"relink\.gateway\.errors\.NodeError"),
    ("py:class", r"relink\.models\.base\.(BaseModel|BaseSettings)"),
    ("py:class", r"relink\.network\.base\.(BaseHTTPManager|BaseWebsocketManager)"),
    ("py:class", r"relink\.rest\.http\..+"),
    ("py:class", r"relink\.gateway\.queue\.base\..+"),
    ("py:class", r"relink\.gateway\.events\..+"),
    ("py:class", r"relink\.utils\.properties\.(T|T_co|_cached_property)"),
]

# -- Options for autodoc --
autodoc_default_options = {
    "members": True,
    "member-order": "groupwise",
    "undoc-members": True,
}
autodoc_typehints = "both"
autodoc_class_signature = "mixed"
napoleon_preprocess_types = True


# -- Options for HTML output --
html_theme = "furo"
html_static_path = ["_static"]
html_title = f"{project} {release} documentation"
html_favicon = "_static/logo.svg"

html_theme_options = {
    "light_logo": "light-banner.svg",
    "dark_logo": "dark-banner.svg",
    "sidebar_hide_name": True,
}


def _resolve_unqualified_python_reference(
    app: Sphinx,
    env: BuildEnvironment,
    node: pending_xref,
    contnode: nodes.TextElement,
) -> nodes.reference | None:
    """
    Attempts to resolve an unqualified Python reference to a full name.
    """
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


def setup(app: Sphinx) -> None:
    app.connect("missing-reference", _resolve_unqualified_python_reference)
