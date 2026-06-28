# VideoForge

AI video generation frontend supporting multiple backends — local ComfyUI (Wan2.1), MiniMax Hailuo, Together.ai, and OVI (video+audio with lip-sync).

## Features

- **Local (Wan2.1)** — GGUF-quantized image-to-video via ComfyUI. Free, runs on your GPU. Full control over steps, CFG, sampler, scheduler, seed, FPS.
- **MiniMax Hailuo 2.3** — Cloud text-to-video and image-to-video. High quality, fast (~1-2 min). Camera movement controls via `[Pan left]`, `[Push in]`, etc.
- **Together.ai** — Cloud video generation via Together API (Seedance model).
- **OVI (Character.AI)** — Video + audio with lip-sync. Single subject speaks your prompt.

## Quick Start

```bash
# Start the server (loads API keys from ~/.hermes/.env)
bash run.sh 8889

# Or directly (make sure MINIMAX_API_KEY is in your environment)
python3 server.py 8889
```

Open http://localhost:8889 in your browser.

## Architecture

```
┌─────────────┐     ┌──────────────────┐     ┌──────────────┐
│  Browser    │────▶│  server.py :8889 │────▶│ ComfyUI :8188│
│  (index.html)│     │  (proxy + API)   │     │  (Wan2.1)    │
└─────────────┘     └────────┬─────────┘     └──────────────┘
                             │
                    ┌────────▼─────────┐
                    │ MiniMax API      │
                    │ Together.ai API  │
                    │ Cloudinary       │
                    └──────────────────┘
```

### Backend Routes

| Route | Purpose |
|-------|---------|
| `/api/*` | Proxy to ComfyUI |
| `/minimax/create` | Start MiniMax video generation (T2V/I2V) |
| `/minimax/status/<task_id>` | Poll MiniMax task status |
| `/minimax/download/<file_id>` | Get MiniMax video download URL |
| `/together/*` | Proxy to Together.ai API |

## Configuration

### Environment Variables

Load via `run.sh` (sources `~/.hermes/.env`) or set manually:

| Variable | Purpose |
|----------|---------|
| `MINIMAX_API_KEY` | MiniMax API key (starts with `sk-api--`) |

### MiniMax Video API

- **Endpoint:** `https://api.minimax.io/v1/video_generation`
- **Models:** `MiniMax-Hailuo-2.3`, `MiniMax-Hailuo-02`, `T2V-01-Director`, `T2V-01`
- **Resolutions:** `720P`, `768P`, `1080P` (model-dependent)
- **Durations:** `6` or `10` seconds (model-dependent)
- **Camera controls:** `[Pan left]`, `[Push in]`, `[Pedestal up]`, `[Zoom out]`, etc.

## Dependencies

- Python 3.11+ (uses stdlib `http.server`, `urllib`, `json`)
- ComfyUI running on `:8188` for local generation
- MiniMax API key for cloud generation
- Together.ai API key (for Together mode)

## License

MIT
