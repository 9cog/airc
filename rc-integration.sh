#!/bin/sh
# rc-integration.sh -- Integration helper for using Plan 9 rc shell with AI chat tools
#
# This script helps AI chat tools like aichat detect and work with the rc shell.
# It can be sourced in shell detection code to add rc shell support.

# Detect if current shell is rc
detect_rc_shell() {
    if [ -n "$0" ] && [ "$(basename "$0" 2>/dev/null)" = "rc" ]; then
        return 0
    fi
    
    # Check if SHELL environment variable points to rc
    if [ -n "$SHELL" ]; then
        shell_basename=$(basename "$SHELL" 2>/dev/null)
        if [ "$shell_basename" = "rc" ]; then
            return 0
        fi
    fi
    
    return 1
}

# Get rc shell history file location
get_rc_history_file() {
    # Check if $history is set in rc environment
    if [ -n "$history" ]; then
        echo "$history"
    # Check if $HOME is set
    elif [ -n "$HOME" ]; then
        echo "$HOME/.rc_history"
    else
        # Fallback to home directory detection
        home_dir=$(cd ~ && pwd)
        echo "$home_dir/.rc_history"
    fi
}

# Append command to rc shell history
# Usage: append_rc_history "command" exit_code
append_rc_history() {
    command="$1"
    exit_code="${2:-0}"
    history_file=$(get_rc_history_file)
    
    if [ -n "$history_file" ]; then
        # For rc shell, we simply append the command
        echo "$command" >> "$history_file"
    fi
}

# Export shell information for rc
export_rc_shell_info() {
    echo "rc"
}

# Export command format for rc
export_rc_shell_cmd() {
    # Find rc in PATH or use default location
    if command -v rc >/dev/null 2>&1; then
        command -v rc
    else
        echo "/usr/local/bin/rc"
    fi
}

# Export shell argument for rc (typically -c for command execution)
export_rc_shell_arg() {
    echo "-c"
}

# Main detection function that outputs all rc shell info
detect_and_export_rc() {
    if detect_rc_shell; then
        echo "SHELL_NAME=$(export_rc_shell_info)"
        echo "SHELL_CMD=$(export_rc_shell_cmd)"
        echo "SHELL_ARG=$(export_rc_shell_arg)"
        echo "SHELL_HISTORY=$(get_rc_history_file)"
        return 0
    fi
    return 1
}

# If script is being run directly (not sourced), run detection
# Note: This detection works in bash/zsh but may not work in all POSIX shells
if [ -n "$BASH_VERSION" ] && [ "${BASH_SOURCE[0]}" = "${0}" ]; then
    detect_and_export_rc
elif [ "$0" = "rc-integration.sh" ] || [ "$0" = "./rc-integration.sh" ]; then
    detect_and_export_rc
fi
