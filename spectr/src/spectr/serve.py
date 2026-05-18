"""Local HTTP server: serve the repo from cwd; Spectr specs open in a wrapper frame with chrome CSS/JS."""

from __future__ import annotations

import html
import importlib.resources
import sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlencode, urlparse


_SPECTR_PREFIX = "/__spectr__/"
_STATIC_FILES = {
    "view.css": ("view.css", "text/css; charset=utf-8"),
    "view.js": ("view.js", "application/javascript; charset=utf-8"),
    "chrome.css": ("chrome.css", "text/css; charset=utf-8"),
    "chrome.js": ("chrome.js", "application/javascript; charset=utf-8"),
}


def _load_static(filename: str) -> bytes:
    return importlib.resources.files("spectr").joinpath("static", filename).read_bytes()


def _wants_raw(query: str) -> bool:
    q = parse_qs(query, keep_blank_values=True)
    vals = q.get("spectr-raw")
    if vals is None:
        return False
    v = vals[-1]
    if v == "":
        return True
    return str(v).lower() in ("1", "true", "yes", "on")


def _iframe_raw_url(request_path: str) -> str:
    """Same resource as ``request_path``, with ``spectr-raw=1`` for iframe embedding."""
    p = urlparse(request_path)
    q = parse_qs(p.query, keep_blank_values=True)
    q["spectr-raw"] = ["1"]
    pairs = [(k, v) for k in sorted(q.keys()) for v in q[k]]
    qs = urlencode(pairs)
    return p.path + ("?" + qs if qs else "")


def _render_wrapper(*, iframe_src: str, title: str, label: str) -> bytes:
    tpl = (
        importlib.resources.files("spectr")
        .joinpath("static/wrapper.html")
        .read_text(encoding="utf-8")
    )
    page = (
        tpl.replace("{{TITLE}}", html.escape(title))
        .replace("{{LABEL}}", html.escape(label))
        .replace("{{IFRAME_SRC}}", html.escape(iframe_src))
    )
    return page.encode("utf-8")


def _is_spec_html(path: Path) -> bool:
    name = path.name.lower()
    return name == "spec.html" or name.endswith("_spec.html")


def make_handler_class(root: Path):
    root_resolved = root.resolve()

    class SpectrServeHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(root_resolved), **kwargs)

        def log_message(self, fmt: str, *args) -> None:
            sys.stderr.write(
                "%s - - [%s] %s\n"
                % (self.address_string(), self.log_date_time_string(), fmt % args)
            )

        def do_GET(self):  # noqa: N802
            parsed = urlparse(self.path)
            path_only = unquote(parsed.path)

            if path_only.startswith(_SPECTR_PREFIX):
                name = path_only[len(_SPECTR_PREFIX) :].lstrip("/")
                if name in _STATIC_FILES:
                    filename, ctype = _STATIC_FILES[name]
                    data = _load_static(filename)
                    self.send_response(200)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                self.send_error(404, "Not Found")
                return

            translated = Path(self.translate_path(self.path))
            try:
                translated = translated.resolve()
            except OSError:
                super().do_GET()
                return

            if not translated.is_relative_to(root_resolved):
                self.send_error(403, "Forbidden")
                return

            if (
                translated.is_file()
                and _is_spec_html(translated)
                and not _wants_raw(parsed.query)
            ):
                iframe_src = _iframe_raw_url(self.path)
                label = translated.name
                title = f"Spectr · {label}"
                body = _render_wrapper(
                    iframe_src=iframe_src,
                    title=title,
                    label=label,
                )
                self.send_response(200)
                self.send_header("Content-Type", "text/html; charset=utf-8")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
                return

            super().do_GET()

    return SpectrServeHandler


def run_serve(root: Path, bind_host: str, port: int) -> None:
    handler_cls = make_handler_class(root)
    server = ThreadingHTTPServer((bind_host, port), handler_cls)
    host_display = bind_host
    if ":" in bind_host and not bind_host.startswith("["):
        host_display = f"[{bind_host}]"
    print(
        f"Serving {root.resolve()} at http://{host_display}:{port}/ (Ctrl+C to stop)",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.", file=sys.stderr)
    finally:
        server.server_close()
