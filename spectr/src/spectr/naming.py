"""Folder and file naming derived from spec titles."""

from __future__ import annotations

import re
from pathlib import Path

# Default title when ``spectr init`` receives an empty TITLE; used for fallback paths when no spec.html is discovered.
DEFAULT_INIT_TITLE = "Change set"

_QUESTIONS_COMPANION_SPEC_SUFFIX = re.compile(r"(.+)_spec\.html\Z", re.IGNORECASE)


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


def questions_companion_stem(spec_path: Path) -> str:
    """Basename segment for ``{stem}_questions.html`` next to ``spec_path``.

    When the spec file is named ``<stem>_spec.html``, ``stem`` is used so a flat layout like
    ``specs/foo_spec.html`` pairs with ``specs/foo_questions.html`` (not ``specs_questions.html``).
    Otherwise (e.g. ``spec.html``), the parent directory name is normalized like feature folders.
    """
    name = spec_path.name
    m = _QUESTIONS_COMPANION_SPEC_SUFFIX.fullmatch(name)
    if m:
        return m.group(1)
    return spec_folder_name_from_title(spec_path.parent.name or DEFAULT_INIT_TITLE)
