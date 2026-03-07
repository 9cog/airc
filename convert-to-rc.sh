#!/bin/sh
# convert-to-rc.sh -- Convert bash/sh command syntax to Plan 9 rc shell syntax
#
# Usage:
#   ./convert-to-rc.sh 'bash_command'
#   echo 'bash_command' | ./convert-to-rc.sh
#   ./convert-to-rc.sh --reference
#   ./convert-to-rc.sh < script.sh
#
# This is a wrapper around examples/bash_to_rc_converter.py.
# Requires python3 to be installed.

# Find the directory containing this script
script_dir="$(cd "$(dirname "$0")" && pwd)"
converter="$script_dir/examples/bash_to_rc_converter.py"

if [ ! -f "$converter" ]; then
    echo "Error: $converter not found" >&2
    exit 1
fi

exec python3 "$converter" "$@"
