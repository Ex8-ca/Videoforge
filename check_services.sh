#!/bin/bash
# Quick check script for VideoForge services

echo "╔══════════════════════════════════════╗"
echo "║   VideoForge Services Status         ║"
echo "╚══════════════════════════════════════╝"
echo ""

echo "=== Systemd Services ==="
echo ""

# Together Bridge
echo "Together Bridge (port 9000):"
systemctl --user is-active together-bridge.service 2>/dev/null && echo "  ✓ Running" || echo "  ✗ Not running"

# VideoForge
echo "VideoForge (port 8889):"
systemctl --user is-active videoforge.service 2>/dev/null && echo "  ✓ Running" || echo "  ✗ Not running"

echo ""
echo "=== Endpoint Tests ==="
echo ""

# Test Together Bridge
BRIDGE_RESP=$(curl -s http://127.0.0.1:9000/health 2>/dev/null)
if echo "$BRIDGE_RESP" | grep -q '"status": "ok"'; then
    echo "Together Bridge API: ✓ OK"
else
    echo "Together Bridge API: ✗ Not responding"
fi

# Test VideoForge
VIDEOFORGE_RESP=$(curl -s http://192.168.1.3:8889/ 2>/dev/null)
if echo "$VIDEOFORGE_RESP" | grep -q "VideoForge"; then
    echo "VideoForge Web: ✓ OK"
else
    echo "VideoForge Web: ✗ Not responding"
fi

echo ""
echo "=== Quick Actions ==="
echo ""
echo "Restart all:   systemctl --user restart together-bridge videoforge"
echo "View logs:     journalctl --user -u together-bridge -u videoforge -f"
echo "Stop all:      systemctl --user stop together-bridge videoforge"
echo ""
echo "Access: http://192.168.1.3:8889"
