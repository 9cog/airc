#!/usr/bin/env python3
"""
bash_to_rc_converter.py
Converts bash/sh command syntax to Plan 9 rc shell syntax.

This is useful for AI chat tools that need to generate rc-compatible commands
from bash patterns, or for users migrating bash scripts to rc.

Usage:
    python3 bash_to_rc_converter.py 'command'
    echo 'command' | python3 bash_to_rc_converter.py
    python3 bash_to_rc_converter.py --reference

Can also be imported as a module:
    from bash_to_rc_converter import convert_to_rc, convert_line
"""

import re
import sys
from typing import List, Tuple


# Translation rules: list of (description, pattern, replacement) tuples.
# Applied in order, so ordering matters for overlapping patterns.
SUBSTITUTION_RULES: List[Tuple[str, str, str]] = [
    # Command substitution: $(cmd) -> `{cmd}
    ("command substitution", r'\$\(([^)]*)\)', r'`{\1}'),

    # Arithmetic expansion: $((expr)) -> awk (rc has no built-in arithmetic)
    # Note: rc has no built-in arithmetic; flag for manual review
    ("arithmetic expansion", r'\$\(\(([^)]*)\)\)', r'`{awk "BEGIN{print \1}"}  # TODO: rc has no arithmetic; use awk or dc'),

    # Variable length: ${#var} -> $#var
    ("variable length", r'\$\{#([A-Za-z_][A-Za-z0-9_]*)\}', r'$#\1'),

    # Variable with braces: ${var} -> $var
    ("braced variable", r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}', r'$\1'),

    # stderr to stdout: 2>&1 -> >[2=1]
    ("stderr redirect", r'2>&1', r'>[2=1]'),

    # stderr to /dev/null: 2>/dev/null -> >[2]/dev/null
    ("stderr to devnull", r'2>/dev/null', r'>[2]/dev/null'),
]


def convert_command_substitution(line: str) -> str:
    """Convert $(cmd) to `{cmd}, and flag $((expr)) for manual review."""
    # Handle arithmetic expansion first: $((expr)) - rc has no built-in arithmetic
    result = re.sub(
        r'\$\(\(([^)]*)\)\)',
        r'`{awk "BEGIN{print \1}"}  # TODO: rc has no arithmetic; use awk or dc',
        line
    )
    # Command substitution: $(cmd) -> `{cmd}
    result = re.sub(r'\$\(([^)]*)\)', r'`{\1}', result)
    return result


def convert_variable_syntax(line: str) -> str:
    """Convert ${var} to $var and ${#var} to $#var, and ${var}text to $var^text."""
    # ${#var} -> $#var (length)
    result = re.sub(r'\$\{#([A-Za-z_][A-Za-z0-9_]*)\}', r'$#\1', line)
    # ${var}text -> $var^text (variable immediately followed by text)
    # Hyphen is placed at end of character class to avoid range interpretation
    result = re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}([A-Za-z0-9_./:.-])', r'$\1^\2', result)
    # ${var} -> $var (simple braces with no following text)
    result = re.sub(r'\$\{([A-Za-z_][A-Za-z0-9_]*)\}', r'$\1', result)
    return result


def convert_redirections(line: str) -> str:
    """Convert bash redirection syntax to rc syntax."""
    result = line.replace('2>&1', '>[2=1]')
    result = result.replace('2>/dev/null', '>[2]/dev/null')
    return result


def convert_assignment(line: str) -> str:
    """Convert bare variable assignments: var=value -> var = value.

    Only converts simple assignments at the start of a line (possibly indented),
    not assignments inside commands like grep 'x=y' or PATH=/usr/bin:$PATH.
    """
    # Match: optional indent, identifier, =, value (not preceded by a space or another =)
    # This handles: VAR=value, export VAR=value
    stripped = line.lstrip()
    indent = line[:len(line) - len(stripped)]

    # Handle 'export VAR=value'
    export_match = re.match(r'^export\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
    if export_match:
        var, val = export_match.group(1), export_match.group(2)
        return indent + f'{var} = {val}'

    # Handle 'local VAR=value' (bash-only construct, rc uses regular assignment)
    local_match = re.match(r'^local\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
    if local_match:
        var, val = local_match.group(1), local_match.group(2)
        return indent + f'{var} = {val}  # note: rc has no local variables'

    # Handle 'readonly VAR=value'
    readonly_match = re.match(r'^readonly\s+([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
    if readonly_match:
        var, val = readonly_match.group(1), readonly_match.group(2)
        return indent + f'{var} = {val}'

    # Simple assignment: VAR=value (but not cmd=... where cmd has spaces before it)
    assign_match = re.match(r'^([A-Za-z_][A-Za-z0-9_]*)=(.*)$', stripped)
    if assign_match:
        var, val = assign_match.group(1), assign_match.group(2)
        return indent + f'{var} = {val}'

    return line


def convert_for_loop(line: str) -> str:
    """Convert for loop header: for VAR in LIST; do -> for(VAR in LIST) {"""
    stripped = line.rstrip()
    indent = stripped[:len(stripped) - len(stripped.lstrip())]
    m = re.match(
        r'^(\s*)for\s+([A-Za-z_][A-Za-z0-9_]*)\s+in\s+(.*?)\s*;\s*do\s*$',
        stripped
    )
    if m:
        ind, var, lst = m.group(1), m.group(2), m.group(3)
        return f'{ind}for({var} in {lst}) {{'
    return line


def convert_while_loop(line: str) -> str:
    """Convert while loop header to rc syntax."""
    # while [ condition ]; do -> while(test condition) {
    # while [[ condition ]]; do -> while(test condition) {
    # while command; do -> while(command) {
    m = re.match(
        r'^(\s*)while\s+\[\[(.*?)\]\]\s*;\s*do\s*$',
        line.rstrip()
    )
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}while(test {cond}) {{'

    m = re.match(
        r'^(\s*)while\s+\[(.*?)\]\s*;\s*do\s*$',
        line.rstrip()
    )
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}while(test {cond}) {{'

    m = re.match(
        r'^(\s*)while\s+(.*?)\s*;\s*do\s*$',
        line.rstrip()
    )
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}while({cond}) {{'

    return line


def convert_if_statement(line: str) -> str:
    """Convert if/elif/else/fi to rc syntax."""
    stripped = line.rstrip()

    # elif [[ ... ]]; then -> } else if(test ...) {
    m = re.match(r'^(\s*)elif\s+\[\[(.*?)\]\]\s*;\s*then\s*$', stripped)
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}}} else if(test {cond}) {{'

    # elif [ ... ]; then -> } else if(test ...) {
    m = re.match(r'^(\s*)elif\s+\[(.*?)\]\s*;\s*then\s*$', stripped)
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}}} else if(test {cond}) {{'

    # elif command; then -> } else if(command) {
    m = re.match(r'^(\s*)elif\s+(.*?)\s*;\s*then\s*$', stripped)
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}}} else if({cond}) {{'

    # if [[ ... ]]; then -> if(test ...) {
    m = re.match(r'^(\s*)if\s+\[\[(.*?)\]\]\s*;\s*then\s*$', stripped)
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}if(test {cond}) {{'

    # if [ ... ]; then -> if(test ...) {
    m = re.match(r'^(\s*)if\s+\[(.*?)\]\s*;\s*then\s*$', stripped)
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}if(test {cond}) {{'

    # if command; then -> if(command) {
    m = re.match(r'^(\s*)if\s+(.*?)\s*;\s*then\s*$', stripped)
    if m:
        ind, cond = m.group(1), m.group(2).strip()
        return f'{ind}if({cond}) {{'

    # else -> } else {
    m = re.match(r'^(\s*)else\s*$', stripped)
    if m:
        return f'{m.group(1)}}} else {{'

    # fi -> }
    m = re.match(r'^(\s*)fi\s*$', stripped)
    if m:
        return m.group(1) + '}'

    # done -> }
    m = re.match(r'^(\s*)done\s*$', stripped)
    if m:
        return m.group(1) + '}'

    return line


def convert_function_def(line: str) -> str:
    """Convert function definitions to rc fn syntax."""
    stripped = line.rstrip()

    # function name() { -> fn name {
    m = re.match(r'^(\s*)function\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{?\s*$', stripped)
    if m:
        ind, name = m.group(1), m.group(2)
        return f'{ind}fn {name} {{'

    # name() { -> fn name {
    m = re.match(r'^(\s*)([A-Za-z_][A-Za-z0-9_]*)\s*\(\)\s*\{?\s*$', stripped)
    if m:
        ind, name = m.group(1), m.group(2)
        return f'{ind}fn {name} {{'

    return line


def convert_shebang(line: str) -> str:
    """Convert bash/sh shebang to rc shebang."""
    if re.match(r'^#!\s*/bin/(bash|sh)\s*$', line) or \
       re.match(r'^#!\s*/usr/(local/)?bin/(bash|sh)\s*$', line) or \
       re.match(r'^#!\s*/usr/bin/env\s+(bash|sh)\s*$', line):
        return '#!/usr/local/bin/rc'
    return line


def convert_test_syntax(line: str) -> str:
    """Convert [[ ]] test syntax to rc ~ operator where appropriate."""
    # [[ $var == value ]] -> ~ $var value (string equality)
    m = re.match(r'^(\s*)\[\[\s*(\$[A-Za-z_][A-Za-z0-9_]*)\s*==\s*(\S+)\s*\]\]\s*$', line.rstrip())
    if m:
        ind, var, val = m.group(1), m.group(2), m.group(3)
        return f'{ind}~ {var} {val}'

    # [[ -z $var ]] -> ~ $var ''
    m = re.match(r'^(\s*)\[\[\s*-z\s+(\$[A-Za-z_][A-Za-z0-9_]*)\s*\]\]\s*$', line.rstrip())
    if m:
        ind, var = m.group(1), m.group(2)
        return f"{ind}~ {var} ''"

    # [[ -n $var ]] -> ! ~ $var ''
    m = re.match(r'^(\s*)\[\[\s*-n\s+(\$[A-Za-z_][A-Za-z0-9_]*)\s*\]\]\s*$', line.rstrip())
    if m:
        ind, var = m.group(1), m.group(2)
        return f"{ind}! ~ {var} ''"

    return line


def convert_line(line: str) -> str:
    """Apply all conversions to a single line."""
    # Shebang must be first
    result = convert_shebang(line)
    if result != line:
        return result

    # Apply transformations in sequence
    result = convert_command_substitution(result)
    result = convert_variable_syntax(result)
    result = convert_redirections(result)

    # Control flow (order matters: elif before if)
    result = convert_if_statement(result)
    result = convert_for_loop(result)
    result = convert_while_loop(result)
    result = convert_function_def(result)

    # Assignment last (after control flow, to avoid matching 'for' etc.)
    result = convert_assignment(result)

    # Test syntax
    result = convert_test_syntax(result)

    return result


def convert_to_rc(script: str) -> str:
    """Convert a multi-line bash/sh script to rc syntax.

    Args:
        script: Bash/sh script text

    Returns:
        Converted rc script text
    """
    lines = script.split('\n')
    converted = [convert_line(line) for line in lines]
    return '\n'.join(converted)


def print_reference() -> None:
    """Print a bash-to-rc syntax reference."""
    print("""Bash/sh to rc shell syntax reference
=====================================

COMMAND SUBSTITUTION:
  bash:  result=$(command)
  rc:    result = `{command}

VARIABLES:
  bash:  var=value              rc:  var = value
  bash:  ${var}text             rc:  $var^text
  bash:  ${#var}                rc:  $#var

FOR LOOPS:
  bash:  for f in *.txt; do     rc:  for(f in *.txt) {
  bash:    echo $f              rc:    echo $f
  bash:  done                   rc:  }

IF STATEMENTS:
  bash:  if [ -f file ]; then   rc:  if(test -f file) {
  bash:    cmd                  rc:    cmd
  bash:  elif [ -d d ]; then    rc:  } else if(test -d d) {
  bash:  else                   rc:  } else {
  bash:  fi                     rc:  }

WHILE LOOPS:
  bash:  while [ cond ]; do     rc:  while(test cond) {
  bash:    cmd                  rc:    cmd
  bash:  done                   rc:  }

FUNCTIONS:
  bash:  greet() {              rc:  fn greet {
  bash:    echo hello           rc:    echo hello
  bash:  }                      rc:  }

REDIRECTION:
  bash:  cmd 2>&1               rc:  cmd >[2=1]
  bash:  cmd 2>/dev/null        rc:  cmd >[2]/dev/null

STRING CONCATENATION:
  bash:  echo "${a}text"        rc:  echo $a^text
  bash:  echo "$a$b"            rc:  echo $a^$b

TESTS (in conditions):
  bash:  [[ $x == y ]]          rc:  ~ $x y
  bash:  [[ -z $x ]]            rc:  ~ $x ''
  bash:  [[ -n $x ]]            rc:  ! ~ $x ''

NOTE: Most basic Unix commands (ls, grep, find, etc.) work the same in rc.
""")


def main() -> None:
    """Main entry point for command-line usage."""
    if len(sys.argv) > 1:
        arg = sys.argv[1]
        if arg in ('-h', '--help'):
            print(__doc__)
            sys.exit(0)
        elif arg in ('--reference', '--ref'):
            print_reference()
            sys.exit(0)
        else:
            # Treat all arguments as a single command to convert
            cmd = ' '.join(sys.argv[1:])
            print(convert_to_rc(cmd))
            return

    # Read from stdin
    if sys.stdin.isatty():
        print("Usage: bash_to_rc_converter.py 'command'")
        print("       echo 'command' | bash_to_rc_converter.py")
        print("       bash_to_rc_converter.py --reference")
        sys.exit(1)

    script = sys.stdin.read()
    print(convert_to_rc(script), end='')


if __name__ == '__main__':
    main()
