# Plan 9 RC Shell Syntax Guide for AI Tools

This guide provides a comprehensive reference for AI chat tools generating commands
for the Plan 9 rc shell. RC has a clean, minimal syntax that differs from bash/sh
in several important ways.

## Quick Reference

| Feature | bash/sh | rc |
|---------|---------|-----|
| Command substitution | `$(cmd)` | `` `{cmd} `` |
| Variable | `$var` or `${var}` | `$var` |
| Concatenation | `"${a}b"` | `$a^b` |
| Variable length | `${#var}` | `$#var` |
| List | `"a" "b" "c"` | `(a b c)` |
| Assignment | `var=value` | `var = value` |
| For loop | `for i in x; do...done` | `for(i in x) {...}` |
| If | `if [...]; then...fi` | `if(...) {...}` |
| While | `while [...]; do...done` | `while(...) {...}` |
| Function | `f() {...}` | `fn f {...}` |
| Stderr redirect | `2>&1` | `>[2=1]` |
| Glob | `*.txt` | `*.txt` (same) |
| Pipeline | `cmd1 \| cmd2` | `cmd1 \| cmd2` (same) |
| Background | `cmd &` | `cmd &` (same) |

## Command Substitution

In rc, command substitution uses backtick-brace syntax:

```rc
# Get hostname
host = `{hostname}

# Use in a string (concatenation with ^)
echo 'Hello from '^`{hostname}

# Multi-word substitution (splits on $ifs, defaults to whitespace)
files = `{ls *.txt}
for(f in $files) echo $f
```

**Note:** `$(cmd)` does **not** work in rc. Always use `` `{cmd} ``.

## Variables

```rc
# Assignment (spaces around = are required)
name = Alice
count = 0
path = /usr/local/bin

# Access variable
echo $name

# String concatenation with ^
greeting = 'Hello, '^$name^'!'
echo $greeting

# Variable length
echo $#name      # number of elements (1 for scalar, n for list)

# List variables
items = (apple banana cherry)
echo $items       # prints: apple banana cherry
echo $#items      # prints: 3
echo $items(1)    # prints: apple (1-indexed)
echo $items(2)    # prints: banana

# Variable in path (use ^ for concatenation)
config = $HOME^'/.config'
```

### Special Variables

| Variable | Meaning |
|----------|---------|
| `$0` | Script name |
| `$*` | All arguments |
| `$#` | Argument count |
| `$1`, `$2`, ... | Positional arguments |
| `$status` | Exit status of last command |
| `$pid` | Current process ID |
| `$home` | Home directory |
| `$path` | Command search path (list) |
| `$prompt` | Shell prompt |
| `$ifs` | Internal field separator |
| `$history` | History file path |

## Control Flow

### If Statement

```rc
# Simple if
if(test -f file.txt) echo 'file exists'

# If with block
if(test -f file.txt) {
    echo 'file exists'
    cat file.txt
}

# If-else
if(test -f file.txt) {
    echo 'file exists'
} else {
    echo 'file not found'
}

# If-else if-else
if(test -d /etc) {
    echo 'is directory'
} else if(test -f /etc) {
    echo 'is file'
} else {
    echo 'does not exist'
}

# String matching with ~
if(~ $SHELL */rc) echo 'using rc shell'

# Test a command's success
if(grep -q pattern file.txt) echo 'found'
```

### For Loop

```rc
# Loop over list
for(f in *.txt) {
    echo $f
}

# Loop over explicit list
for(color in red green blue) {
    echo $color
}

# Loop with command output
for(f in `{ls -1}) {
    echo $f
}

# Single-command for (no braces needed)
for(f in *.md) echo $f
```

### While Loop

```rc
# While with test
while(test -f lockfile) {
    echo 'waiting...'
    sleep 1
}

# While reading stdin
while(read line) {
    echo 'got: '^$line
}
```

### Switch Statement

```rc
# Switch on a value
switch($1) {
case help
    echo 'Usage: ...'
case start
    start_service
case stop
    stop_service
case *
    echo 'Unknown command: '^$1
}
```

## Functions

```rc
# Define a function
fn greet {
    echo 'Hello, '^$1^'!'
}

# Call the function
greet World

# Function with multiple statements
fn backup {
    src = $1
    dst = $2
    cp -r $src $dst
    echo 'Backed up '^$src^' to '^$dst
}

# Remove a function
fn greet {}  # or: rfn greet

# Check if function exists
if(~ `{whatis greet 2>/dev/null} 'fn greet'*) echo 'greet is defined'
```

## String Operations

```rc
# Concatenation with ^
echo $HOME^'/.config'
echo 'Hello, '^$name^'!'

# Quote strings with single quotes (no interpolation)
echo 'This is a literal $variable'

# Multi-word strings need quotes
msg = 'Hello World'
echo $msg

# String comparison with ~
if(~ $name Alice) echo 'Hello Alice'

# Pattern matching with ~
if(~ $file *.txt) echo 'is a text file'
if(~ $file *.{txt,md}) echo 'is text or markdown'

# Check if variable is empty
if(~ $var '') echo 'var is empty'
if(! ~ $var '') echo 'var is not empty'
```

## Redirection

```rc
# Standard redirection (same as bash)
echo hello > file.txt
echo hello >> file.txt      # append
cat < file.txt

# Redirect stderr to stdout (rc syntax)
make >[2=1]

# Redirect stderr to /dev/null
make >[2]/dev/null

# Redirect both stdout and stderr to file
make > output.txt >[2=1]

# Here document
cat <<EOF
line 1
line 2
EOF

# Here string (if supported)
grep pattern <<<'text to search'
```

## Pipelines

```rc
# Standard pipeline (same as bash)
ls | sort | uniq

# Pipeline with redirection
find . -name '*.txt' | xargs grep pattern >[2]/dev/null

# Named pipe (process substitution equivalent)
diff <{cmd1} <{cmd2}
```

## Lists and Globbing

```rc
# Create a list
files = (README.md COPYING AUTHORS)

# Glob patterns work as in bash
ls *.txt
ls ?.c

# Recursive glob (if supported by system)
ls **/*.py

# Brace expansion
files = *.{c,h}

# Null glob (non-matching globs return empty)
files = (*.nonexistent)  # empty list

# List operations
all = ($list1 $list2)          # concatenate lists
first = $list(1)               # first element (1-indexed)
last = $list($#list)           # last element
```

## Error Handling

```rc
# Check exit status
cmd
if(! ~ $status 0) echo 'command failed with status '^$status

# Logical AND (&&)
test -f file && cat file

# Logical OR (||)
test -f file || echo 'not found'

# Combine: run cmd1, and if it succeeds run cmd2
cmd1 && cmd2

# Run cmd1, and if it fails run cmd2
cmd1 || cmd2

# Exit on error (no set -e equivalent; check status manually)
do_thing
if(! ~ $status 0) { echo 'failed'; exit 1 }
```

## Common Patterns for AI Tools

### File Operations

```rc
# List files
ls -la

# Find files
find . -name '*.txt' -type f

# Check if file exists
if(test -f file.txt) echo 'exists'

# Read file line by line
for(line in `{cat file.txt}) echo $line

# Process each file
for(f in *.txt) {
    echo 'Processing '^$f
    wc -l $f
}
```

### Text Processing

```rc
# Search in files
grep -r pattern .

# Count lines
wc -l file.txt

# Replace text
sed 's/old/new/g' file.txt

# Get field from output
df -h | awk '{print $5}'
```

### System Information

```rc
# Current directory
pwd

# System info
uname -a

# Process list
ps aux

# Disk usage
df -h
du -sh *
```

### Network Operations

```rc
# Download file
curl -O https://example.com/file.txt
wget https://example.com/file.txt

# Check connectivity
ping -c 3 example.com
```

### Script Template

```rc
#!/usr/local/bin/rc

# RC script template
# Usage: script.rc [options] argument

# Check arguments
if(~ $#* 0) {
    echo 'Usage: script.rc argument'
    exit 1
}

arg = $1

# Main logic
echo 'Processing '^$arg

# Cleanup on exit
fn cleanup {
    echo 'Cleaning up...'
}

# Note: rc doesn't have 'trap', use explicit cleanup before exit
```

## Differences from Bash: Key Points for AI

1. **No `$(...)` command substitution** — use `` `{...} `` instead
2. **Spaces required in assignments** — `var = value`, not `var=value`
3. **Different loop/conditional syntax** — `for(i in x) {...}` not `for i in x; do...done`
4. **Concatenation with `^`** — `$var^text`, not `"${var}text"` 
5. **No `[[ ]]` or `[ ]` builtins** — use `test` command or `~` operator
6. **Functions with `fn`** — `fn name {...}` not `name() {...}`
7. **Stderr redirect** — `>[2=1]` not `2>&1`
8. **No `export`** — all variables are automatically available; use assignment
9. **Lists are first-class** — `items = (a b c)` creates a proper list
10. **Most basic Unix commands work the same** — `ls`, `grep`, `find`, etc.

## Automated Conversion

Use the included converter to translate bash commands to rc:

```bash
# Convert a single command
python3 examples/bash_to_rc_converter.py 'for f in *.txt; do echo $f; done'

# Convert a script
python3 examples/bash_to_rc_converter.py < script.sh > script.rc

# Show conversion reference
python3 examples/bash_to_rc_converter.py --reference
```

## References

- [Plan 9 rc manual page](http://doc.cat-v.org/plan_9/4th_edition/papers/rc)
- [Byron Rakitzis rc README](../README)
- [AI Integration Guide](AI_INTEGRATION.md)
- [Bash-to-rc converter](examples/bash_to_rc_converter.py)
