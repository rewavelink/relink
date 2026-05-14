import ast
import datetime
import re

from sonolink import _version  # type: ignore

UNRELEASED_SECTION_RE = (
    r"(?P<section>`Unreleased`_\n-+\n\n.*?)(?=\n\.\. _vp|\n\.\. _unreleased:|\Z)"
)
CHANGELOG_INTRO_RE = (
    r"(?P<intro>\.\. currentmodule:: .*?\n\n\.\. _whats_new:\n\nChangelog\n=+\n\n"
    r"This page keeps a detailed human friendly rendering of what's new and changed\n"
    r"in specific versions\.\n\n)"
)
RELEASE_SECTION_RE = r"(?P<section>\.\. _vp[^\n]+:\n\nv[^\n]+\n-+\n\n.*?)(?=\n\.\. _vp|\n\.\. _unreleased:|\Z)"
UNRELEASED_LINK_RE = r"(?P<link>\.\. _unreleased: [^\n]+)\n?"

UNRELEASED_SECTION_TEXT = """
`Unreleased`_
--------------

These changes are available on the `main` branch, but have not yet been released.

Added
~~~~~~

Changed
~~~~~~~

Fixed
~~~~~~

Removed
~~~~~~~

Deprecated
~~~~~~~~~~~
"""

CHANGELOG_CATEGORIES = ("Added", "Changed", "Fixed", "Removed", "Deprecated")


def edit_version() -> None:
    current_version = _version.version_info
    new_version = current_version
    print(f"Current version: {current_version}")

    with open("sonolink/_version.py", "r") as f:
        content = f.read()

    tree = ast.parse(content, type_comments=True)
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "version_info":
                    version_call: ast.Call = node.value  # type: ignore
                    keywords = version_call.keywords
                    for keyword in keywords:
                        if keyword.arg == "minor":
                            keyword.value = ast.Constant(
                                value=current_version.minor + 1
                            )
                        elif keyword.arg == "patch":
                            keyword.value = ast.Constant(value=0)
                        elif keyword.arg == "release_level":
                            keyword.value = ast.Constant(value="alpha")

                    new_version = _version.VersionInfo(
                        major=current_version.major,
                        minor=current_version.minor + 1,
                        patch=0,
                        release_level="alpha",
                    )

                    print(f"Bumped version to: {new_version}")

    new_content = ast.unparse(tree)
    with open("sonolink/_version.py", "w") as f:
        f.write(new_content)

    edit_docs(current_version)


def format_file():
    import subprocess

    subprocess.run(
        [
            "uv",
            "run",
            "ruff",
            "check",
            "sonolink/_version.py",
            "--select",
            "I",
            "--fix",
        ],
        check=True,
    )
    subprocess.run(
        ["uv", "run", "ruff", "format", "sonolink/_version.py"],
        check=True,
    )


def edit_docs(current_version: _version.VersionInfo) -> None:
    with open("docs/changelog.rst", "r") as f:
        content = f.read()

    changelog_intro = re.search(CHANGELOG_INTRO_RE, content, re.DOTALL)
    unreleased_section = re.search(UNRELEASED_SECTION_RE, content, re.DOTALL)
    unreleased_link = re.search(UNRELEASED_LINK_RE, content)

    if changelog_intro is None:
        raise ValueError("Could not find changelog header in docs/changelog.rst")
    if unreleased_section is None:
        raise ValueError("Could not find Unreleased section in docs/changelog.rst")
    if unreleased_link is None:
        raise ValueError("Could not find Unreleased link in docs/changelog.rst")

    release_sections = re.findall(RELEASE_SECTION_RE, content, re.DOTALL)

    version_anchor = f".. _vp{current_version.major}p{current_version.minor}p{current_version.patch}:"

    current_date = datetime.datetime.now(datetime.UTC).strftime("%Y-%m-%d")

    version_heading = f"v{current_version.as_str()} - {current_date}"
    version_underline = "-" * len(version_heading)
    unreleased_body = _extract_release_body(unreleased_section.group("section"))

    new_release_section = (
        f"{version_anchor}\n\n"
        f"{version_heading}\n"
        f"{version_underline}\n\n"
        f"{unreleased_body}\n\n"
    )

    new_content = (
        f"{changelog_intro.group('intro')}"
        f"{UNRELEASED_SECTION_TEXT.strip()}\n\n"
        f"{new_release_section}"
        f"{''.join(release_sections).lstrip()}"
        f"\n{unreleased_link.group('link')}\n"
    )

    with open("docs/changelog.rst", "w") as f:
        f.write(new_content)


def _extract_release_body(unreleased_section: str) -> str:
    category_blocks: list[str] = []
    current_title: str | None = None
    current_underline: str | None = None
    current_body: list[str] = []
    lines = unreleased_section.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]
        next_line = lines[i + 1] if i + 1 < len(lines) else None

        if line in CHANGELOG_CATEGORIES and next_line and set(next_line) == {"~"}:
            if current_title is not None:
                body = "\n".join(current_body).strip()
                if body:
                    category_blocks.append(
                        f"{current_title}\n{current_underline}\n\n{body}"
                    )
            current_title = line
            current_underline = next_line
            current_body = []
            i += 2
            while i < len(lines) and lines[i] == "":
                i += 1
            continue

        if current_title is not None:
            current_body.append(line)
        i += 1

    if current_title is not None:
        body = "\n".join(current_body).strip()
        if body:
            category_blocks.append(f"{current_title}\n{current_underline}\n\n{body}")

    return "\n".join(category_blocks).rstrip()


edit_version()
format_file()
