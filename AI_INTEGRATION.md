# AI Chat Integration for Plan 9 rc Shell

This document describes how to integrate the Plan 9 rc shell with AI chat tools like [sigoden/aichat](https://github.com/sigoden/aichat).

## Overview

The Plan 9 rc shell is a clean, simple shell with a syntax similar to C. This integration provides shell detection and history management functionality that allows AI chat tools to work seamlessly with rc.

## Shell Detection

AI chat tools need to detect which shell is being used to generate appropriate commands. The rc shell can be detected using:

1. **Environment Variable**: Check if `$SHELL` contains `rc`
2. **Process Name**: Check if the current process is named `rc`
3. **Shell Prompt**: Check for rc-specific prompt patterns

### For AI Tool Developers

To add rc shell support to your tool, use the following detection logic:

```rust
// Rust example (similar to sigoden/aichat)
fn detect_shell() -> Shell {
    let shell_path = env::var("SHELL").unwrap_or_default();
    let shell_name = Path::new(&shell_path)
        .file_stem()
        .and_then(|s| s.to_str())
        .unwrap_or("sh");
    
    match shell_name {
        "rc" => Shell::new("rc", "rc", "-c"),
        "bash" => Shell::new("bash", "bash", "-c"),
        // ... other shells
        _ => Shell::new("sh", "/bin/sh", "-c"),
    }
}
```

```python
# Python example
import os
from pathlib import Path

def detect_shell():
    shell = os.environ.get('SHELL', '/bin/sh')
    shell_name = Path(shell).stem
    
    if shell_name == 'rc':
        return {'name': 'rc', 'cmd': 'rc', 'arg': '-c'}
    elif shell_name == 'bash':
        return {'name': 'bash', 'cmd': 'bash', 'arg': '-c'}
    # ... other shells
    else:
        return {'name': 'sh', 'cmd': '/bin/sh', 'arg': '-c'}
```

## History File Location

The rc shell uses a history file for command recall. The history file location can be:

1. **`$history` variable**: If set in rc, this takes precedence
2. **Default location**: `$HOME/.rc_history`

### For AI Tool Developers

To support rc history file location:

```rust
// Rust example
fn get_history_file(shell: &str) -> Option<PathBuf> {
    match shell {
        "rc" => {
            env::var("history")
                .ok()
                .map(PathBuf::from)
                .or_else(|| Some(home_dir()?.join(".rc_history")))
        }
        "bash" | "sh" => {
            env::var("HISTFILE")
                .ok()
                .map(PathBuf::from)
                .or_else(|| Some(home_dir()?.join(".bash_history")))
        }
        // ... other shells
        _ => None,
    }
}
```

```python
# Python example
def get_history_file(shell_name):
    if shell_name == 'rc':
        history = os.environ.get('history')
        if history:
            return history
        home = os.path.expanduser('~')
        return os.path.join(home, '.rc_history')
    elif shell_name in ['bash', 'sh']:
        histfile = os.environ.get('HISTFILE')
        if histfile:
            return histfile
        home = os.path.expanduser('~')
        return os.path.join(home, '.bash_history')
    # ... other shells
    return None
```

## Appending to History

When AI tools execute commands, they should append them to the shell history. For rc shell:

```rust
// Rust example
fn append_to_shell_history(shell: &str, command: &str, exit_code: i32) -> io::Result<()> {
    if let Some(history_file) = get_history_file(shell) {
        let command = command.replace('\n', " ");
        
        match shell {
            "rc" => {
                // For rc, simply append the command
                let mut file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(&history_file)?;
                writeln!(file, "{}", command)?;
            }
            "fish" => {
                // fish format
                let now = now_timestamp();
                let history_txt = format!("- cmd: {}\n  when: {}", command, now);
                let mut file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(&history_file)?;
                writeln!(file, "{}", history_txt)?;
            }
            "zsh" => {
                // zsh format
                let now = now_timestamp();
                let history_txt = format!(": {}:0;{}", now, command);
                let mut file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(&history_file)?;
                writeln!(file, "{}", history_txt)?;
            }
            _ => {
                // bash/sh and others: simple format
                let mut file = OpenOptions::new()
                    .create(true)
                    .append(true)
                    .open(&history_file)?;
                writeln!(file, "{}", command)?;
            }
        }
    }
    Ok(())
}
```

## Using rc with aichat

If you're using [sigoden/aichat](https://github.com/sigoden/aichat), you can enable rc shell support by:

1. **Set your SHELL environment variable**:
   ```sh
   export SHELL=/usr/local/bin/rc
   ```

2. **Configure history in rc**:
   Add to your `~/.rcrc`:
   ```rc
   history = $home^'/.rc_history'
   ```

3. **Use aichat with rc syntax**:
   ```sh
   aichat -e "list all files in current directory"
   ```
   
   aichat should now generate rc-compatible commands.

## Integration Scripts

This repository provides helper scripts for integration:

### rc-integration.sh

A POSIX shell script that provides rc shell detection functions:

```sh
# Source the integration script
. ./rc-integration.sh

# Detect if current shell is rc
if detect_rc_shell; then
    echo "Running in rc shell"
fi

# Get rc history file location
history_file=$(get_rc_history_file)

# Append command to history
append_rc_history "echo hello" 0
```

### rc-shell.rc

An rc shell script that provides shell information:

```rc
# Source in your rc session
. ./rc-shell.rc

# Get shell name
rcshell_info

# Get history file location
rcshell_history

# Get all detection info
rcshell_detect
```

## Command Syntax Differences

When generating commands for rc, AI tools should be aware of syntax differences:

| Feature | bash/sh | rc |
|---------|---------|-----|
| Command substitution | `$(cmd)` or `` `cmd` `` | `` `{cmd} `` |
| Variable | `$var` or `${var}` | `$var` |
| List | `item1 item2` | `(item1 item2)` |
| For loop | `for i in *; do echo $i; done` | `for(i in *) echo $i` |
| If statement | `if [ condition ]; then cmd; fi` | `if(condition) cmd` |
| Pipeline | `cmd1 | cmd2` | `cmd1 | cmd2` |
| Redirection | `cmd > file` | `cmd > file` |
| Background | `cmd &` | `cmd &` |

### Example Command Conversions

**List files with details:**
- bash: `ls -la`
- rc: `ls -la` (same)

**Find and delete files:**
- bash: `find . -name '*.tmp' -delete`
- rc: `find . -name '*.tmp' -delete` (same)

**Get current directory:**
- bash: `pwd`
- rc: `pwd` (same)

**Command substitution:**
- bash: `echo "Current dir: $(pwd)"`
- rc: ``echo 'Current dir: '^`{pwd}``

**Loop over files:**
- bash: `for f in *.txt; do echo $f; done`
- rc: `for(f in *.txt) echo $f`

## Contributing

To add rc shell support to your AI chat tool:

1. Add rc to your shell detection logic
2. Add rc history file location support
3. Optionally, adjust command generation to prefer rc-compatible syntax
4. Test with rc shell users

## Troubleshooting

### Build Issues

**Problem:** Build fails with "parse.tab.h: No such file or directory"

**Solution:** This should be automatically fixed by the Makefile. If you still encounter this:
```bash
make clean
make
```

See BUILD.md for more detailed build troubleshooting.

### Integration Issues

**Problem:** AI tool doesn't detect rc shell

**Solution:** 
1. Verify SHELL environment variable: `echo $SHELL`
2. Make sure it points to rc: `export SHELL=/path/to/rc`
3. Test detection: `./demo-integration.sh`

**Problem:** Commands not added to history

**Solution:**
1. Check history variable is set in ~/.rcrc: `history = $home^'/.rc_history'`
2. Verify history file is writable: `touch ~/.rc_history`
3. Check AI tool has history integration enabled

**Problem:** Generated commands don't work in rc

**Solution:**
- Most basic Unix commands work the same
- For advanced features, check command syntax differences in this document
- RC uses different syntax for: command substitution (`` `{cmd} ``), loops (`for(var in list) cmd`), conditionals (`if(test) cmd`)

### Testing the Integration

Run the comprehensive demo:
```bash
./demo-integration.sh
```

Run the test suite:
```bash
./test-integration.sh
```

Test shell detection manually:
```bash
# POSIX shell
. ./rc-integration.sh
detect_rc_shell && echo "RC detected"

# RC shell
./rc -c '. ./rc-shell.rc; rcshell_info'
```

## References

- [Plan 9 rc shell manual](http://doc.cat-v.org/plan_9/4th_edition/papers/rc)
- [sigoden/aichat](https://github.com/sigoden/aichat) - AI chat tool with shell integration
- [This repository](https://github.com/9cog/airc) - Plan 9 rc shell implementation

## License

These integration scripts and documentation are provided under the same license as the rc shell itself.
