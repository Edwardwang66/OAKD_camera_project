#!/bin/bash
# Run Phase 3 without GUI display (Qt errors will be suppressed)
# This script redirects stderr to suppress Qt plugin errors

echo "Running Phase 3 without GUI display..."
echo "Qt errors will be suppressed. All output will go to terminal."
echo ""

# Redirect Qt errors to /dev/null but keep other errors
exec 2> >(grep -v "qt.qpa\|Qt platform\|QT_QPA" >&2)

python phase3_demo.py "$@"

