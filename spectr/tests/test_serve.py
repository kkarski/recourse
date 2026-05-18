"""Tests for ``spectr serve`` HTTP handler."""

from __future__ import annotations

import threading
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from spectr.serve import _iframe_raw_url, _wants_raw, make_handler_class


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


@pytest.fixture
def serve_root(tmp_path: Path) -> Path:
    (tmp_path / "plain.txt").write_text("hi", encoding="utf-8")
    (tmp_path / "my_spec.html").write_text(
        "<html><head><title>t</title></head><body>x</body></html>",
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

        with urllib.request.urlopen(f"{base}/my_spec.html?spectr-raw=1") as r:
            raw = r.read().decode("utf-8")
        assert "<iframe" not in raw
        assert "<title>t</title>" in raw

        with urllib.request.urlopen(f"{base}/__spectr__/view.css") as r:
            css = r.read().decode("utf-8")
        assert "body" in css
        assert "#spectr-doc-nav" in css

        with urllib.request.urlopen(f"{base}/__spectr__/view.js") as r:
            view_js = r.read().decode("utf-8")
        assert "spectrEnhanceView" in view_js
        assert "renderAllMarkdown" in view_js

        with urllib.request.urlopen(f"{base}/__spectr__/chrome.js") as r:
            js = r.read().decode("utf-8")
        assert "spectr-view-css" in js
        assert "spectr-view-js" in js
        assert "spectr-markdown-it" in js
        assert "dompurify" in js.lower()
        assert "jquery" in js.lower()

        with urllib.request.urlopen(f"{base}/plain.txt") as r:
            assert r.read() == b"hi"
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=2)
