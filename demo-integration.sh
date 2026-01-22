#!/bin/bash
# demo-integration.sh - Demonstrates AI chat integration with rc shell
#
# This script shows how to use rc shell with AI chat tools like aichat.
# It sets up the environment and provides examples of interaction.

set -e

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== RC Shell AI Chat Integration Demo ===${NC}\n"

# Check if rc is built
if [ ! -x ./rc ]; then
    echo -e "${YELLOW}Building rc shell...${NC}"
    make
    echo -e "${GREEN}✓ RC shell built successfully${NC}\n"
fi

# Set up environment
RC_PATH="$(pwd)/rc"
export SHELL="$RC_PATH"
export history="$HOME/.rc_history_demo"

echo -e "${BLUE}Environment Setup:${NC}"
echo "  SHELL=$SHELL"
echo "  history=$history"
echo ""

# Source integration script
echo -e "${BLUE}Testing Integration Scripts:${NC}\n"

echo -e "${YELLOW}1. Testing rc-integration.sh (POSIX shell)...${NC}"
if [ ! -f ./rc-integration.sh ]; then
    echo -e "${YELLOW}✗ rc-integration.sh not found${NC}"
else
    if . ./rc-integration.sh && detect_rc_shell; then
        echo -e "${GREEN}✓ Shell detected as rc${NC}"
        echo "  Shell name: $(export_rc_shell_info)"
        echo "  Shell command: $(export_rc_shell_cmd)"
        echo "  Shell argument: $(export_rc_shell_arg)"
        echo "  History file: $(get_rc_history_file)"
    else
        echo -e "${YELLOW}✗ Shell not detected as rc (may need to run in rc)${NC}"
    fi
fi
echo ""

echo -e "${YELLOW}2. Testing rc-shell.rc (native rc script)...${NC}"
if [ ! -f ./rc-shell.rc ]; then
    echo -e "${YELLOW}✗ rc-shell.rc not found${NC}"
else
    $RC_PATH -c '. ./rc-shell.rc; rcshell_detect'
    echo -e "${GREEN}✓ RC native detection script works${NC}"
fi
echo ""

# Test Python integration
echo -e "${YELLOW}3. Testing Python integration...${NC}"
if command -v python3 >/dev/null 2>&1; then
    cd examples
    python3 rc_shell_support.py
    cd ..
    echo -e "${GREEN}✓ Python integration works${NC}"
else
    echo -e "${YELLOW}✗ Python3 not found, skipping test${NC}"
fi
echo ""

# Demonstrate command execution
echo -e "${BLUE}Example: Using RC Shell for Commands${NC}\n"

echo -e "${YELLOW}Executing simple command...${NC}"
$RC_PATH -c 'echo "Hello from rc shell!"'
echo ""

echo -e "${YELLOW}Executing command with substitution...${NC}"
$RC_PATH -c 'echo "Current directory: "^`{pwd}'
echo ""

echo -e "${YELLOW}Executing command with variables...${NC}"
$RC_PATH -c 'files = `{ls *.md}; echo "Markdown files: "$files'
echo ""

# Show history file
echo -e "${BLUE}History Management:${NC}\n"

# Append some commands to history
if [ -f ./rc-integration.sh ]; then
    . ./rc-integration.sh
    append_rc_history "echo 'test command 1'" 0
    append_rc_history "ls -la" 0
    append_rc_history "pwd" 0
fi

if [ -f "$history" ]; then
    echo -e "${GREEN}✓ History file created: $history${NC}"
    echo "Recent commands:"
    tail -3 "$history" | sed 's/^/  /'
else
    echo -e "${YELLOW}History file not found${NC}"
fi
echo ""

# Integration tips
echo -e "${BLUE}Integration Tips:${NC}\n"
echo "To use rc with AI chat tools like aichat:"
echo ""
echo "1. Set your SHELL environment variable:"
echo "   export SHELL=$RC_PATH"
echo ""
echo "2. Configure history in ~/.rcrc:"
echo "   history = \$home^'/.rc_history'"
echo ""
echo "3. Use with aichat (if installed):"
echo "   aichat -e \"list all text files\""
echo ""
echo "4. The AI will generate rc-compatible commands:"
echo "   ls *.txt"
echo "   for(f in *.txt) echo \$f"
echo ""

echo -e "${GREEN}=== Demo Complete ===${NC}"
echo ""
echo "Try running these commands in rc:"
echo "  $RC_PATH"
echo "  . ./rc-shell.rc"
echo "  rcshell_info"
echo "  rcshell_history"
