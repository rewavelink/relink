from __future__ import annotations

from typing import TYPE_CHECKING

from bs4 import BeautifulSoup

if TYPE_CHECKING:
    from sphinx.application import Sphinx


def _inject_home_link(
    app: Sphinx,
    pagename: str,
    templatename: str,
    context: dict[str, object],
    doctree: object,
) -> None:
    nav_tree = context.get("furo_navigation_tree")
    pathto = context.get("pathto")
    if not isinstance(nav_tree, str) or not nav_tree or not callable(pathto):
        return

    home_href = pathto("index")

    soup = BeautifulSoup(nav_tree, "html.parser")
    top_list = soup.find("ul")
    if top_list is None:
        return

    # Avoid duplicating the synthetic Home item on repeated renders.
    for item in top_list.find_all("li", recursive=False):
        link = item.find("a", recursive=False)
        if link is not None and link.get("href") == home_href:
            return

    home_item = soup.new_tag("li")
    classes = ["toctree-l1"]
    if pagename == "index":
        classes.extend(["current", "current-page"])
    home_item["class"] = classes

    home_link = soup.new_tag(
        "a",
        attrs={
            "class": ["reference", "internal"],
            "href": home_href,
        },
    )
    home_link.string = "Home"
    home_item.append(home_link)

    top_list.insert(0, home_item)
    context["furo_navigation_tree"] = str(soup)


def setup(app: Sphinx) -> dict[str, bool]:
    app.connect("html-page-context", _inject_home_link, priority=600)
    return {"parallel_read_safe": True}
