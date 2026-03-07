#!/bin/bash
# test-integration.sh - Test rc shell integration functionality

set -e

echo "=== Testing RC Shell Integration ==="
echo

# Test 1: Shell detection script
echo "Test 1: Testing rc-integration.sh shell detection..."
if [ -f rc-integration.sh ]; then
    # Test with rc in SHELL
    export SHELL=/usr/local/bin/rc
    result=$(bash rc-integration.sh)
    if echo "$result" | grep -q "SHELL_NAME=rc"; then
        echo "✓ Shell detection works correctly"
    else
        echo "✗ Shell detection failed"
        echo "Output: $result"
        exit 1
    fi
else
    echo "✗ rc-integration.sh not found"
    exit 1
fi
echo

# Test 2: Python example
echo "Test 2: Testing Python example..."
if [ -f examples/rc_shell_support.py ]; then
    export SHELL=/usr/local/bin/rc
    if python3 examples/rc_shell_support.py > /tmp/test_output.txt 2>&1; then
        if grep -q "Detected shell: rc" /tmp/test_output.txt; then
            echo "✓ Python example works correctly"
        else
            echo "✗ Python example didn't detect rc shell"
            cat /tmp/test_output.txt
            exit 1
        fi
    else
        echo "✗ Python example failed to run"
        cat /tmp/test_output.txt
        exit 1
    fi
else
    echo "✗ Python example not found"
    exit 1
fi
echo

# Test 3: RC shell script
echo "Test 3: Testing rc-shell.rc script syntax..."
if [ -f rc-shell.rc ]; then
    # Check if rc binary is available and test the script
    if [ -f ./rc ]; then
        # Test rcshell_info function
        result=$(./rc -c '. ./rc-shell.rc && rcshell_info')
        if [ "$result" = "rc" ]; then
            echo "✓ rc-shell.rc works correctly with rc binary"
        else
            echo "✗ rc-shell.rc test failed"
            echo "Expected: rc, Got: $result"
            exit 1
        fi
    else
        echo "✓ rc-shell.rc exists (rc binary not built, skipping runtime test)"
    fi
else
    echo "✗ rc-shell.rc not found"
    exit 1
fi
echo

# Test 4: Check documentation
echo "Test 4: Checking documentation files..."
# Note: Update this list when adding new documentation files
files_to_check=("AI_INTEGRATION.md" "USAGE_GUIDE.md" "examples/README.md" "README")
all_found=true
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✓ $file exists"
    else
        echo "✗ $file not found"
        all_found=false
    fi
done
if [ "$all_found" = false ]; then
    exit 1
fi
echo

# Test 5: Verify history file detection
echo "Test 5: Testing history file detection..."
export SHELL=/usr/local/bin/rc
export history=/tmp/test_rc_history
result=$(bash rc-integration.sh | grep SHELL_HISTORY)
if echo "$result" | grep -q "/tmp/test_rc_history"; then
    echo "✓ History file detection from \$history variable works"
else
    echo "✗ History file detection failed"
    echo "Output: $result"
    exit 1
fi
echo

# Test 6: Bash-to-rc converter
echo "Test 6: Testing bash-to-rc command converter..."
if [ -f examples/bash_to_rc_converter.py ]; then
    # Test command substitution conversion
    result=$(echo 'result=$(hostname)' | python3 examples/bash_to_rc_converter.py)
    if echo "$result" | grep -q '`{hostname}'; then
        echo "✓ Command substitution conversion works"
    else
        echo "✗ Command substitution conversion failed"
        echo "Output: $result"
        exit 1
    fi

    # Test assignment conversion
    result=$(echo 'VAR=hello' | python3 examples/bash_to_rc_converter.py)
    if echo "$result" | grep -q 'VAR = hello'; then
        echo "✓ Variable assignment conversion works"
    else
        echo "✗ Variable assignment conversion failed"
        echo "Output: $result"
        exit 1
    fi

    # Test for loop conversion
    result=$(printf 'for f in *.txt; do\n  echo $f\ndone\n' | python3 examples/bash_to_rc_converter.py)
    if echo "$result" | grep -q 'for(f in \*.txt)'; then
        echo "✓ For loop conversion works"
    else
        echo "✗ For loop conversion failed"
        echo "Output: $result"
        exit 1
    fi

    # Test if statement conversion
    result=$(printf 'if [ -f file.txt ]; then\n  echo yes\nfi\n' | python3 examples/bash_to_rc_converter.py)
    if echo "$result" | grep -q 'if(test -f file.txt)'; then
        echo "✓ If statement conversion works"
    else
        echo "✗ If statement conversion failed"
        echo "Output: $result"
        exit 1
    fi

    # Test stderr redirection conversion
    result=$(echo 'make 2>&1 | head' | python3 examples/bash_to_rc_converter.py)
    if echo "$result" | grep -q '>\[2=1\]'; then
        echo "✓ Stderr redirection conversion works"
    else
        echo "✗ Stderr redirection conversion failed"
        echo "Output: $result"
        exit 1
    fi

    # Test shebang conversion
    result=$(echo '#!/bin/bash' | python3 examples/bash_to_rc_converter.py)
    if echo "$result" | grep -q '#!/usr/local/bin/rc'; then
        echo "✓ Shebang conversion works"
    else
        echo "✗ Shebang conversion failed"
        echo "Output: $result"
        exit 1
    fi
else
    echo "✗ examples/bash_to_rc_converter.py not found"
    exit 1
fi
echo

# Test 7: Verify convert-to-rc.sh wrapper
echo "Test 7: Testing convert-to-rc.sh wrapper..."
if [ -f convert-to-rc.sh ]; then
    result=$(echo 'result=$(pwd)' | ./convert-to-rc.sh)
    if echo "$result" | grep -q '`{pwd}'; then
        echo "✓ convert-to-rc.sh wrapper works"
    else
        echo "✗ convert-to-rc.sh wrapper failed"
        echo "Output: $result"
        exit 1
    fi
else
    echo "✗ convert-to-rc.sh not found"
    exit 1
fi
echo

# Test 8: Verify RC_SYNTAX_GUIDE.md
echo "Test 8: Checking RC_SYNTAX_GUIDE.md..."
if [ -f RC_SYNTAX_GUIDE.md ]; then
    # Check for key sections
    if grep -q "Command Substitution" RC_SYNTAX_GUIDE.md && \
       grep -q "For Loop" RC_SYNTAX_GUIDE.md && \
       grep -q "Functions" RC_SYNTAX_GUIDE.md; then
        echo "✓ RC_SYNTAX_GUIDE.md exists and contains key sections"
    else
        echo "✗ RC_SYNTAX_GUIDE.md is missing key sections"
        exit 1
    fi
else
    echo "✗ RC_SYNTAX_GUIDE.md not found"
    exit 1
fi
echo

echo "=== All tests passed! ==="
echo
echo "Integration files:"
echo "  - rc-integration.sh (POSIX shell integration)"
echo "  - rc-shell.rc (rc shell native integration)"
echo "  - convert-to-rc.sh (bash-to-rc syntax converter)"
echo "  - AI_INTEGRATION.md (comprehensive documentation)"
echo "  - RC_SYNTAX_GUIDE.md (rc syntax reference for AI tools)"
echo "  - examples/rc_shell_support.py (Python shell support example)"
echo "  - examples/bash_to_rc_converter.py (bash-to-rc converter)"
echo "  - examples/rc_shell_support.rs (Rust example)"
echo "  - examples/README.md (examples documentation)"
