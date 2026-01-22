#!/usr/bin/env python3
"""
rc_shell_support.py
Example Python code showing how to add rc shell support to AI chat tools

This file demonstrates the minimal changes needed to add Plan 9 rc shell
support to AI chat tools in Python.
"""

import os
import time
from pathlib import Path
from typing import Optional, Dict


class Shell:
    """Shell configuration"""
    
    def __init__(self, name: str, cmd: str, arg: str):
        self.name = name
        self.cmd = cmd
        self.arg = arg
    
    def __repr__(self):
        return f"Shell(name={self.name!r}, cmd={self.cmd!r}, arg={self.arg!r})"


def detect_shell() -> Shell:
    """
    Detect the current shell, including rc shell support
    
    Returns:
        Shell: The detected shell configuration
    """
    shell_path = os.environ.get('SHELL', '/bin/sh')
    shell_name = Path(shell_path).stem.lower()
    
    # Handle special case for nushell
    if shell_name == 'nu':
        shell_name = 'nushell'
    
    # Determine shell argument based on shell name
    if shell_name in ['powershell', 'pwsh']:
        shell_arg = '-Command'
    elif shell_name == 'cmd':
        shell_arg = '/C'
    else:
        # rc, bash, zsh, fish, sh all use -c
        shell_arg = '-c'
    
    return Shell(name=shell_name, cmd=shell_path, arg=shell_arg)


def get_history_file(shell_name: str) -> Optional[Path]:
    """
    Get the history file path for a given shell, including rc shell support
    
    Args:
        shell_name: The name of the shell
    
    Returns:
        Optional[Path]: The path to the history file, or None if not found
    """
    home_dir = Path.home()
    
    if shell_name == 'rc':
        # rc shell support - check $history variable or use default
        history_env = os.environ.get('history')
        if history_env:
            return Path(history_env)
        return home_dir / '.rc_history'
    
    elif shell_name in ['bash', 'sh']:
        histfile = os.environ.get('HISTFILE')
        if histfile:
            return Path(histfile)
        return home_dir / '.bash_history'
    
    elif shell_name == 'zsh':
        histfile = os.environ.get('HISTFILE')
        if histfile:
            return Path(histfile)
        return home_dir / '.zsh_history'
    
    elif shell_name == 'nushell':
        config_dir = Path.home() / '.config'
        return config_dir / 'nushell' / 'history.txt'
    
    elif shell_name == 'fish':
        return home_dir / '.local' / 'share' / 'fish' / 'fish_history'
    
    elif shell_name in ['powershell', 'pwsh']:
        if os.name == 'nt':  # Windows
            appdata = Path(os.environ.get('APPDATA', home_dir / 'AppData' / 'Roaming'))
            return (appdata / 'Microsoft' / 'Windows' / 'PowerShell' / 
                   'PSReadLine' / 'ConsoleHost_history.txt')
        else:  # Unix-like
            return (home_dir / '.local' / 'share' / 'powershell' / 
                   'PSReadLine' / 'ConsoleHost_history.txt')
    
    elif shell_name == 'ksh':
        return home_dir / '.ksh_history'
    
    elif shell_name == 'tcsh':
        return home_dir / '.history'
    
    return None


def append_to_shell_history(shell_name: str, command: str, exit_code: int = 0) -> bool:
    """
    Append a command to the shell history, including rc shell support
    
    Args:
        shell_name: The name of the shell
        command: The command to append
        exit_code: The exit code of the command (default: 0)
    
    Returns:
        bool: True if successful, False otherwise
    """
    history_file = get_history_file(shell_name)
    if not history_file:
        return False
    
    # Replace newlines with spaces
    command = command.replace('\n', ' ')
    now = int(time.time())
    
    # Format based on shell type
    if shell_name in ['rc', 'bash', 'sh']:
        # rc shell: simple format, just append the command
        history_txt = command
    elif shell_name == 'fish':
        history_txt = f"- cmd: {command}\n  when: {now}"
    elif shell_name == 'zsh':
        history_txt = f": {now}:{exit_code};{command}"
    else:
        history_txt = command
    
    try:
        # Ensure parent directory exists
        history_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Append to history file
        with open(history_file, 'a', encoding='utf-8') as f:
            f.write(history_txt + '\n')
        return True
    except Exception as e:
        print(f"Error appending to history: {e}")
        return False


def main():
    """Example usage"""
    shell = detect_shell()
    print(f"Detected shell: {shell.name}")
    print(f"Shell command: {shell.cmd}")
    print(f"Shell argument: {shell.arg}")
    
    history_file = get_history_file(shell.name)
    if history_file:
        print(f"History file: {history_file}")
    else:
        print("No history file configured for this shell")
    
    # Example: append a command to history
    command = "echo hello world"
    exit_code = 0
    if append_to_shell_history(shell.name, command, exit_code):
        print(f"Successfully appended command to history")
    else:
        print(f"Failed to append command to history")


if __name__ == '__main__':
    main()
