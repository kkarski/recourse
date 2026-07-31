"""Tests for ``spectr serve`` HTTP handler."""

from __future__ import annotations

import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from spectr.serve import (
    _breadcrumb_segments,
    _iframe_raw_url,
    _parent_href,
    _wants_raw,
    make_handler_class,
)


@pytest.mark.parametrize(
    "qs,expected",
    [
        ("", False),
        ("spectr-raw=1", True),
        ("spectr-raw=true", True),
        ("x=1&spectr-raw=1", True),
        ("spectr-raw=0", False),
    ],
)
def test_wants_raw(qs: str, expected: bool) -> None:
    assert _wants_raw(qs) is expected


def test_iframe_raw_url_appends_param() -> None:
    assert _iframe_raw_url("/a/my_spec.html").endswith("spectr-raw=1")
    assert "spectr-raw=1" in _iframe_raw_url("/a/my_spec.html?foo=bar")


@pytest.mark.parametrize(
    "path,expected",
    [
        ("/my_spec.html", "/"),
        ("/age_probability/age_probability_spec.html", "/age_probability/"),
        ("/a/b/c_spec.html", "/a/b/"),
        ("/a/b/c_spec.html?x=1", "/a/b/"),
    ],
)
def test_parent_href(path: str, expected: str) -> None:
    assert _parent_href(path) == expected


def test_breadcrumb_segments() -> None:
    assert _breadcrumb_segments("/age_probability/age_probability_spec.html") == [
        ("Spectr", "/"),
        ("age_probability", "/age_probability/"),
        ("age_probability_spec.html", None),
    ]
    assert _breadcrumb_segments("/my_spec.html") == [
        ("Spectr", "/"),
        ("my_spec.html", None),
    ]


@pytest.fixture
def serve_root(tmp_path: Path) -> Path:
    (tmp_path / "plain.txt").write_text("hi", encoding="utf-8")
    (tmp_path / "my_spec.html").write_text(
        "<html><head><title>t</title></head><body>x</body></html>",
        encoding="utf-8",
    )
    nested = tmp_path / "age_probability"
    nested.mkdir()
    (nested / "age_probability_spec.html").write_text(
        "<html><head><title>age</title></head><body>y</body></html>",
        encoding="utf-8",
    )
    return tmp_path


def test_spec_wrapper_and_raw_and_static(serve_root: Path) -> None:
    handler = make_handler_class(serve_root)
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    port = server.server_address[1]

    def run() -> None:
        server.serve_forever(poll_interval=0.05)

    t = threading.Thread(target=run, daemon=True)
    t.start()

    try:
        base = f"http://127.0.0.1:{port}"
        with urllib.request.urlopen(f"{base}/my_spec.html") as r:
            wrap = r.read().decode("utf-8")
        assert "<iframe" in wrap
        assert "spectr-raw=1" in wrap
        assert "/__spectr__/chrome.css" in wrap
        assert "/__spectr__/chrome.js" in wrap
        assert "@tailwindcss/browser" in wrap
        assert "font-sans" in wrap
        assert 'href="/"' in wrap
        assert "spectr-chrome-up" in wrap
        assert "Parent" in wrap

        with urllib.request.urlopen(
            f"{base}/age_probability/age_probability_spec.html"
        ) as r:
            nested_wrap = r.read().decode("utf-8")
        assert 'href="/age_probability/"' in nested_wrap
        assert "age_probability_spec.html" in nested_wrap
        assert "aria-label=\"Breadcrumb\"" in nested_wrap

        with urllib.request.urlopen(f"{base}/my_spec.html?spectr-raw=1") as r:
            raw = r.read().decode("utf-8")
        assert "<iframe" not in raw
        assert "<title>t</title>" in raw

        with urllib.request.urlopen(f"{base}/__spectr__/view.css") as r:
            css = r.read().decode("utf-8")
        assert "@apply" in css
        assert "#spectr-doc-nav" in css
        assert "spectr-nav-item" in css
        assert "spectr-sid-badge" in css
        assert "spectr-nav-h4" not in css
        assert "spectr-doc-nav-toggle" not in css
        assert "spectr-tablist" in css
        assert "spectr-tab" in css
        assert "spectr-ac-clause--when" in css
        assert "spectr-ac-kw" in css
        assert "spectr-term-tip" in css
        assert "spectr-term-tip-panel" in css

        with urllib.request.urlopen(f"{base}/__spectr__/view.js") as r:
            view_js = r.read().decode("utf-8")
        assert "spectrEnhanceView" in view_js
        assert "renderAllMarkdown" in view_js
        assert "spectr-sid-badge" in view_js
        assert "spectr-nav-item" in view_js
        assert '"h1, h2, h3"' in view_js or "'h1, h2, h3'" in view_js
        assert "h1, h2, h3, h4" not in view_js
        assert "spectr-doc-nav-toggle" not in view_js
        assert "spectr-tabs" in view_js
        assert "buildTabs" in view_js
        assert 'setAttribute("role", "tablist")' in view_js
        assert "Definitions" in view_js
        assert "Use Cases" in view_js
        assert "renderAcceptanceCriteria" in view_js
        assert "spectr-ac-clause" in view_js
        assert "linkifyGlossaryTerms" in view_js
        assert "spectr-term-tip" in view_js
        assert "collectGlossaryPhrases" in view_js
        assert "wireGlossaryTermLinks" not in view_js
        assert "headingNavLabel" in view_js
        with urllib.request.urlopen(f"{base}/__spectr__/chrome.js") as r:
            js = r.read().decode("utf-8")
        assert "spectr-view-css" in js
        assert "spectr-view-js" in js
        assert "spectr-tailwind-browser" in js
        assert "text/tailwindcss" in js
        assert "spectr-markdown-it" in js
        assert "dompurify" in js.lower()
        assert "jquery" in js.lower()

        with urllib.request.urlopen(f"{base}/plain.txt") as r:
            assert r.read() == b"hi"
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=2)
