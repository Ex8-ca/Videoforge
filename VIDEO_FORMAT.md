# Video Format: MP4 vs WEBP

## Why We Changed to MP4 ✅

### Problem with WEBP
- **WEBP is an image format**, not a video format
- Animated WEBP exists but has limited support
- Cloudinary's video API **doesn't accept WEBP**
- Many platforms don't support animated WEBP playback

### Benefits of MP4
- ✅ **Universal compatibility** - plays everywhere
- ✅ **Cloudinary supports it** - uploads work
- ✅ **Better compression** - smaller files, better quality
- ✅ **Hardware acceleration** - faster playback
- ✅ **Standard format** - works on all devices/browsers

---

## Changes Made

### 1. ComfyUI Workflow Output
**Before:** `SaveAnimatedWEBP` → `.webp` files
**After:** `VHS_VideoCombine` → `.mp4` files (H.264 codec)

### 2. Frontend Updates
- Download filename: `.mp4` instead of `.webp`
- History preview: checks for `.mp4` and `.webm`
- Cloudinary upload: sends `.mp4` files

### 3. Output Location
Videos saved to: `/home/marc/.comfyui/output/videoforge_*.mp4`

---

## Video Specifications

| Setting | Value |
|---------|-------|
| **Format** | MP4 (H.264) |
| **Codec** | h264-mp4 |
| **Pixel Format** | yuv420p (compatible with all players) |
| **CRF** | 23 (good quality/size balance) |
| **Frame Rate** | 16 fps (configurable) |
| **Resolution** | 832x480 or 480x832 (configurable) |

---

## File Size Comparison

| Duration | WEBP (old) | MP4 (new) |
|----------|------------|-----------|
| 5 seconds | ~4-8 MB | ~2-4 MB |
| 30 seconds | ~24-48 MB | ~12-24 MB |

MP4 is typically **50% smaller** with better quality!

---

## Cloudinary Upload

Now uploads work correctly:
```
https://res.cloudinary.com/dol2t3l5x/video/upload/videoforge/videoforge_12345.mp4
```

### Supported Cloudinary Formats
- ✅ MP4 (recommended)
- ✅ WebM
- ✅ MOV
- ✅ AVI
- ✅ FLV
- ❌ WEBP (not supported for video)

---

## Testing

1. **Hard refresh** browser (Ctrl+Shift+R)
2. **Generate a new video** (existing WEBP files won't convert automatically)
3. **Check output**: `/home/marc/.comfyui/output/videoforge_*.mp4`
4. **Upload to Cloudinary**: Should work now!

---

## Converting Old WEBP Files

To convert existing WEBP files to MP4:
```bash
cd /home/marc/.comfyui/output/
for f in videoforge_*.webp; do
    ffmpeg -i "$f" -c:v libx264 -pix_fmt yuv420p "${f%.webp}.mp4"
done
```

---

## Troubleshooting

### "No video output"
- Ensure VHS (VideoHelperSuite) custom node is installed
- Check ComfyUI logs for errors
- Verify `video/h264-mp4` format is supported

### "Upload still fails"
- Check file extension is `.mp4`
- Verify Cloudinary credentials are correct
- Check browser console for errors

### "Video won't play"
- Try different browser
- Check if file downloaded completely
- Verify codec compatibility (H.264 + yuv420p)
