#!/bin/bash
# Clean Python cache files to resolve git pull conflicts
# Run this on Raspberry Pi

cd ~/projects/OAKD_camera_project

echo "Cleaning Python cache files..."

# Remove all __pycache__ directories
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null

# Remove all .pyc files
find . -type f -name "*.pyc" -delete

# Remove all .pyo files
find . -type f -name "*.pyo" -delete

echo "✓ Cache files cleaned!"
echo ""
echo "Now you can run: git pull"

