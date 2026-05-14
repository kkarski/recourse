#!/usr/bin/env bash
# Build and install the Spectr CLI from a checkout of this repository.
# Default: create or reuse .venv at the repo root and pip install -e spectr/

set -euo pipefail

usage() {
  cat <<'EOF'
Usage: build-install-spectr.sh [options]

Creates or reuses a virtualenv, upgrades pip/setuptools/wheel, optionally builds a
wheel under spectr/dist/, then installs the CLI (editable by default).

Options:
  -h, --help          Show this help and exit.
  --user              Use 'pip install --user' (installs to user site, e.g.
                      ~/.local/bin). Implies --skip-venv; ensure ~/.local/bin
                      is on your PATH.
  --no-editable       Install with 'pip install' instead of 'pip install -e'.
  --skip-venv         Do not create or activate a venv; use the current Python.
  --wheel             Also run 'pip wheel' and write wheels to spectr/dist/.
  --venv PATH         Virtualenv directory (default: <repo>/.venv).

Environment:
  VENV                Same as --venv when set and --venv not passed.

Examples:
  ./scripts/build-install-spectr.sh
  ./scripts/build-install-spectr.sh --user
  ./scripts/build-install-spectr.sh --wheel
  VENV=~/venvs/spectr ./scripts/build-install-spectr.sh --skip-venv
EOF
}

EDITABLE=1
SKIP_VENV=0
BUILD_WHEEL=0
PIP_USER=0
VENV_DIR="${VENV:-}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    -h|--help)
      usage
      exit 0
      ;;
    --user) PIP_USER=1 ;;
    --no-editable) EDITABLE=0 ;;
    --skip-venv) SKIP_VENV=1 ;;
    --wheel) BUILD_WHEEL=1 ;;
    --venv)
      VENV_DIR="${2:-}"
      if [[ -z "$VENV_DIR" ]]; then
        echo "error: --venv requires a path" >&2
        exit 1
      fi
      shift
      ;;
    *)
      echo "error: unknown option: $1" >&2
      usage >&2
      exit 1
      ;;
  esac
  shift
done

if [[ $PIP_USER -eq 1 ]]; then
  SKIP_VENV=1
fi

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PACKAGE_DIR="$REPO_ROOT/spectr"

if [[ ! -f "$PACKAGE_DIR/pyproject.toml" ]]; then
  echo "error: expected spectr/pyproject.toml under $REPO_ROOT" >&2
  exit 1
fi

if [[ $SKIP_VENV -eq 0 ]]; then
  if [[ -z "$VENV_DIR" ]]; then
    VENV_DIR="$REPO_ROOT/.venv"
  fi
  if [[ ! -d "$VENV_DIR" ]]; then
    if ! python3 -m venv "$VENV_DIR"; then
      rm -rf "$VENV_DIR"
      if command -v uv >/dev/null 2>&1; then
        uv venv --seed "$VENV_DIR"
      else
        echo "error: failed to create venv with python3 -m venv." >&2
        echo "Install python3-venv (e.g. apt install python3-venv) or install uv (https://docs.astral.sh/uv/)." >&2
        exit 1
      fi
    fi
  fi
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
fi

if [[ $PIP_USER -eq 1 ]]; then
  if [[ -n "${VIRTUAL_ENV:-}" ]]; then
    echo "error: --user install cannot run inside an active virtualenv. Run 'deactivate' first." >&2
    exit 1
  fi
  if [[ -x /usr/bin/python3 ]]; then
    py=(/usr/bin/python3)
  elif [[ -x /usr/local/bin/python3 ]]; then
    py=(/usr/local/bin/python3)
  elif command -v python3 >/dev/null 2>&1; then
    py=(python3)
  else
    echo "error: python3 not found for --user install" >&2
    exit 1
  fi
elif [[ $SKIP_VENV -eq 0 ]]; then
  py=(python)
else
  if command -v python3 >/dev/null 2>&1; then
    py=(python3)
  else
    py=(python)
  fi
fi

pip_install() {
  local extra=()
  [[ $PIP_USER -eq 1 ]] && extra+=(--user)
  "${py[@]}" -m pip install "${extra[@]}" "$@"
}

pip_install -U pip setuptools wheel

if [[ $BUILD_WHEEL -eq 1 ]]; then
  mkdir -p "$PACKAGE_DIR/dist"
  "${py[@]}" -m pip wheel "$PACKAGE_DIR" -w "$PACKAGE_DIR/dist"
fi

if [[ $EDITABLE -eq 1 ]]; then
  pip_install -e "$PACKAGE_DIR"
else
  pip_install "$PACKAGE_DIR"
fi

if [[ $PIP_USER -eq 1 ]]; then
  export PATH="${HOME}/.local/bin:${PATH}"
fi

spectr --version
printf 'Installed: %s\n' "$(command -v spectr)"
if [[ $PIP_USER -eq 1 ]]; then
  echo "Ensure ~/.local/bin is on PATH in your shell profile if 'spectr' is not found." >&2
fi
