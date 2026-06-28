#!/bin/bash
# VideoForge Systemd Service Setup
# Run this ONCE to set up auto-start on boot

set -e

echo "╔══════════════════════════════════════╗"
echo "║   VideoForge Systemd Setup           ║"
echo "╚══════════════════════════════════════╝"
echo ""

# Check if running as user systemd
if [ "$EUID" -eq 0 ]; then
    echo "ERROR: Do NOT run as root/sudo"
    echo "Run as regular user: ./setup_systemd.sh"
    exit 1
fi

# Create systemd user directory if needed
mkdir -p ~/.config/systemd/user

echo "1. Reloading systemd daemon..."
systemctl --user daemon-reload

echo "2. Enabling services (auto-start on boot)..."
systemctl --user enable together-bridge.service
systemctl --user enable videoforge.service

echo "3. Starting services now..."
systemctl --user start together-bridge.service
sleep 2
systemctl --user start videoforge.service
sleep 2

echo ""
echo "4. Checking service status..."
echo ""
echo "=== Together Bridge ==="
systemctl --user status together-bridge.service --no-pager | head -10

echo ""
echo "=== VideoForge ==="
systemctl --user status videoforge.service --no-pager | head -10

echo ""
echo "╔══════════════════════════════════════╗"
echo "║   Setup Complete!                    ║"
echo "╠══════════════════════════════════════╣"
echo "║   Services will auto-start on boot   ║"
echo "╠══════════════════════════════════════╣"
echo "║   Useful commands:                   ║"
echo "║                                      ║"
echo "║   # Check status                     ║"
echo "║   systemctl --user status together-bridge  ║"
echo "║   systemctl --user status videoforge       ║"
echo "║                                      ║"
echo "║   # Restart services                 ║"
echo "║   systemctl --user restart together-bridge ║"
echo "║   systemctl --user restart videoforge      ║"
echo "║                                      ║"
echo "║   # Stop services                    ║"
echo "║   systemctl --user stop together-bridge    ║"
echo "║   systemctl --user stop videoforge         ║"
echo "║                                      ║"
echo "║   # View logs                        ║"
echo "║   journalctl --user -u together-bridge     ║"
echo "║   journalctl --user -u videoforge          ║"
echo "║                                      ║"
echo "║   # Disable auto-start               ║"
echo "║   systemctl --user disable together-bridge ║"
echo "║   systemctl --user disable videoforge      ║"
echo "╚══════════════════════════════════════╝"
echo ""
echo "Access VideoForge at: http://192.168.1.3:8889"
