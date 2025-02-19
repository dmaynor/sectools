#!/usr/bin/env bash

# Default values
SHELL_TYPE="$SHELL"  # Auto-detects current shell
SOURCE_FILE=""
SHOW_ADDED=false
SHOW_REMOVED=false
SHOW_PERSISTED=false

# Usage help
usage() {
    echo "Usage: $0 [-s shell] [-f file] [--added] [--removed] [--persisted]"
    echo "  -s shell    : Specify shell type (zsh, bash, fish)"
    echo "  -f file     : File to source and compare effects"
    echo "  --added     : Show newly added environment variables/functions/hooks"
    echo "  --removed   : Show removed environment variables/functions/hooks"
    echo "  --persisted : Show unchanged environment variables/functions/hooks"
    exit 1
}

# Parse CLI arguments
while [[ "$#" -gt 0 ]]; do
    case "$1" in
        -s) SHELL_TYPE="$2"; shift ;;
        -f) SOURCE_FILE="$2"; shift ;;
        --added) SHOW_ADDED=true ;;
        --removed) SHOW_REMOVED=true ;;
        --persisted) SHOW_PERSISTED=true ;;
        *) usage ;;
    esac
    shift
done

# Ensure file is provided
if [[ -z "$SOURCE_FILE" ]]; then
    echo "❌ Error: No file specified. Use -f <file>."
    usage
fi

# Ensure shell is valid
if ! command -v "$SHELL_TYPE" &>/dev/null; then
    echo "❌ Error: Shell '$SHELL_TYPE' not found."
    exit 1
fi

echo "🔹 Running in: $SHELL_TYPE"
echo "🔹 Sourcing: $SOURCE_FILE"

# Capture environment before sourcing
echo "📌 Capturing pre-source environment..."
env > /tmp/env_before.txt
typeset -f > /tmp/functions_before.txt

# Check if using Zsh or Bash for hooks
if [[ "$SHELL_TYPE" == "zsh" ]]; then
    echo "📌 Capturing Zsh hooks..."
    (autoload -Uz add-zsh-hook && add-zsh-hook -L) > /tmp/hooks_before.txt
elif [[ "$SHELL_TYPE" == "bash" ]]; then
    echo "📌 Capturing Bash traps..."
    trap -p > /tmp/hooks_before.txt
else
    echo "⚠️ Hook tracking not supported for $SHELL_TYPE"
fi

# Source the file in a subshell
echo "🔄 Sourcing $SOURCE_FILE in $SHELL_TYPE..."
$SHELL_TYPE -c "source $SOURCE_FILE; env > /tmp/env_after.txt; typeset -f > /tmp/functions_after.txt; trap -p > /tmp/hooks_after.txt"

# Compare before & after states
echo "🔍 Comparing pre- and post-source states..."

# Find added, removed, and persisted variables
added_vars=$(diff --new-line-format="+ %L" --old-line-format="" --unchanged-line-format="" /tmp/env_before.txt /tmp/env_after.txt)
removed_vars=$(diff --new-line-format="" --old-line-format="- %L" --unchanged-line-format="" /tmp/env_before.txt /tmp/env_after.txt)
persisted_vars=$(diff --unchanged-line-format="  %L" --new-line-format="" --old-line-format="" /tmp/env_before.txt /tmp/env_after.txt)

# Find added, removed, and persisted functions
added_funcs=$(diff --new-line-format="+ %L" --old-line-format="" --unchanged-line-format="" /tmp/functions_before.txt /tmp/functions_after.txt)
removed_funcs=$(diff --new-line-format="" --old-line-format="- %L" --unchanged-line-format="" /tmp/functions_before.txt /tmp/functions_after.txt)

# Find added and removed hooks
added_hooks=$(diff --new-line-format="+ %L" --old-line-format="" --unchanged-line-format="" /tmp/hooks_before.txt /tmp/hooks_after.txt)
removed_hooks=$(diff --new-line-format="" --old-line-format="- %L" --unchanged-line-format="" /tmp/hooks_before.txt /tmp/hooks_after.txt)

# Display results based on flags
echo "📌 Environment Variable Changes:"
if $SHOW_ADDED; then echo "🟢 Added Variables:" && echo "$added_vars"; fi
if $SHOW_REMOVED; then echo "🔴 Removed Variables:" && echo "$removed_vars"; fi
if $SHOW_PERSISTED; then echo "🔵 Persisted Variables:" && echo "$persisted_vars"; fi

echo "📌 Function Changes:"
if $SHOW_ADDED; then echo "🟢 Added Functions:" && echo "$added_funcs"; fi
if $SHOW_REMOVED; then echo "🔴 Removed Functions:" && echo "$removed_funcs"; fi

echo "📌 Hook Changes:"
if $SHOW_ADDED; then echo "🟢 Added Hooks:" && echo "$added_hooks"; fi
if $SHOW_REMOVED; then echo "🔴 Removed Hooks:" && echo "$removed_hooks"; fi

echo "✅ Done!"