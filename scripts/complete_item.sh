#!/bin/zsh
# Mark an open item on the Apple Reminders "Grocery" list as completed (exact name match, case-insensitive).
# Usage: scripts/complete_item.sh "<item name>" [list-name]
# Exit 0 if at least one item was completed, 1 if no match.
set -euo pipefail
ITEM="${1:?usage: complete_item.sh \"<item name>\" [list-name]}"
LIST="${2:-Grocery}"
COUNT=$(osascript <<APPLESCRIPT
tell application "Reminders"
  set matches to (every reminder of list "$LIST" whose name is "$ITEM" and completed is false)
  repeat with r in matches
    set completed of r to true
  end repeat
  return count of matches
end tell
APPLESCRIPT
)
if [[ "$COUNT" -eq 0 ]]; then
  echo "no open item named '$ITEM' on list '$LIST'" >&2
  exit 1
fi
echo "completed $COUNT: $ITEM"
