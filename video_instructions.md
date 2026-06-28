# VideoForge — AI Short Film Pipeline

Create viral AI short films like "Olivia Vlogs in Space" using open-source tools running locally on your RTX 5080.

## Quick Start

1. **Open VideoForge**: http://192.168.1.3:8889
2. **Upload a reference image** — your character (consistent face across all episodes)
3. **Enter motion prompt** — describe what happens in the scene
4. **Click Generate** — wait 3-5 minutes for a 5-second clip
5. **Chain clips together** — use last frame of clip A as reference for clip B

## The Pipeline (Olivia Method Clone)

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐     ┌──────────────┐
│  Reference  │ ──► │  Wan2.1 I2V  │ ──► │  F5-TTS     │ ──► │   FFmpeg /   │
│   Image     │     │  (ComfyUI)   │     │  (Voice)    │     │   Resolve    │
└─────────────┘     └──────────────┘     └─────────────┘     └──────────────┘
   Character           5-sec clip          Narration          Final edit
   stills              animation           audio              + music
```

### Step 1: Character Design (FLUX + IPAdapter)

Generate consistent character stills using FLUX with IPAdapter FaceID. This is your "storyboard" — each scene starts as a still image.

**Key**: Same face, same uniform, same lighting style across ALL episodes.

### Step 2: Animate Stills (Wan2.1 I2V)

The Wan2.1 Image-to-Video model animates your stills into 5-second clips.

**Settings for 5-second clips:**
- Resolution: 832x480 (landscape) or 480x832 (vertical for TikTok/Shorts)
- Frames: 81 at 16fps = 5.06 seconds
- Steps: 20 (higher = better quality, slower)
- CFG: 6.0 (guidance strength)
- Shift: 8.0 (Wan2.1 flow-matching parameter)
- Sampler: uni_pc (recommended for Wan)
- Scheduler: simple

**Generation time**: ~3-5 minutes per clip on RTX 5080

### Step 3: Voice Narration (F5-TTS)

Generate first-person vlog-style narration using F5-TTS zero-shot voice cloning.

```bash
# Example usage
cd /home/marc/.hermes/skills/creative/ai-short-filmmaking/scripts
./generate_voice.sh "ref.wav" "Reference audio text" "Your episode narration here" output.wav
```

**Tip**: Record a 5-second sample of the voice you want, then clone it. Use the same voice for every episode.

### Step 4: Clip Chaining (30-second episodes)

Wan2.1 generates 5-second clips. To make 30-second episodes:

1. Generate clip A from still image A
2. Extract the **last frame** of clip A
3. Use last frame as the reference image for clip B
4. Repeat for 6 clips (6 × 5s = 30s)
5. Stitch together with FFmpeg or DaVinci Resolve

```bash
# Extract last frame
ffmpeg -sseof -0.1 -i clip_A.mp4 -frames:v 1 last_frame.png

# Stitch clips
ffmpeg -f concat -safe 0 -i filelist.txt -c copy episode.mp4
```

### Step 5: Final Edit

Combine video + voice + music + subtitles in DaVinci Resolve (free) or FFmpeg.

```bash
# Simple FFmpeg combine
ffmpeg -i video.mp4 -i voice.wav -c:v copy -c:a aac -shortest combined.mp4
```

## Hardware Requirements

| Component | Minimum | Recommended |
|-----------|---------|-------------|
| GPU | RTX 3090 (24GB) | RTX 5080 (16GB) |
| VRAM | 16GB (Q4 quant) | 16GB (Q5 quant) |
| RAM | 32GB | 64GB |
| Storage | 100GB free | 500GB+ NVMe |

**Your setup**: RTX 5080 16GB — perfect for Q5_K_S quantization.

## Model Files (Already Downloaded)

| Model | Location | Size |
|-------|----------|------|
| Wan2.1 I2V 14B Q5_K_S | `unet/wan2.1-i2v-14b-480p-Q5_K_S.gguf` | 12GB |
| UMT5-XXL Text Encoder | `text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors` | 6.3GB |
| Wan2.1 VAE | `vae/wan_2.1_vae.safetensors` | 243MB |
| CLIP Vision H | `clip_vision/clip_vision_h.safetensors` | 1.2GB |

## Workflow Nodes (ComfyUI)

| Node | Type | Purpose |
|------|------|---------|
| 37 | UnetLoaderGGUF | Loads Wan2.1 GGUF model |
| 38 | CLIPLoader | UMT5 text encoder (type: wan) |
| 39 | VAELoader | Wan2.1 VAE |
| 49 | CLIPVisionLoader | CLIP vision encoder |
| 50 | WanImageToVideo | Creates latent from image + prompts |
| 51 | CLIPVisionEncode | Encodes reference image |
| 52 | LoadImage | Uploaded reference image |
| 54 | ModelSamplingSD3 | Flow-matching shift (8.0) |
| 6, 7 | CLIPTextEncode | Positive/negative prompts |
| 3 | KSampler | Denoising (20 steps, cfg=6) |
| 8 | VAEDecode | Latent → frames |
| 28 | SaveAnimatedWEBP | Output video |

## Tips for Viral Quality

1. **3-second hook** — Start every episode with something attention-grabbing
2. **First-person vlog** — "I woke up alone on the ship..." creates parasocial connection
3. **Cliffhanger endings** — Each episode ends mid-action
4. **Consistent character** — Same face, uniform, ship across ALL episodes
5. **Vertical format** (480x832) — Better for TikTok/Shorts discovery
6. **Serialize** — Number episodes (EP1, EP2...), create bingeable series
7. **Background music** — Add subtle ambient/cinematic music in editing

## Troubleshooting

**"ComfyUI Offline"**: Ensure Docker container is running: `docker ps | grep comfyui`

**"Model not found"**: Check file exists at `/home/marc/nvme-data/ai-models/comfyui/unet/wan2.1-i2v-14b-480p-Q5_K_S.gguf`

**Out of memory**: Reduce resolution or use Q4_K_S quant instead of Q5_K_S

**Slow generation**: Normal — 3-5 min per 5s clip at 480p on RTX 5080

**WebSocket not connecting**: Frontend falls back to HTTP polling automatically

## Access

- **VideoForge Frontend**: http://192.168.1.3:8889
- **ComfyUI Direct**: http://192.168.1.3:8188
- **PhotoForge (images)**: http://192.168.1.3:8888

## Skills Reference

Full documentation saved to: `~/.hermes/skills/creative/ai-short-filmmaking/SKILL.md`

Helper scripts:
- `~/.hermes/skills/creative/ai-short-filmmaking/scripts/generate_voice.sh`
- `~/.hermes/skills/creative/ai-short-filmmaking/scripts/stitch_clips.sh`
- `~/.hermes/skills/creative/ai-short-filmmaking/scripts/extract_last_frame.sh`
