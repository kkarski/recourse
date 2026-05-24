#!/usr/bin/env bash
# Create a local venv (unless skipped), build wheels when asked, and install the spectr CLI.
# Run from the spectr package directory: ./install.sh

set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$ROOT"

PYTHON="${PYTHON:-python3}"
VENV_DIR="${VENV_DIR:-$ROOT/.venv}"
DIST_DIR="$ROOT/dist"

DO_BUILD=0
DO_INSTALL=1
DO_TEST=0
USE_VENV=1
EDITABLE=1
USER_INSTALL=0

usage() {
  cat <<'EOF'
Usage: ./install.sh [options]

Default: create or reuse .venv, upgrade pip/setuptools/wheel, editable install.

Options:
  --build          Build wheel and sdist into dist/ (also installs build tooling)
  --no-install     Build only; skip installing the package
  --no-venv        Install with the active interpreter (or --user) instead of .venv
  --user           pip install --user (implies --no-venv)
  --no-editable    pip install . instead of pip install -e .
  --test           Install pytest and run the test suite after install
  -h, --help       Show this help
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --build)
      DO_BUILD=1
      shift
      ;;
    --no-install)
      DO_INSTALL=0
      shift
      ;;
    --no-venv)
      USE_VENV=0
      shift
      ;;
    --user)
      USE_VENV=0
      USER_INSTALL=1
      shift
      ;;
    --no-editable)
      EDITABLE=0
      shift
      ;;
    --test)
      DO_TEST=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

if [[ "$DO_BUILD" -eq 0 && "$DO_INSTALL" -eq 0 && "$DO_TEST" -eq 0 ]]; then
  echo "Nothing to do: enable install (default), --build, or --test." >&2
  usage >&2
  exit 2
fi

if [[ "$USE_VENV" -eq 1 ]]; then
  if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating virtual environment at $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
  fi
  # shellcheck source=/dev/null
  source "$VENV_DIR/bin/activate"
  PYTHON="$VENV_DIR/bin/python"
fi

echo "Using Python: $($PYTHON -c 'import sys; print(sys.executable)')"
"$PYTHON" -m pip install -U pip setuptools wheel

if [[ "$DO_BUILD" -eq 1 ]]; then
  "$PYTHON" -m pip install -U build
  rm -rf "$DIST_DIR"
  mkdir -p "$DIST_DIR"
  "$PYTHON" -m build --outdir "$DIST_DIR"
  echo "Built distributions in $DIST_DIR"
fi

if [[ "$DO_INSTALL" -eq 1 ]]; then
  install_args=()
  if [[ "$USER_INSTALL" -eq 1 ]]; then
    install_args+=(--user)
  fi
  if [[ "$EDITABLE" -eq 1 ]]; then
    "$PYTHON" -m pip install "${install_args[@]}" -e .
  else
    "$PYTHON" -m pip install "${install_args[@]}" .
  fi
  if command -v spectr >/dev/null 2>&1; then
    spectr --version
  else
    "$PYTHON" -m spectr --version
  fi
fi

if [[ "$DO_TEST" -eq 1 ]]; then
  "$PYTHON" -m pip install pytest
  "$PYTHON" -m pytest tests/ -q
fi

if [[ "$USE_VENV" -eq 1 ]]; then
  echo "Activate the environment: source $VENV_DIR/bin/activate"
fi
