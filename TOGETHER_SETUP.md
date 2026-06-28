# Together.ai Bridge Setup ✅

## Architecture

```
VideoForge Frontend (port 8889)
         │
         │ HTTP POST /generate
         ▼
Together Bridge (port 9000)
         │
         │ Together Python SDK
         ▼
Together.ai API
```

## Services

### 1. VideoForge Server (port 8889)
- Main web interface
- Handles local Wan2.1 generation
- Proxies to Together bridge for cloud generation

### 2. Together Bridge (port 9000)
- Python service using official Together SDK
- Handles video generation requests
- Polls for completion
- Returns video URL when ready

## Starting Services

### Quick Start
```bash
# Start Together Bridge (required for cloud generation)
cd /home/marc/videoforge && python3 together_bridge.py &

# Start VideoForge (if not running)
cd /home/marc/videoforge && python3 server.py &
```

### Auto-start Script
```bash
#!/bin/bash
# Start VideoForge services

# Start Together Bridge
cd /home/marc/videoforge
nohup python3 together_bridge.py > /tmp/together_bridge.log 2>&1 &
echo "Together Bridge started (PID: $!)"

# Wait for bridge to be ready
sleep 3

# Start VideoForge
nohup python3 server.py > /tmp/videoforge.log 2>&1 &
echo "VideoForge started (PID: $!)"

echo ""
echo "Services running:"
echo "  - VideoForge: http://192.168.1.3:8889"
echo "  - Together Bridge: http://127.0.0.1:9000"
```

## API Endpoints

### Together Bridge

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Health check |
| `/generate` | POST | Start video generation |
| `/status/{task_id}` | GET | Check generation status |

### Generate Request
```json
POST http://127.0.0.1:9000/generate
{
  "prompt": "Woman winking at camera",
  "image": "data:image/png;base64,..."
}
```

### Generate Response
```json
{
  "task_id": "task_1234567890"
}
```

### Status Response
```json
{
  "status": "processing" | "completed" | "failed",
  "video_url": "https://...",  // when completed
  "error": "..."  // when failed
}
```

## Usage in VideoForge

1. **Open** http://192.168.1.3:8889
2. **Select "Together.ai Cloud"** mode
3. **Upload reference image**
4. **Enter motion prompt**
5. **Click Generate**
6. **Wait ~2 minutes**
7. **Video appears!**

## Troubleshooting

### "Bridge service not running"
```bash
# Start the bridge
cd /home/marc/videoforge && python3 together_bridge.py &

# Or check if already running
ps aux | grep together_bridge
```

### "Together SDK not installed"
```bash
pip install together --break-system-packages
```

### "API key invalid"
- Check key in `together_bridge.py`
- Verify at https://api.together.ai/settings/api-keys
- Ensure you have credits

### Generation timeout
- Together.ai can be slow during peak times
- Default timeout: 10 minutes
- Check bridge logs: `cat /tmp/together_bridge.log`

## Configuration

### API Key
Edit `together_bridge.py`:
```python
TOGETHER_API_KEY = "tgp_v1_..."  # Your key
```

### Port
Edit `together_bridge.py`:
```python
port = 9000  # Change if needed
```

### Model
Edit `together_bridge.py` in `generate_video()`:
```python
response = client.videos.create(
    model="ByteDance/Seedance-1.0-pro",  # Change model
    ...
)
```

## Logs

| Service | Log File |
|---------|----------|
| Together Bridge | `/tmp/together_bridge.log` |
| VideoForge | `/tmp/videoforge.log` |

## Credit Usage

- Check credits: https://api.together.ai/settings/credits
- Video generation: ~$0.05-0.20 per video
- Your balance: $92

## Performance

| Metric | Value |
|--------|-------|
| Generation time | ~2 minutes |
| Video length | 5 seconds |
| Resolution | 1920x1088 |
| Format | MP4 (H.264) |
| FPS | 25 |
