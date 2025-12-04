#!/bin/bash
# Run Phase 2 demo in Docker container
# This avoids Qt/X11 display conflicts

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=========================================="
echo "Phase 2 Docker Runner"
echo "=========================================="
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed"
    echo "Install Docker: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if docker-compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "Error: docker-compose is not installed"
    echo "Install docker-compose: https://docs.docker.com/compose/install/"
    exit 1
fi

# Parse command line arguments
SIMULATION="--simulation"
VESC_PORT=""
TARGET_DISTANCE=""
EXTRA_ARGS=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-simulation|--real)
            SIMULATION=""
            shift
            ;;
        --vesc-port)
            VESC_PORT="$2"
            shift 2
            ;;
        --target-distance)
            TARGET_DISTANCE="$2"
            shift 2
            ;;
        *)
            EXTRA_ARGS="$EXTRA_ARGS $1"
            shift
            ;;
    esac
done

# Build command
CMD="python phase2/phase2_demo.py"
if [ -n "$SIMULATION" ]; then
    CMD="$CMD $SIMULATION"
fi
if [ -n "$VESC_PORT" ]; then
    CMD="$CMD --vesc-port $VESC_PORT"
fi
if [ -n "$TARGET_DISTANCE" ]; then
    CMD="$CMD --target-distance $TARGET_DISTANCE"
fi
CMD="$CMD $EXTRA_ARGS"

echo "Building Docker image..."
docker-compose build || docker compose build

echo ""
echo "Running Phase 2 demo in Docker..."
echo "Command: $CMD"
echo ""

# Run with docker-compose
docker-compose run --rm phase2 $CMD || docker compose run --rm phase2 $CMD

