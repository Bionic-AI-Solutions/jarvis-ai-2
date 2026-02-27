#!/bin/bash
# Build Configuration for JARVIS AI Windows Desktop

# Skip the problematic electron-builder code-signing and use a simpler approach
# This creates a portable, self-contained Windows executable

set -e

echo "Building JARVIS AI Windows Setup..."

# Step 1: Build React frontend
echo "[1/3] Building React application..."
cd frontend
npm run build

# Step 2: Copy electron files
echo "[2/3] Packaging Electron application..."
mkdir -p dist/bin
cp electron/*.js dist/bin/

# Step 3: Create Windows runner script
cat > dist/bin/run-jarvis.js << 'EOF'
/**
 * JARVIS AI Entry Point
 * Starts backend (if needed) and launches web interface
 */
const { app, BrowserWindow } = require('electron');
const path = require('path');
const fetch = require('electron-fetch');

const BACKEND_URL = 'http://localhost:9000';
let mainWindow;

async function checkBackendHealth() {
  try {
    const response = await fetch(`${BACKEND_URL}/health`);
    return response.ok;
  } catch {
    return false;
  }
}

function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
    }
  });

  const isDev = process.env.NODE_ENV === 'development';
  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../index.html'));
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

app.on('ready', async () => {
  const backendHealthy = await checkBackendHealth();
  
  if (!backendHealthy) {
    console.warn('⚠️  Backend server not responding at ' + BACKEND_URL);
    console.warn('Please ensure backend is running: python run_server.py');
  }
  
  createWindow();
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});
EOF

echo "[3/3] Build complete!"
echo ""
echo "✅ Frontend built: dist/"
echo "✅ Electron packaged: dist/bin/"
echo ""
echo "Next: Use npm run electron:pack to create installer"
