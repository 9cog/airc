# RC Shell AI Integration - Usage Guide

This guide provides practical examples of using the Plan 9 rc shell with AI chat tools.

## Quick Start

### 1. Set Up RC Shell

First, build and install rc:

```bash
make
sudo make install
```

### 2. Configure Your Environment

Add to your shell profile (e.g., `~/.bashrc`, `~/.zshrc`):

```bash
# Use rc as your shell for AI tools
export SHELL=/usr/local/bin/rc
```

Or, if you want to use rc as your default shell:

```bash
# Change your default shell
chsh -s /usr/local/bin/rc
```

### 3. Configure RC History

Create or edit `~/.rcrc`:

```rc
# Set history file location
history = $home^'/.rc_history'

# Optional: increase history size
# Note: rc doesn't have a built-in history limit,
# you may want to manage this with external tools
```

## Using with AI Chat Tools

### With aichat

If you're using [sigoden/aichat](https://github.com/sigoden/aichat):

```bash
# Install aichat
cargo install aichat

# Configure aichat with your API key
aichat --list-models  # Follow setup instructions

# Use aichat with rc shell
export SHELL=/usr/local/bin/rc
aichat -e "list all files in current directory"
```

The AI will generate rc-compatible commands like:

```rc
ls -la
```

### With Custom AI Tools

For developers building AI tools, use the integration scripts:

**POSIX Shell (for your AI tool wrapper):**

```bash
#!/bin/bash
# my-ai-tool.sh

# Source the rc integration
source /path/to/rc-integration.sh

# Detect shell
if detect_rc_shell; then
    echo "Running with rc shell"
    # Your AI tool logic here
fi

# Get history file
history_file=$(get_rc_history_file)

# Execute command and add to history
command="ls -la"
eval "$command"
exit_code=$?
append_rc_history "$command" $exit_code
```

**Python:**

```python
#!/usr/bin/env python3
# my_ai_tool.py

import sys
sys.path.append('/path/to/airc/examples')
from rc_shell_support import detect_shell, append_to_shell_history

# Detect shell
shell = detect_shell()
print(f"Using shell: {shell.name}")

# Generate and execute command
command = "ls -la"  # From your AI
import subprocess
result = subprocess.run([shell.cmd, shell.arg, command])

# Add to history
append_to_shell_history(shell.name, command, result.returncode)
```

## RC Shell Syntax Reference for AI Tools

When generating commands for rc shell, AI tools should be aware of these syntax patterns:

### Variables

```rc
# Simple variable
var = value

# List variable
files = (file1.txt file2.txt file3.txt)

# Access variable
echo $var
echo $files
```

### Command Substitution

```rc
# Command substitution
result = `{command}
files = `{ls *.txt}

# Use in echo
echo 'Files: '^`{ls}
```

### Conditionals

```rc
# Simple if
if (test -f file.txt) echo 'File exists'

# If-else
if (test -f file.txt) {
    echo 'File exists'
} else {
    echo 'File does not exist'
}

# Using test operators
if (~ $var value) echo 'var equals value'
```

### Loops

```rc
# For loop
for (file in *.txt) {
    echo $file
}

# While loop
while (test condition) {
    # commands
}
```

### Functions

```rc
# Define function
fn greet {
    echo 'Hello, '^$1
}

# Call function
greet 'World'
```

### Pipelines and Redirection

```rc
# Pipeline (same as other shells)
ls | grep txt

# Redirection
echo 'hello' > file.txt
cat < file.txt
command >[2=1]  # redirect stderr to stdout
```

## Common AI Command Patterns

### File Operations

**List files:**
```rc
ls -la
ls *.txt
```

**Find files:**
```rc
find . -name '*.txt'
```

**Copy/Move files:**
```rc
cp source.txt dest.txt
mv old.txt new.txt
```

### Text Processing

**Search in files:**
```rc
grep pattern file.txt
grep -r pattern .
```

**Count lines:**
```rc
wc -l file.txt
```

**Process text:**
```rc
cat file.txt | sed 's/old/new/g'
```

### System Information

**Current directory:**
```rc
pwd
```

**Disk usage:**
```rc
df -h
du -sh *
```

**Process list:**
```rc
ps aux
```

## Testing Your Integration

Use the provided test script:

```bash
cd /path/to/airc
./test-integration.sh
```

This will verify:
- Shell detection works correctly
- History file detection works
- Integration scripts function properly

## Troubleshooting

### AI tool doesn't detect rc

**Solution:** Ensure `$SHELL` is set:

```bash
export SHELL=/usr/local/bin/rc
echo $SHELL  # Should output: /usr/local/bin/rc
```

### Commands not appearing in history

**Solution:** Check history configuration in `~/.rcrc`:

```rc
history = $home^'/.rc_history'
```

Verify the file is writable:

```bash
touch ~/.rc_history
chmod 644 ~/.rc_history
```

### Syntax errors in generated commands

**Solution:** Ensure your AI tool is generating rc-compatible syntax. Most basic Unix commands work the same, but watch for:

- Command substitution: Use `` `{cmd} `` not `$(cmd)`
- Test conditions: Use `test` or `~` operator
- Variable assignment: Use `var = value` not `var=value`

## Integration Examples

### Example 1: Simple Command Generation

```bash
# User asks: "Show me all text files"
# AI generates for rc:
ls *.txt

# Compared to bash (same):
ls *.txt
```

### Example 2: Command with Substitution

```bash
# User asks: "Show current directory in a message"
# AI generates for rc:
echo 'Current directory: '^`{pwd}

# Compared to bash:
echo "Current directory: $(pwd)"
```

### Example 3: Loop over Files

```bash
# User asks: "Print each text file name"
# AI generates for rc:
for (f in *.txt) echo $f

# Compared to bash:
for f in *.txt; do echo $f; done
```

## Contributing

If you've integrated rc shell support into your AI tool:

1. Add your example to this guide
2. Submit a PR with your integration code
3. Share your experience in the discussions

## Resources

- [Plan 9 rc manual](http://doc.cat-v.org/plan_9/4th_edition/papers/rc)
- [AI_INTEGRATION.md](AI_INTEGRATION.md) - Technical integration details
- [examples/](examples/) - Code examples in Rust and Python
- [sigoden/aichat](https://github.com/sigoden/aichat) - Reference AI chat tool

## License

This documentation is provided under the same license as the rc shell itself.
