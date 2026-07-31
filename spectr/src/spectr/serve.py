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


def _parent_href(request_path: str) -> str:
    """Directory URL one level above ``request_path`` (always ends with ``/``)."""
    path = unquote(urlparse(request_path).path)
    parts = [p for p in path.split("/") if p]
    if len(parts) <= 1:
        return "/"
    return "/" + "/".join(parts[:-1]) + "/"


def _breadcrumb_segments(request_path: str) -> list[tuple[str, str | None]]:
    """Labels and hrefs for the chrome breadcrumb.

    Each tuple is ``(label, href)``. ``href`` is ``None`` for the current page.
    """
    path = unquote(urlparse(request_path).path)
    parts = [p for p in path.split("/") if p]
    crumbs: list[tuple[str, str | None]] = [("Spectr", "/")]
    if not parts:
        return crumbs
    acc: list[str] = []
    for i, part in enumerate(parts):
        acc.append(part)
        if i == len(parts) - 1:
            crumbs.append((part, None))
        else:
            crumbs.append((part, "/" + "/".join(acc) + "/"))
    return crumbs


_BREADCRUMB_SEP = (
    '<svg class="size-4 shrink-0 fill-current text-zinc-300 dark:text-zinc-600" '
    'viewBox="0 0 16 16" aria-hidden="true">'
    '<path d="M6.22 4.22a.75.75 0 0 1 1.06 0l3.25 3.25a.75.75 0 0 1 0 1.06l-3.25 '
    '3.25a.75.75 0 0 1-1.06-1.06L8.94 8 6.22 5.28a.75.75 0 0 1 0-1.06Z"/>'
    "</svg>"
)

_PARENT_ICON = (
    '<svg class="size-4 shrink-0 fill-current" viewBox="0 0 16 16" aria-hidden="true">'
    '<path fill-rule="evenodd" clip-rule="evenodd" '
    'd="M9.78 4.22a.75.75 0 0 1 0 1.06L7.06 8l2.72 2.72a.75.75 0 1 1-1.06 '
    '1.06L5.47 8.53a.75.75 0 0 1 0-1.06l3.25-3.25a.75.75 0 0 1 1.06 0Z"/>'
    "</svg>"
)


def _render_breadcrumb_html(request_path: str) -> str:
    parent = _parent_href(request_path)
    parts: list[str] = [
        '<nav class="spectr-chrome-nav flex min-w-0 flex-1 items-center gap-x-2" '
        'aria-label="Breadcrumb">',
        f'<a href="{html.escape(parent, quote=True)}" '
        'class="spectr-chrome-up inline-flex shrink-0 items-center gap-x-1.5 rounded-lg '
        "px-2 py-1.5 text-sm/5 font-medium text-zinc-950 hover:bg-zinc-950/5 "
        'dark:text-white dark:hover:bg-white/5" '
        'title="Parent folder">',
        _PARENT_ICON,
        '<span class="hidden sm:inline">Parent</span>',
        "</a>",
        '<span class="hidden h-4 w-px shrink-0 bg-zinc-950/10 sm:block dark:bg-white/10" '
        'aria-hidden="true"></span>',
        '<ol class="flex min-w-0 items-center gap-x-2 overflow-hidden">',
    ]
    segments = _breadcrumb_segments(request_path)
    for i, (label, href) in enumerate(segments):
        if i:
            parts.append(f'<li class="flex shrink-0 items-center" aria-hidden="true">{_BREADCRUMB_SEP}</li>')
        safe_label = html.escape(label)
        if href is None:
            parts.append(
                f'<li class="min-w-0 truncate text-sm/6 text-zinc-500 dark:text-zinc-400" '
                f'aria-current="page">{safe_label}</li>'
            )
        else:
            safe_href = html.escape(href, quote=True)
            parts.append(
                f'<li class="flex shrink-0 items-center">'
                f'<a href="{safe_href}" '
                f'class="text-sm/6 font-medium text-zinc-950 hover:underline '
                f'dark:text-white">{safe_label}</a></li>'
            )
    parts.append("</ol></nav>")
    return "".join(parts)


def _render_wrapper(*, iframe_src: str, title: str, request_path: str) -> bytes:
    tpl = (
        importlib.resources.files("spectr")
        .joinpath("static/wrapper.html")
        .read_text(encoding="utf-8")
    )
    page = (
        tpl.replace("{{TITLE}}", html.escape(title))
        .replace("{{BREADCRUMB}}", _render_breadcrumb_html(request_path))
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
                    request_path=self.path,
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
