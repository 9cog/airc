# RC Shell Support Examples

This directory contains example code showing how to add Plan 9 rc shell support to AI chat tools and other applications that need shell detection.

## Files

### rc_shell_support.rs

Rust implementation showing how to add rc shell support to tools like [sigoden/aichat](https://github.com/sigoden/aichat).

**Key features:**
- Shell detection including rc
- History file location detection for rc (`$history` or `~/.rc_history`)
- History appending with proper format for rc

**Usage:**
```rust
let shell = detect_shell();
println!("Detected shell: {}", shell.name);

if let Some(history) = get_history_file(&shell.name) {
    println!("History file: {}", history.display());
}

append_to_shell_history(&shell.name, "echo hello", 0)
    .expect("Failed to append to history");
```

### rc_shell_support.py

Python implementation of rc shell support for Python-based AI tools.

**Usage:**
```bash
python3 rc_shell_support.py
```

Or import in your code:
```python
from rc_shell_support import detect_shell, get_history_file, append_to_shell_history

shell = detect_shell()
print(f"Detected shell: {shell.name}")

history_file = get_history_file(shell.name)
append_to_shell_history(shell.name, "echo hello", 0)
```

## Integration Guide

To add rc shell support to your AI chat tool:

1. **Add rc to shell detection logic:**
   - Check if `$SHELL` contains `rc`
   - Use `-c` as the command argument (same as bash, zsh, etc.)

2. **Add rc history file support:**
   - Check `$history` environment variable first
   - Fall back to `~/.rc_history` as default

3. **Use simple history format:**
   - For rc: just append the command line by line
   - No special timestamp or format needed (unlike zsh or fish)

## Testing

### Test shell detection:
```bash
# In bash or zsh
SHELL=/usr/local/bin/rc python3 rc_shell_support.py

# In rc shell
python3 rc_shell_support.py
```

### Test history appending:
```bash
# Set history file for testing
export history=/tmp/test_rc_history

# Run the example
python3 rc_shell_support.py

# Check the history file
cat /tmp/test_rc_history
```

## See Also

- [AI_INTEGRATION.md](../AI_INTEGRATION.md) - Comprehensive integration guide
- [rc-integration.sh](../rc-integration.sh) - Shell script for integration
- [rc-shell.rc](../rc-shell.rc) - RC shell script for shell info

## Contributing

If you've implemented rc shell support in your tool, please consider:
1. Adding your implementation as an example here
2. Updating the main AI_INTEGRATION.md documentation
3. Submitting a PR to the upstream tool (e.g., sigoden/aichat)
