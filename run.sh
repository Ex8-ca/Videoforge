#!/bin/bash
set -a
# Load MiniMax API key
source ~/.hermes/.env
set +a
exec python3 /home/marc/videoforge/server.py "$@"
