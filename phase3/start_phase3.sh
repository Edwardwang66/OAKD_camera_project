#!/bin/bash
# Safe startup script for Phase 3 that handles Qt errors
# This script suppresses Qt errors and allows program to continue

echo "Starting Phase 3 Demo..."
echo ""

# Check if --no-gui flag is present
if [[ "$*" == *"--no-gui"* ]]; then
    echo "[INFO] Running without GUI display"
    python phase3_demo.py "$@"
else
    echo "[INFO] Attempting to start with GUI (Qt errors will be suppressed)"
    echo ""
    
    # Redirect stderr to filter Qt errors, but keep other errors visible
    # We use a temporary file to capture stderr, filter it, then output
    exec 3>&2  # Save stderr to fd 3
    exec 2> >(
        while IFS= read -r line; do
            # Filter out Qt errors but keep other important errors
            if [[ ! "$line" =~ (qt\.qpa|Qt platform|QT_QPA|Could not find the Qt|Available platform plugins|Aborted) ]]; then
                echo "$line" >&3
            fi
        done
    )
    
    # Run the program
    python phase3_demo.py "$@"
    exit_code=$?
    
    # Restore stderr
    exec 2>&3
    exec 3>&-
    
    exit $exit_code
fi

