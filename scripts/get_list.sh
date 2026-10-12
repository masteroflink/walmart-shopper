#!/bin/zsh
# Print open (not completed) items from the Apple Reminders "Grocery" list, one per line.
# Usage: scripts/get_list.sh [list-name]
set -euo pipefail
LIST="${1:-Grocery}"
osascript <<APPLESCRIPT
tell application "Reminders"
  set names to name of every reminder of list "$LIST" whose completed is false
  set AppleScript's text item delimiters to linefeed
  return names as text
end tell
APPLESCRIPT
