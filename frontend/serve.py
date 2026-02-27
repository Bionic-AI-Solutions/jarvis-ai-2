#!/usr/bin/env python3
"""
JARVIS AI Frontend Server
Serves the React build and auto-opens in browser
"""

import os
import sys
import time
import webbrowser
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

FRONTEND_PORT = 3000
BACKEND_URL = "http://localhost:9000"

class ReactHTTPRequestHandler(SimpleHTTPRequestHandler):
    """Serve React SPA with proper routing"""
    
    def do_GET(self):
        """Handle routing for React SPA"""
        # Serve index.html for unknown routes (React Router)
        if not self.path.startswith('/assets/') and not '.' in self.path:
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        """Less verbose logging"""
        if '200' in str(args):
            print(f'[HTTP] {args[0]}')

def start_server():
    """Start the HTTP server"""
    os.chdir(Path(__file__).parent / 'dist')
    
    server = HTTPServer(('localhost', FRONTEND_PORT), ReactHTTPRequestHandler)
    print(f'[*] HTTP Server listening on http://localhost:{FRONTEND_PORT}')
    
    # Run server in background thread
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    return server

def main():
    print("=" * 50)
    print("  JARVIS AI Frontend Server")
    print("=" * 50)
    print()
    
    # Check backend
    print(f"[*] Checking backend at {BACKEND_URL}...")
    try:
        import urllib.request
        urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=2)
        print("[✓] Backend is running")
    except:
        print("[!] Warning: Backend not reachable at " + BACKEND_URL)
        print("    Please start: cd backend && python run_server.py")
        print()
    
    # Check that we have dist folder
    dist_path = Path(__file__).parent / 'dist'
    if not dist_path.exists():
        print(f"[ERROR] dist/ folder not found at {dist_path}")
        print("Run: npm run build")
        sys.exit(1)
    
    print(f"[*] Serving from: {dist_path}")
    print()
    
    # Start server
    server = start_server()
    
    print(f"[✓] Frontend ready at http://localhost:{FRONTEND_PORT}")
    print()
    
    # Open browser
    time.sleep(1)
    print("[*] Opening browser...")
    webbrowser.open(f"http://localhost:{FRONTEND_PORT}")
    
    print()
    print("=" * 50)
    print("  Press Ctrl+C to stop")
    print("=" * 50)
    print()
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")
        server.shutdown()
        print("[✓] Goodbye!")

if __name__ == '__main__':
    main()
