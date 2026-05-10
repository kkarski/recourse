#!/usr/bin/env bash
# Copy spectr skills, agents, and plugin rules to ~/.claude (physical copy).
# Overwrites any existing files in the target location.

set -e

SPECTR_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${SPECTR_ROOT}/skills"
TARGET_BASE="${HOME}/.claude/skills"

SOURCE_AGENTS="${SPECTR_ROOT}/agents"
TARGET_AGENTS="${HOME}/.claude/agents"

SOURCE_RULES="${SPECTR_ROOT}/.claude-plugin/rules"
TARGET_RULES="${HOME}/.claude-plugin/rules"

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

# Copy each top-level item under agents (files or folders), same remove-then-cp pattern as skills
if [[ ! -d "$SOURCE_AGENTS" ]]; then
  echo "Warning: agents folder not found at $SOURCE_AGENTS (skipping)" >&2
else
  mkdir -p "$TARGET_AGENTS"
  for agent_item in "$SOURCE_AGENTS"/*; do
    [[ -e "$agent_item" ]] || continue

    agent_name="$(basename "$agent_item")"
    agent_target="${TARGET_AGENTS}/${agent_name}"

    echo "Copying agents/$agent_name..."

    if [[ -e "$agent_target" ]]; then
      if [[ -d "$agent_target" ]]; then
        rm -rf "$agent_target"
      else
        rm -f "$agent_target"
      fi
    fi

    cp -r "$agent_item" "$agent_target"
    echo "  Copied $agent_item -> $agent_target"
  done
fi

# Copy each top-level item under .claude-plugin/rules
if [[ ! -d "$SOURCE_RULES" ]]; then
  echo "Warning: rules folder not found at $SOURCE_RULES (skipping)" >&2
else
  mkdir -p "$TARGET_RULES"
  for rule_item in "$SOURCE_RULES"/*; do
    [[ -e "$rule_item" ]] || continue

    rule_name="$(basename "$rule_item")"
    rule_target="${TARGET_RULES}/${rule_name}"

    echo "Copying rules/$rule_name..."

    if [[ -e "$rule_target" ]]; then
      if [[ -d "$rule_target" ]]; then
        rm -rf "$rule_target"
      else
        rm -f "$rule_target"
      fi
    fi

    cp -r "$rule_item" "$rule_target"
    echo "  Copied $rule_item -> $rule_target"
  done
fi

if [[ ! -f "$REFERENCE_FILE" ]]; then
  echo "Warning: Reference file not found at $REFERENCE_FILE" >&2
fi

echo "Copy complete."
