#!/usr/bin/env bash
# Mount recourse/skills under ~/.claude/skills (bind mount).
# Run from the recourse repo; requires sufficient privileges for mount.

set -e

RECOURSE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${RECOURSE_ROOT}/skills"
TARGET="${HOME}/.claude/skills"

if [[ ! -d "$SOURCE" ]]; then
  echo "Error: skills folder not found at $SOURCE" >&2
  exit 1
fi

mkdir -p "$(dirname "$TARGET")"

if [[ -e "$TARGET" ]]; then
  if mountpoint -q "$TARGET" 2>/dev/null; then
    echo "Already mounted: $TARGET"
    exit 0
  fi
  if [[ -d "$TARGET" ]] && [[ -n "$(ls -A "$TARGET" 2>/dev/null)" ]]; then
    echo "Error: $TARGET exists and is non-empty. Move or back it up, then run again." >&2
    exit 1
  fi
  rmdir "$TARGET" 2>/dev/null || true
fi

mkdir -p "$TARGET"
if mount --bind "$SOURCE" "$TARGET" 2>/dev/null; then
  echo "Mounted $SOURCE -> $TARGET"
else
  echo "Bind mount failed (may need sudo). Creating symlink instead." >&2
  rmdir "$TARGET" 2>/dev/null || true
  ln -sf "$SOURCE" "$TARGET"
  echo "Symlinked $SOURCE -> $TARGET"
fi
