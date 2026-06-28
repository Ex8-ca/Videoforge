#!/usr/bin/env python3
"""
Together.ai Bridge Service
Exposes Together.ai video generation via local REST API.
Uses official Together Python SDK (which has proper API access).

Run: python3 together_bridge.py
Port: 9000
"""

import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Try to import together SDK
try:
    from together import Together
    TOGETHER_AVAILABLE = True
except ImportError:
    TOGETHER_AVAILABLE = False
    print("WARNING: together SDK not installed. Run: pip install together")

# Your Together.ai API key
TOGETHER_API_KEY = "tgp_v1_GxSXE3v-k5RrSFq-EQ17BiqSyW8jfuMmOyTRi8hf1uE"

# Task storage (in-memory)
tasks = {}

class TogetherBridgeHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        print(f"[Bridge] {args[0]}")
    
    def send_json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data).encode())
    
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def do_GET(self):
        parsed = urlparse(self.path)
        
        # Health check
        if parsed.path == '/health':
            self.send_json({
                'status': 'ok',
                'sdk_available': TOGETHER_AVAILABLE
            })
            return
        
        # Get task status: /status/{task_id}
        if parsed.path.startswith('/status/'):
            task_id = parsed.path.split('/')[-1]
            if task_id in tasks:
                self.send_json(tasks[task_id])
            else:
                self.send_json({'error': 'Task not found'}, 404)
            return
        
        self.send_json({'error': 'Not found'}, 404)
    
    def do_POST(self):
        parsed = urlparse(self.path)
        
        # Generate video: /generate
        if parsed.path == '/generate':
            if not TOGETHER_AVAILABLE:
                self.send_json({
                    'error': 'Together SDK not installed. Run: pip install together'
                }, 503)
                return
            
            content_len = int(self.headers.get('Content-Length', 0))
            body = self.rfile.read(content_len)
            
            try:
                data = json.loads(body)
                prompt = data.get('prompt', '')
                image = data.get('image', '')
                
                if not prompt:
                    self.send_json({'error': 'Prompt is required'}, 400)
                    return
                
                # Start generation in background thread
                task_id = f"task_{int(time.time() * 1000)}"
                tasks[task_id] = {
                    'status': 'processing',
                    'prompt': prompt,
                    'created_at': time.time()
                }
                
                # Start background generation
                thread = threading.Thread(
                    target=generate_video,
                    args=(task_id, prompt, image)
                )
                thread.daemon = True
                thread.start()
                
                self.send_json({'task_id': task_id})
                
            except Exception as e:
                self.send_json({'error': str(e)}, 500)
            return
        
        self.send_json({'error': 'Not found'}, 404)

def generate_video(task_id, prompt, image_data_url):
    """Generate video using Together.ai SDK in background thread"""
    try:
        print(f"[Bridge] Starting generation for task {task_id}")
        
        # Initialize Together client
        client = Together(api_key=TOGETHER_API_KEY)
        
        # Extract base64 from data URL if present
        image_url = None
        if image_data_url and image_data_url.startswith('data:'):
            # For Together.ai, we need a public URL or upload first
            # For now, we'll do text-to-video only
            print(f"[Bridge] Image provided but Together requires public URL. Using text-to-video.")
            image_url = None
        
        # Create video generation request
        # Together.ai video API via SDK
        response = client.videos.create(
            model="ByteDance/Seedance-1.0-pro",
            prompt=prompt,
            # Note: image_to_video requires image upload first via their platform
            # For now we do text-to-video
            width=1920,
            height=1088,
            seconds=5,
            output_format="MP4"
        )
        
        video_id = response.id
        print(f"[Bridge] Created video task: {video_id}")
        
        # Poll for completion
        max_wait = 600  # 10 minutes
        waited = 0
        
        while waited < max_wait:
            time.sleep(10)
            waited += 10
            
            # Check status
            status_response = client.videos.retrieve(video_id)
            status = status_response.status
            
            print(f"[Bridge] Task {video_id} status: {status} ({waited}s)")
            
            if status == 'completed':
                # Video URL is nested under outputs
                video_url = status_response.outputs.video_url if status_response.outputs else None
                cost = status_response.outputs.cost if status_response.outputs else None
                tasks[task_id] = {
                    'status': 'completed',
                    'video_url': video_url,
                    'cost': cost,
                    'prompt': prompt,
                    'completed_at': time.time()
                }
                print(f"[Bridge] Task {task_id} completed: {video_url} (cost: ${cost})")
                return
            
            if status == 'failed':
                error_msg = getattr(status_response, 'error', 'Unknown error')
                tasks[task_id] = {
                    'status': 'failed',
                    'error': str(error_msg),
                    'prompt': prompt
                }
                print(f"[Bridge] Task {task_id} failed: {error_msg}")
                return
        
        # Timeout
        tasks[task_id] = {
            'status': 'failed',
            'error': 'Generation timed out after 10 minutes'
        }
        
    except Exception as e:
        print(f"[Bridge] Generation error: {e}")
        tasks[task_id] = {
            'status': 'failed',
            'error': str(e)
        }

def main():
    port = 9000
    # Listen on all interfaces so VideoForge can reach it
    server = HTTPServer(('0.0.0.0', port), TogetherBridgeHandler)
    
    print(f"""
╔══════════════════════════════════════╗
║   Together.ai Bridge Service         ║
║   Running on http://127.0.0.1:{port}    ║
╠══════════════════════════════════════╣
║   SDK Available: {str(TOGETHER_AVAILABLE):5}           ║
║   API Key: {TOGETHER_API_KEY[:20]}... ║
╠══════════════════════════════════════╣
║   Endpoints:                         ║
║   POST /generate  - Start generation ║
║   GET  /status/id - Check status     ║
║   GET  /health    - Health check     ║
╚══════════════════════════════════════╝

Press Ctrl+C to stop
""")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down...")
        server.shutdown()

if __name__ == '__main__':
    main()
