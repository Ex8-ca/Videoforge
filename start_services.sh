#!/bin/bash
# VideoForge Services Startup Script

VIDEOFORGE_DIR="/home/marc/videoforge"

echo "Starting VideoForge Services..."

cd "$VIDEOFORGE_DIR"

# Kill existing
pkill -f "together_bridge.py" 2>/dev/null || true
pkill -f "server.py" 2>/dev/null || true
sleep 1

# Start Together Bridge
nohup python3 together_bridge.py > /tmp/together_bridge.log 2>&1 &
echo "Together Bridge started (PID: $!)"

sleep 3

# Start VideoForge
nohup python3 server.py > /tmp/videoforge.log 2>&1 &
echo "VideoForge started (PID: $!)"

sleep 2

echo ""
echo "Services running:"
echo "  VideoForge: http://192.168.1.3:8889"
echo "  Together Bridge: http://127.0.0.1:9000"
echo ""
ps aux | grep -E "together_bridge|videoforge.*server" | grep -v grep
