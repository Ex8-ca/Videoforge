# MiniMax Video Generation Setup ✅

## Configuration Complete

| Setting | Value |
|---------|-------|
| **API Key** | `sk-api--FAygT...` (configured) |
| **Model** | `video-01` |
| **Endpoint** | `https://api.minimax.io/v1/video/generations` |
| **Status** | ✅ Ready |

## How It Works

1. **Upload reference image** - Your character/scene
2. **Enter motion prompt** - Describe the action
3. **Select "MiniMax Cloud"** mode
4. **Click Generate** - Video created in ~1-2 minutes
5. **Download or upload to Cloudinary**

## API Endpoints (Proxied)

| Operation | Endpoint |
|-----------|----------|
| Generate | `/minimax/video/generations` → `https://api.minimax.io/v1/video/generations` |
| Status Check | `/minimax/video/tasks/{task_id}` → `https://api.minimax.io/v1/video/tasks/{task_id}` |

## Request Format

```json
{
  "model": "video-01",
  "prompt": "Woman winking with breeze blowing hair",
  "image": "data:image/png;base64,...",
  "video_duration": 5
}
```

## Response

```json
{
  "task_id": "abc123...",
  "task_status": "processing"
}
```

## Status Polling

```json
{
  "task_status": "success",
  "video_url": "https://cdn.minimax.io/..."
}
```

## Credit Usage

- Check your credits at: https://platform.minimax.io/
- Video generation uses credits based on duration
- 5-second video = ~1 credit (check current rates)

## Troubleshooting

### "Invalid API key"
- Verify key starts with `sk-api--`
- Check key is active in MiniMax dashboard

### "Insufficient credits"
- Add credits at: https://platform.minimax.io/billing
- Or switch to Local (Wan2.1) mode for free generation

### "Task failed"
- Check prompt is descriptive
- Ensure image is valid PNG/JPG/WEBP
- Try simpler prompt first

## Comparison: MiniMax vs Local

| Feature | MiniMax Cloud | Local (Wan2.1) |
|---------|---------------|----------------|
| Speed | ~1-2 min | 10-15 min (first), 3-5 min |
| Quality | High | High |
| Cost | API credits | Free |
| VRAM Usage | None | 12-16GB |
| Facial Animation | Better | Limited |
| Availability | Always | Depends on GPU |

## Best Practices

1. **Use clear prompts** - "woman walking, hair blowing in wind"
2. **Keep images simple** - Single subject works best
3. **Shorter is better** - 5 seconds optimal
4. **Check credits** - Before starting generation

## Links

- **Dashboard**: https://platform.minimax.io/
- **API Docs**: https://platform.minimax.io/docs/guides/video-generation
- **Billing**: https://platform.minimax.io/billing
