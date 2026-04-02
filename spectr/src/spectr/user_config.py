from __future__ import annotations

import os
import sys
from pathlib import Path

ENV_ROLE = "SPECTR_ROLE"


def default_config_path() -> Path:
    return Path.home() / ".spectr" / "config"


def read_role(*, config_path: Path | None = None) -> str | None:
    """Return the configured author role from env then file, or None if unset."""
    env = os.environ.get(ENV_ROLE, "").strip()
    if env:
        return env
    path = config_path or default_config_path()
    if not path.is_file():
        return None
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if line.startswith("role="):
            val = line[5:].strip()
            return val or None
    return None


def resolve_role(*, cli_role: str | None = None, config_path: Path | None = None) -> str | None:
    """Effective role: ``--role`` flag wins, then ``SPECTR_ROLE``, then config file."""
    if cli_role is not None and str(cli_role).strip():
        return str(cli_role).strip()
    return read_role(config_path=config_path)


def argv_requests_help(argv: list[str] | None = None) -> bool:
    """True if -h/--help appears anywhere (subcommand help)."""
    args = argv if argv is not None else sys.argv
    return any(a in ("-h", "--help") for a in args[1:])
