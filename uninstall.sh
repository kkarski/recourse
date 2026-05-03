#!/usr/bin/env bash
# Uninstall spectr skills from ~/.claude/skills
# Removes all symlinks and unmounts bind mounts created by install.sh
# Also removes any spectr-related items even if they no longer exist in source

set -e

SPECTR_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SOURCE="${SPECTR_ROOT}/skills"
TARGET_BASE="${HOME}/.claude/skills"

if [[ ! -d "$TARGET_BASE" ]]; then
  echo "No ~/.claude/skills directory found. Nothing to uninstall."
  exit 0
fi

echo "Uninstalling spectr skills from $TARGET_BASE..."

# Get list of skill names from source (if it exists)
declare -A SOURCE_SKILLS
if [[ -d "$SOURCE" ]]; then
  for skill_dir in "$SOURCE"/*/; do
    if [[ -d "$skill_dir" ]]; then
      skill_name="$(basename "$skill_dir")"
      if [[ "$skill_name" != "references" ]] && [[ "$skill_name" != "templates" ]]; then
        SOURCE_SKILLS["$skill_name"]=1
      fi
    fi
  done
fi

# Process all directories in target to find spectr-related items
for skill_target in "$TARGET_BASE"/*/; do
  if [[ ! -d "$skill_target" ]]; then
    continue
  fi
  
  skill_name="$(basename "$skill_target")"
  skill_target="${TARGET_BASE}/${skill_name}"
  
  # Check if this is a spectr skill by:
  # 1. Checking if it's a symlink/mount to our source
  # 2. Checking if the skill name exists in our source
  # 3. Checking if it contains spectr-related content
  
  is_spectr_skill=false
  
  # Check if it's mounted from our source
  if mountpoint -q "$skill_target" 2>/dev/null; then
    # Try to determine if it's from our source (mounts are harder to check)
    # We'll assume mounted directories in ~/.claude/skills are likely from us
    is_spectr_skill=true
  # Check if it's a symlink to our source
  elif [[ -L "$skill_target" ]]; then
    link_target="$(readlink -f "$skill_target")"
    if [[ "$link_target" == "$(readlink -f "$SOURCE/${skill_name}")" ]] || [[ "$link_target" == "$SOURCE/${skill_name}" ]]; then
      is_spectr_skill=true
    fi
  # Check if skill name exists in our source
  elif [[ -n "${SOURCE_SKILLS[$skill_name]}" ]]; then
    is_spectr_skill=true
  fi
  
  # If we determined it's a spectr skill, process it
  if [[ "$is_spectr_skill" == "true" ]]; then
    echo "Processing $skill_name..."
    
    # Remove symlink for references/how_to_use_questions.md
    skill_ref_link="${skill_target}/references/how_to_use_questions.md"
    if [[ -L "$skill_ref_link" ]]; then
      # Check if it points to our reference file before removing
      if [[ -f "${SPECTR_ROOT}/skills/references/how_to_use_questions.md" ]]; then
        if [[ "$(readlink -f "$skill_ref_link")" == "$(readlink -f "${SPECTR_ROOT}/skills/references/how_to_use_questions.md")" ]]; then
          rm -f "$skill_ref_link"
          echo "  Removed symlink: $skill_ref_link"
        fi
      else
        # Source file doesn't exist, but if it's a symlink, remove it anyway
        rm -f "$skill_ref_link"
        echo "  Removed symlink: $skill_ref_link"
      fi
    fi
    
    # Remove references directory only if it's empty and we created it
    # Don't remove if it has other content (preserve existing references folders)
    skill_ref_dir="${skill_target}/references"
    if [[ -d "$skill_ref_dir" ]] && [[ -z "$(ls -A "$skill_ref_dir" 2>/dev/null)" ]]; then
      rmdir "$skill_ref_dir" 2>/dev/null || true
      if [[ ! -d "$skill_ref_dir" ]]; then
        echo "  Removed empty references directory"
      fi
    fi
    
    # Unmount if it's a mount point
    if mountpoint -q "$skill_target" 2>/dev/null; then
      if umount "$skill_target" 2>/dev/null; then
        echo "  Unmounted: $skill_target"
      else
        echo "  Warning: Could not unmount $skill_target (may need sudo)" >&2
      fi
    fi
    
    # Remove if it's a symlink to the source
    if [[ -L "$skill_target" ]]; then
      link_target="$(readlink -f "$skill_target")"
      if [[ "$link_target" == "$(readlink -f "$SOURCE/${skill_name}")" ]] || [[ "$link_target" == "$SOURCE/${skill_name}" ]]; then
        rm -f "$skill_target"
        echo "  Removed symlink: $skill_target"
      fi
    # Remove if it's an empty directory (leftover from mount)
    elif [[ -d "$skill_target" ]] && [[ -z "$(ls -A "$skill_target" 2>/dev/null)" ]]; then
      rmdir "$skill_target" 2>/dev/null || true
      if [[ ! -d "$skill_target" ]]; then
        echo "  Removed empty directory: $skill_target"
      fi
    # If it's a directory that was mounted/symlinked but still exists, warn
    elif [[ -d "$skill_target" ]] && [[ -n "$(ls -A "$skill_target" 2>/dev/null)" ]]; then
      echo "  Warning: $skill_target exists and is not empty. Skipping removal." >&2
      echo "  You may need to manually remove it if it's no longer needed." >&2
    fi
  fi
done

echo "Uninstall complete."
