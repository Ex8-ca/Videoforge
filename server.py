#!/usr/bin/env python3
"""VideoForge frontend + ComfyUI reverse proxy on a single port."""
import http.server
import urllib.request
import urllib.error
import os
import json
import gzip
from urllib.parse import urlparse, parse_qs

COMFYUI = "http://127.0.0.1:8188"
# MiniMax API key — loaded from env, with local fallback
_MINIMAX_KEY = os.environ.get("MINIMAX_API_VIDEOFORGE", "")
if not _MINIMAX_KEY:
    print("FATAL: MINIMAX_API_VIDEOFORGE is not set. Source your .env before starting.", file=__import__("sys").stderr)
    __import__("sys").exit(1)
MINIMAX_VIDEO_API_KEY = _MINIMAX_KEY
MINIMAX_VIDEO_URL = "https://api.minimax.io/v1/video_generation"
MINIMAX_VIDEO_QUERY_URL = "https://api.minimax.io/v1/query/video_generation"
MINIMAX_FILES_URL = "https://api.minimax.io/v1/files/retrieve"
FRONTEND_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".")

class ProxyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def do_GET(self):
        if self.path.startswith("/api/"):
            self.proxy("GET")
        elif self.path.startswith("/together/"):
            self.proxy_together("GET")
        elif self.path.startswith("/minimax/status/"):
            self.handle_minimax_status()
        elif self.path.startswith("/minimax/download/"):
            self.handle_minimax_download()
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy("POST")
        elif self.path.startswith("/together/"):
            self.proxy_together("POST")
        elif self.path == "/minimax/create":
            self.handle_minimax_create()
        else:
            self.send_error(404)

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, DELETE, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _minimax_request(self, method, url, data=None, query_params=None):
        """Helper for MiniMax API calls."""
        if query_params:
            qs = "&".join(f"{k}={v}" for k, v in query_params.items())
            url = f"{url}?{qs}"
        req = urllib.request.Request(url, method=method)
        req.add_header("Authorization", f"Bearer {MINIMAX_VIDEO_API_KEY}")
        req.add_header("Content-Type", "application/json")
        req.add_header("User-Agent", "VideoForge/1.0")
        if data:
            req.data = json.dumps(data).encode()
        with urllib.request.urlopen(req, timeout=300) as resp:
            raw = resp.read()
            if resp.headers.get("Content-Encoding") == "gzip":
                raw = gzip.decompress(raw)
            return json.loads(raw)

    def handle_minimax_create(self):
        """POST /minimax/create — start video generation (T2V or I2V)."""
        try:
            content_len = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(content_len))
        except Exception as e:
            self._send_json(400, {"error": f"Invalid request: {e}"})
            return

        print(f"[MiniMax] Creating video: model={body.get('model')} prompt='{body.get('prompt', '')[:80]}...'")

        payload = {
            "model": body.get("model", "MiniMax-Hailuo-2.3"),
            "prompt": body.get("prompt", ""),
        }
        if "duration" in body:
            payload["duration"] = body["duration"]
        if "resolution" in body:
            payload["resolution"] = body["resolution"]
        if "prompt_optimizer" in body:
            payload["prompt_optimizer"] = body["prompt_optimizer"]
        if "fast_pretreatment" in body:
            payload["fast_pretreatment"] = body["fast_pretreatment"]
        # I2V: first frame image (URL or data URL)
        if "first_frame_image" in body:
            payload["first_frame_image"] = body["first_frame_image"]
        # S2V: subject reference
        if "subject_reference" in body:
            payload["subject_reference"] = body["subject_reference"]
        if "audio_url" in body:
            payload["audio_url"] = body["audio_url"]

        try:
            result = self._minimax_request("POST", MINIMAX_VIDEO_URL, data=payload)
            base_resp = result.get("base_resp", {})
            if base_resp.get("status_code") != 0:
                self._send_json(500, {"error": f"MiniMax error: {base_resp.get('status_msg', 'Unknown')}"})
                return
            self._send_json(200, result)
        except urllib.error.HTTPError as e:
            err_body = e.read() if e.fp else b""
            self._send_json(e.code, {"error": f"HTTP {e.code}: {err_body.decode()[:500]}"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def handle_minimax_status(self):
        """GET /minimax/status/<task_id> — poll task status."""
        task_id = self.path[len("/minimax/status/"):]
        if not task_id:
            self._send_json(400, {"error": "Missing task_id"})
            return
        try:
            result = self._minimax_request("GET", MINIMAX_VIDEO_QUERY_URL, query_params={"task_id": task_id})
            self._send_json(200, result)
        except urllib.error.HTTPError as e:
            err_body = e.read() if e.fp else b""
            self._send_json(e.code, {"error": f"HTTP {e.code}: {err_body.decode()[:500]}"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def handle_minimax_download(self):
        """GET /minimax/download/<file_id> — get download URL."""
        file_id = self.path[len("/minimax/download/"):]
        if not file_id:
            self._send_json(400, {"error": "Missing file_id"})
            return
        try:
            result = self._minimax_request("GET", MINIMAX_FILES_URL, query_params={"file_id": file_id})
            self._send_json(200, result)
        except urllib.error.HTTPError as e:
            err_body = e.read() if e.fp else b""
            self._send_json(e.code, {"error": f"HTTP {e.code}: {err_body.decode()[:500]}"})
        except Exception as e:
            self._send_json(500, {"error": str(e)})

    def proxy(self, method):
        comfyui_path = self.path[4:]  # strip "/api"
        url = COMFYUI + comfyui_path
        try:
            if method == "POST":
                content_type = self.headers.get("Content-Type", "")
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len) if content_len > 0 else None
                req = urllib.request.Request(url, data=body, method="POST")
                # Only set Content-Type if it's not multipart (preserve boundary for file uploads)
                if content_type and not content_type.startswith("multipart/"):
                    req.add_header("Content-Type", content_type)
                elif content_type:
                    req.add_header("Content-Type", content_type)
            else:
                req = urllib.request.Request(url)

            with urllib.request.urlopen(req, timeout=600) as resp:
                data = resp.read()
                self.send_response(resp.status)
                ct = resp.headers.get("Content-Type", "application/octet-stream")
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", len(data))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            body = e.read() if e.fp else b''
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.URLError as e:
            print(f"[Proxy] URL Error: {e.reason}")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Connection failed: {e.reason}"}).encode())
        except Exception as e:
            print(f"[Proxy] Error: {e}")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def proxy_together(self, method):
        """Proxy requests to Together.ai API to avoid CORS issues"""
        together_path = self.path[len("/together"):]  # strip "/together"
        url = f"https://api.together.xyz{together_path}"
        
        print(f"[Together.ai Proxy] {method} {self.path} -> {url}")
        
        try:
            if method == "POST":
                content_len = int(self.headers.get("Content-Length", 0))
                body = self.rfile.read(content_len) if content_len > 0 else None
                req = urllib.request.Request(url, data=body, method="POST")
                req.add_header("Content-Type", "application/json")
            else:
                req = urllib.request.Request(url)
            
            req.add_header("Authorization", f"Bearer {_MINIMAX_KEY}")
            req.add_header("User-Agent", "Mozilla/5.0")
            req.add_header("Accept", "application/json")
            
            with urllib.request.urlopen(req, timeout=600) as resp:
                raw_data = resp.read()
                if resp.headers.get("Content-Encoding") == "gzip":
                    try:
                        data = gzip.decompress(raw_data)
                    except Exception as e:
                        print(f"[Together.ai Proxy] Gzip error: {e}")
                        data = raw_data
                else:
                    data = raw_data
                
                self.send_response(resp.status)
                ct = resp.headers.get("Content-Type", "application/json")
                self.send_header("Content-Type", ct)
                self.send_header("Content-Length", len(data))
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(data)
        except urllib.error.HTTPError as e:
            body = e.read() if e.fp else b''
            print(f"[Together.ai Proxy] HTTP Error {e.code}: {body[:200]}")
            self.send_response(e.code)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(body)
        except urllib.error.URLError as e:
            print(f"[Together.ai Proxy] URL Error: {e.reason}")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": f"Connection failed: {e.reason}"}).encode())
        except Exception as e:
            print(f"[Together.ai Proxy] Error: {e}")
            self.send_response(502)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())

    def _send_json(self, status_code, data):
        """Send a JSON response."""
        body = json.dumps(data).encode()
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(body))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def end_headers(self):
        # Disable caching for HTML/JS files
        if not self.path.startswith("/api/"):
            self.send_header("Cache-Control", "no-store, no-cache, must-revalidate, max-age=0")
            self.send_header("Pragma", "no-cache")
            self.send_header("Expires", "0")
        super().end_headers()

    def log_message(self, fmt, *args):
        pass

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8889
    server = http.server.HTTPServer(("0.0.0.0", port), ProxyHandler)
    print(f"VideoForge running at http://192.168.1.3:{port}")
    print(f"Proxying /api/* -> {COMFYUI}")
    print(f"MiniMax video: configured")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down")
        server.shutdown()
