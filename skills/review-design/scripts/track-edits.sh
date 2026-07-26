#!/usr/bin/env bash
# PostToolUse (Edit|Write): mark that this session edited files.
set -euo pipefail

input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id // empty')

if [[ -z "$session_id" ]]; then
  exit 0
fi

state_dir="$(cd "$(dirname "$0")" && pwd)/state"
mkdir -p "$state_dir"
touch "${state_dir}/edited-${session_id}"

exit 0
