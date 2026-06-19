#!/usr/bin/env bash
# Stop: block completion until review-design checklist runs when edits were made.
set -euo pipefail

input=$(cat)
session_id=$(echo "$input" | jq -r '.session_id // empty')
stop_hook_active=$(echo "$input" | jq -r '.stop_hook_active // false')
state_dir="$(cd "$(dirname "$0")" && pwd)/state"
flag="${state_dir}/edited-${session_id}"

if [[ -z "$session_id" ]]; then
  echo '{}'
  exit 0
fi

# Continuation after a prior Stop block — allow finish and clear state.
if [[ "$stop_hook_active" == "true" ]]; then
  rm -f "$flag"
  echo '{}'
  exit 0
fi

if [[ ! -f "$flag" ]]; then
  echo '{}'
  exit 0
fi

jq -n '{
  decision: "block",
  reason: "Run the review-design checklist on all files changed this session before finishing. Scope: changed files and immediate callers. Report findings only (Critical / Major / Minor) per the skill priorities. Do not implement fixes unless the user asks."
}'

exit 0
