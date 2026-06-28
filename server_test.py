#!/usr/bin/env python3
"""Minimal test server for Together.ai proxy"""
import http.server
import urllib.request
import json

TOGETHER_API_KEY = "tgp_v1_GxSXE3v-k5RrSFq-EQ17BiqSyW8jfuMmOyTRi8hf1uE"

class TestHandler(http.server.BaseHTTPRequestHandler):
    def do_POST(self):
        print(f"[TEST] POST {self.path}")
        if self.path == "/test/together":
            # Test Together.ai proxy
            content_len = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_len)
            
            url = "https://api.together.ai/v2/videos"
            req = urllib.request.Request(url, data=body, method="POST")
            req.add_header("Content-Type", "application/json")
            req.add_header("Authorization", f"Bearer {TOGETHER_API_KEY}")
            
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    data = resp.read()
                    self.send_response(resp.status)
                    self.send_header("Content-Type", "application/json")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(data)
                    print(f"[TEST] Success: {resp.status}")
            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json")
                self.end_headers()
                self.wfile.write(json.dumps({"error": str(e)}).encode())
                print(f"[TEST] Error: {e}")
        else:
            self.send_response(404)
            self.end_headers()
    
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Test server running!")
    
    def log_message(self, format, *args):
        pass

if __name__ == "__main__":
    server = http.server.HTTPServer(("0.0.0.0", 9999), TestHandler)
    print("Test server on port 9999")
    server.serve_forever()
