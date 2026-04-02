"""Folder and file naming derived from spec titles."""

from __future__ import annotations

# Default title when ``spectr init`` receives an empty TITLE; used for fallback paths when no spec.html is discovered.
DEFAULT_INIT_TITLE = "Change set"


def spec_folder_name_from_title(title: str) -> str:
    """
    Directory name (typically created in cwd by ``spectr init``): whitespace
    normalized, then spaces replaced with underscores. Empty titles become
    ``spec``. Path separators in the title are replaced with underscores.
    """
    t = " ".join(title.split())
    for sep in ("/", "\\"):
        t = t.replace(sep, "_")
    if not t:
        return "spec"
    return t.replace(" ", "_")
