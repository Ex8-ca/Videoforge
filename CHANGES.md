# VideoForge Changelog

## Latest Updates (March 31, 2026)

### 1. History Persistence Fixed ✅

**Problem:** Generated videos weren't saved to history after page refresh.

**Fix:** 
- History now persists to browser `localStorage`
- Automatically loads on page load
- Stores: video URL, seed, timestamp, cloudinary URL (if uploaded)

**Location:** `index.html` - `addToHistory()` and init function

---

### 2. Cloudinary Upload Integration ✅

**Feature:** Upload generated videos to Cloudinary cloud storage.

**How to use:**
1. Generate a video locally
2. Click "Upload to Cloud" button
3. First time: Enter your Cloudinary credentials:
   - **Cloud Name**: Your cloud name (e.g., `dxxxxx`)
   - **Upload Preset**: Create an unsigned preset in Cloudinary dashboard
4. Video uploads to `videoforge` folder
5. URL copied to clipboard automatically

**Cloudinary Setup:**
1. Go to https://cloudinary.com/users/register/free
2. Create account (free tier: 25GB storage, 25GB bandwidth/month)
3. Go to Settings → Upload → Add upload preset
4. Set signing mode to "Unsigned"
5. Set folder to "videoforge" (optional)
6. Copy the preset name

**Files modified:**
- `index.html` - Added `uploadToCloudinary()` function
- Added "Upload to Cloud" button in video actions bar

---

### 3. Together.ai API Format Fixed ✅

**Problem:** API returning 400 Bad Request - invalid parameters.

**Fix:** Updated request format to match Together.ai spec:
```json
{
  "model": "ByteDance/Seedance-1.0-pro",
  "prompt": "...",
  "frame_images": ["data:image/png;base64,..."],
  "width": 1920,
  "height": 1088,
  "seconds": 5,
  "output_format": "MP4"
}
```

**Note:** Together.ai API key currently returning 403 - may need new key or wait for rate limit reset.

---

### 4. Server Proxy for Together.ai ✅

**Feature:** All Together.ai requests now proxied through VideoForge server to avoid CORS issues.

**Endpoint:** `/together/v2/videos` → `https://api.together.ai/v2/videos`

**Files modified:**
- `server.py` - Added `proxy_together()` method
- `index.html` - Updated fetch calls to use proxy

---

## File Locations

| File | Path | Purpose |
|------|------|---------|
| Frontend | `/home/marc/videoforge/index.html` | Main UI |
| Server | `/home/marc/videoforge/server.py` | Python proxy server |
| Output | `/home/marc/.comfyui/output/` | Generated videos (WEBP) |
| Skill | `~/.hermes/skills/creative/videoforge/` | Documentation |

---

## Quick Start

### Local Generation (Working)
1. Open http://192.168.1.3:8889
2. Hard refresh (Ctrl+Shift+R)
3. Select "Local (Wan2.1)" mode
4. Upload reference image
5. Enter motion prompt
6. Click Generate (10-15 min first run, 3-5 min after)
7. Video saved to history automatically

### Cloudinary Upload
1. After video generates, click "Upload to Cloud"
2. Enter Cloudinary credentials (saved for next time)
3. Wait for upload (~30 seconds)
4. URL copied to clipboard

### Together.ai (Needs API Key Fix)
1. Select "Together.ai" mode
2. Pick model
3. Upload image + enter prompt
4. Click Generate (~1-2 min)
5. **Note:** Current API key getting 403 errors

---

## Troubleshooting

### History not showing
- Hard refresh browser (Ctrl+Shift+R)
- Check browser console for errors
- localStorage may be cleared if using incognito mode

### Cloudinary upload fails
- Verify cloud name is correct (found in Cloudinary dashboard)
- Ensure upload preset is "unsigned"
- Check file size (free tier: max 10MB per upload)
- Check browser console for CORS errors

### Together.ai 403 error
- API key may be rate-limited or invalid
- Generate new key at https://api.together.ai/settings/api-keys
- Wait a few hours if rate-limited

### 502 Bad Gateway
- ComfyUI container may be stopped
- Run: `docker start comfyui`
- Restart VideoForge: `pkill -f server.py && cd /home/marc/videoforge && python3 server.py &`

---

## Video Output Format

- **Format:** Animated WEBP (ComfyUI default)
- **Location:** `/home/marc/.comfyui/output/videoforge_*.webp`
- **Size:** ~4-8MB per 5-second clip
- **Playback:** Opens in browser, can be downloaded

To convert to MP4:
```bash
ffmpeg -i videoforge_00001_.webp -c:v libx264 -pix_fmt yuv420p output.mp4
```
