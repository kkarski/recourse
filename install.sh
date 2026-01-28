#!/usr/bin/env bash
# Install recourse skills under ~/.claude/skills (bind mount or symlink).
# Run from the recourse repo; requires sufficient privileges for mount.

set -e

RECOURSE_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${RECOURSE_ROOT}/skills"
TARGET_BASE="${HOME}/.claude/skills"

if [[ ! -d "$SOURCE" ]]; then
  echo "Error: skills folder not found at $SOURCE" >&2
  exit 1
fi

mkdir -p "$TARGET_BASE"

# Reference file for symlinking
REFERENCE_FILE="${RECOURSE_ROOT}/skills/references/how_to_use_questions.md"

# Mount or symlink each individual skill folder
for skill_dir in "$SOURCE"/*/; do
  if [[ ! -d "$skill_dir" ]]; then
    continue
  fi
  
  skill_name="$(basename "$skill_dir")"
  
  # Skip references and templates directories (not skills)
  if [[ "$skill_name" == "references" ]] || [[ "$skill_name" == "templates" ]]; then
    echo "Skipping $skill_name (not a skill folder)"
    continue
  fi
  
  skill_source="$skill_dir"
  skill_target="${TARGET_BASE}/${skill_name}"
  
  # Track if we should attempt mount/symlink
  should_mount=true
  
  # Skip if already mounted
  if mountpoint -q "$skill_target" 2>/dev/null; then
    echo "Already mounted: $skill_target"
    should_mount=false
  # Skip if target exists and is not empty (preserve existing content)
  elif [[ -e "$skill_target" ]]; then
    if [[ -d "$skill_target" ]] && [[ -n "$(ls -A "$skill_target" 2>/dev/null)" ]]; then
      # Check if it's already a symlink to the source
      if [[ -L "$skill_target" ]] && [[ "$(readlink -f "$skill_target")" == "$(readlink -f "$skill_source")" ]]; then
        echo "Already symlinked: $skill_target -> $skill_source"
      else
        echo "Skipping $skill_name: target exists and is non-empty"
      fi
      should_mount=false
    else
      # Remove empty target if it exists
      rmdir "$skill_target" 2>/dev/null || rm -f "$skill_target" 2>/dev/null || true
    fi
  fi
  
  # Attempt to mount, fall back to symlink (only if needed)
  if [[ "$should_mount" == "true" ]]; then
    if mount --bind "$skill_source" "$skill_target" 2>/dev/null; then
      echo "Mounted $skill_source -> $skill_target"
    else
      # Bind mount failed (may need sudo), create symlink instead
      ln -sf "$skill_source" "$skill_target"
      echo "Symlinked $skill_source -> $skill_target"
    fi
  fi
  
  # Create symlink for references/how_to_use_questions.md in the skill folder
  # This happens regardless of whether the folder was already mounted/existed
  # The symlink is created in the target location (~/.claude/skills), not the source
  # We symlink the individual file, not the references folder, to preserve existing content
  if [[ -f "$REFERENCE_FILE" ]]; then
    # Use the target path (mounted location) for creating the symlink
    skill_ref_dir="${skill_target}/references"
    # Create references directory if it doesn't exist (won't fail if it already exists)
    mkdir -p "$skill_ref_dir"
    skill_ref_link="${skill_ref_dir}/how_to_use_questions.md"
    # Use absolute path to the source reference file
    # Only create/update the symlink if it doesn't exist or is already a symlink
    if [[ ! -e "$skill_ref_link" ]] || [[ -L "$skill_ref_link" ]]; then
      rm -f "$skill_ref_link"
      ln -sf "$REFERENCE_FILE" "$skill_ref_link"
      echo "Created symlink: $skill_ref_link -> $REFERENCE_FILE"
    else
      echo "Skipping $skill_ref_link: file exists and is not a symlink (preserving existing content)"
    fi
  fi
done

if [[ ! -f "$REFERENCE_FILE" ]]; then
  echo "Warning: Reference file not found at $REFERENCE_FILE" >&2
fi
