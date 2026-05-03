#!/usr/bin/env bash
# Copy spectr skills to ~/.claude/skills (physical copy).
# Overwrites any existing files in the target location.

set -e

SPECTR_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${SPECTR_ROOT}/skills"
TARGET_BASE="${HOME}/.claude/skills"

if [[ ! -d "$SOURCE" ]]; then
  echo "Error: skills folder not found at $SOURCE" >&2
  exit 1
fi

mkdir -p "$TARGET_BASE"

# Reference file for copying
REFERENCE_FILE="${SPECTR_ROOT}/skills/references/how_to_use_questions.md"

# Copy each individual skill folder
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
  
  echo "Copying $skill_name..."
  
  # Remove existing target if it exists (to ensure clean copy)
  if [[ -e "$skill_target" ]]; then
    if [[ -d "$skill_target" ]]; then
      rm -rf "$skill_target"
    else
      rm -f "$skill_target"
    fi
  fi
  
  # Copy the entire skill folder
  cp -r "$skill_source" "$skill_target"
  echo "  Copied $skill_source -> $skill_target"
  
  # Copy references/how_to_use_questions.md into the skill's references folder
  # This overwrites any existing file or symlink in the TARGET location only
  if [[ -f "$REFERENCE_FILE" ]]; then
    skill_ref_dir="${skill_target}/references"
    mkdir -p "$skill_ref_dir"
    skill_ref_file="${skill_ref_dir}/how_to_use_questions.md"
    # Remove existing file/symlink in target location to avoid "same file" error
    # This only modifies ~/.claude/skills, not the spectr source folder
    if [[ -e "$skill_ref_file" ]]; then
      rm -f "$skill_ref_file"
    fi
    # Copy the reference file to target location
    # Use absolute path to ensure we're copying from source to target
    cp "$REFERENCE_FILE" "$skill_ref_file"
    echo "  Copied reference file: $skill_ref_file"
  fi
done

if [[ ! -f "$REFERENCE_FILE" ]]; then
  echo "Warning: Reference file not found at $REFERENCE_FILE" >&2
fi

echo "Copy complete."
