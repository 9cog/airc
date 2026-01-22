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
files_to_check=("AI_INTEGRATION.md" "examples/README.md" "README")
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

echo "=== All tests passed! ==="
echo
echo "Integration files created:"
echo "  - rc-integration.sh (POSIX shell integration)"
echo "  - rc-shell.rc (rc shell native integration)"
echo "  - AI_INTEGRATION.md (comprehensive documentation)"
echo "  - examples/rc_shell_support.py (Python example)"
echo "  - examples/rc_shell_support.rs (Rust example)"
echo "  - examples/README.md (examples documentation)"
