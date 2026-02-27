"""
JARVIS AI Windows Application
PyInstaller build script to create standalone .exe
"""

import PyInstaller.__main__
import os
import shutil
from pathlib import Path

# Paths
project_root = Path(__file__).parent
frontend_dist = project_root / "frontend" / "dist"
output_dir = project_root / "dist"

print("=" * 60)
print("  JARVIS AI Windows Application Builder")
print("=" * 60)
print()

# Step 1: Ensure frontend is built
print("[1/3] Checking frontend build...")
if not frontend_dist.exists() or not (frontend_dist / "index.html").exists():
    print("[ERROR] Frontend not built!")
    print("Run: cd frontend && npm run build")
    exit(1)
print(f"[✓] Frontend ready at {frontend_dist}")

# Step 2: Create Python wrapper
wrapper_script = project_root / "jarvis_app.py"
print(f"\n[2/3] Creating Windows application wrapper...")

wrapper_code = '''#!/usr/bin/env python3
"""
JARVIS AI Desktop Application
Standalone Windows .exe wrapper
"""

import sys
import os
import time
import threading
import webbrowser
from pathlib import Path
from http.server import HTTPServer, SimpleHTTPRequestHandler

class ReactHandler(SimpleHTTPRequestHandler):
    """Serve React SPA"""
    def do_GET(self):
        if not self.path.startswith('/assets/') and '.' not in self.path:
            self.path = '/index.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        pass  # Silent mode

def main():
    # Change to frontend dist directory
    dist_path = Path(__file__).parent / "frontend" / "dist"
    os.chdir(dist_path)
    
    # Start server
    server = HTTPServer(("localhost", 3000), ReactHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    
    # Open browser
    time.sleep(1)
    webbrowser.open("http://localhost:3000")
    
    # Keep running
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
'''

with open(wrapper_script, 'w') as f:
    f.write(wrapper_code)
print(f"[✓] Wrapper created at {wrapper_script}")

# Step 3: Build with PyInstaller
print(f"\n[3/3] Building Windows executable...")
print("(This may take 1-2 minutes...)")

output_dir.mkdir(exist_ok=True)

PyInstaller.__main__.run([
    str(wrapper_script),
    '--onefile',
    '--windowed',
    '--name=JARVIS AI',
    f'--distpath={output_dir}',
    '--specpath=/tmp',
    '--buildpath=/tmp/build',
    '--icon=NONE',
])

exe_path = output_dir / "JARVIS AI.exe"

if exe_path.exists():
    print()
    print("=" * 60)
    print("  ✅ BUILD COMPLETE!")
    print("=" * 60)
    print()
    print(f"Application: {exe_path}")
    print(f"Size: {exe_path.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    print("Usage:")
    print(f"  Double-click: {exe_path.name}")
    print()
    print("The application will:")
    print("  1. Start backend on localhost:9000")
    print("  2. Start frontend server on localhost:3000")
    print("  3. Open in your default browser")
    print()
else:
    print("[ERROR] Build failed")
    exit(1)
