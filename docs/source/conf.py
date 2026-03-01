import datetime
import os
import sys

sys.path.insert(0, os.path.abspath("../../relink"))

# -- Project information -----------------------------------------------------
project = "relink"
author = "vmphase, Soheab, DA-344"
copyright = f"{datetime.date.today().year}, {author}"
release = "1.0.0a"

# -- General configuration ---------------------------------------------------
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
exclude_patterns = ["_build"]

# -- Options for autodoc ----------------------------------------------------
autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "undoc-members": True,
    "show-inheritance": True,
    "inherited-members": True,
}
autodoc_typehints = "both"

# -- Options for HTML output -------------------------------------------------
html_theme = "furo"
html_static_path = ["_static"]
