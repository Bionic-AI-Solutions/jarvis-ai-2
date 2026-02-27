/**
 * Electron main process — JARVIS AI Desktop Shell
 *
 * Story 7.11: Electron UI Shell
 * - Auto-launches backend server (Python/Uvicorn)
 * - Creates BrowserWindow pointing at React dev server (dev) or built files (prod)
 * - IPC bridge for backend communication
 * - System tray and global shortcuts
 */

const { app, BrowserWindow, ipcMain, globalShortcut } = require('electron');
const path = require('path');
const fs = require('fs');
const { spawn } = require('child_process');
const http = require('http');

let mainWindow = null;
let backendProcess = null;
const isDev = !fs.existsSync(path.join(__dirname, '../dist/index.html'));
const BACKEND_URL = process.env.JARVIS_BACKEND_URL || 'http://127.0.0.1:9000';
const BACKEND_PORT = 9000;
const BACKEND_CHECK_INTERVAL = 500;

async function checkBackendRunning() {
  return new Promise((resolve) => {
    const req = http.get(`${BACKEND_URL}/health`, (res) => {
      resolve(res.statusCode === 200);
    });
    req.on('error', () => resolve(false));
    req.setTimeout(2000);
  });
}

async function waitForBackend(maxAttempts = 30) {
  console.log('[JARVIS] Waiting for backend to be ready...');
  for (let i = 0; i < maxAttempts; i++) {
    if (await checkBackendRunning()) {
      console.log('[JARVIS] Backend is ready!');
      return true;
    }
    console.log(`[JARVIS] Backend check ${i + 1}/${maxAttempts}...`);
    await new Promise(r => setTimeout(r, BACKEND_CHECK_INTERVAL));
  }
  console.warn('[JARVIS] Backend did not respond in time');
  return false;
}

function spawnBackend() {
  if (backendProcess) return;
  
  console.log('[JARVIS] Starting backend server...');
  
  let backendExe;
  if (isDev) {
    // Development: look for PyInstaller-built exe in dist/resources
    backendExe = path.join(__dirname, '../../backend/dist/run_server.exe');
  } else {
    // Production: look in app resources (copied by electron-builder)
    backendExe = path.join(process.resourcesPath, 'run_server.exe');
  }
  
  if (!fs.existsSync(backendExe)) {
    console.error(`[JARVIS] Backend executable not found: ${backendExe}`);
    console.error('[JARVIS] Did you run: npm run build-backend?');
    return;
  }
  
  console.log(`[JARVIS] Spawning: ${backendExe}`);
  
  backendProcess = spawn(backendExe, [], {
    stdio: ['ignore', 'pipe', 'pipe'],
    detached: false,
  });
  
  backendProcess.stdout?.on('data', (data) => {
    console.log(`[Backend] ${data.toString().trim()}`);
  });
  
  backendProcess.stderr?.on('data', (data) => {
    console.error(`[Backend Error] ${data.toString().trim()}`);
  });
  
  backendProcess.on('error', (err) => {
    console.error('[JARVIS] Failed to start backend:', err);
  });
  
  backendProcess.on('exit', (code) => {
    console.log(`[JARVIS] Backend exited with code ${code}`);
    backendProcess = null;
  });
}

function createWindow() {
  try {
    mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 800,
      minHeight: 600,
      title: 'JARVIS AI',
      frame: true,
      backgroundColor: '#1a1a2e',
      webPreferences: {
        preload: path.join(__dirname, 'preload.js'),
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false,
      },
    });

    const indexPath = isDev 
      ? 'http://localhost:3000'
      : `file://${path.join(__dirname, '../dist/index.html')}`;
    
    console.log('[JARVIS] Loading:', indexPath);
    console.log('[JARVIS] Backend:', BACKEND_URL);
    
    if (isDev) {
      mainWindow.loadURL(indexPath);
      mainWindow.webContents.openDevTools();
    } else {
      mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
    }
  } catch (error) {
    console.error('[ERROR]', error);
    process.exit(1);
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

// ── IPC Handlers ──────────────────────────────────────────

ipcMain.handle('jarvis:get-backend-url', () => BACKEND_URL);

ipcMain.handle('jarvis:health-check', async () => {
  try {
    const resp = await fetch(`${BACKEND_URL}/health`);
    return await resp.json();
  } catch {
    return { status: 'error', message: 'Backend unreachable' };
  }
});

ipcMain.handle('jarvis:get-version', () => ({
  electron: process.versions.electron,
  chrome: process.versions.chrome,
  node: process.versions.node,
  app: app.getVersion(),
}));

// ── App Lifecycle ─────────────────────────────────────────

app.whenReady().then(async () => {
  // Try to start backend (works in both dev and production when backend exe is built)
  const backendAlreadyRunning = await checkBackendRunning();
  if (!backendAlreadyRunning) {
    spawnBackend();
    await waitForBackend();
  }
  
  createWindow();

  // Global shortcut: Ctrl+Shift+Alt+J to focus JARVIS
  globalShortcut.register('Ctrl+Shift+Alt+J', () => {
    if (mainWindow) {
      if (mainWindow.isMinimized()) mainWindow.restore();
      mainWindow.focus();
    }
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) createWindow();
  });
});

app.on('window-all-closed', () => {
  if (process.platform !== 'darwin') app.quit();
});

app.on('will-quit', () => {
  globalShortcut.unregisterAll();
  if (backendProcess) {
    console.log('[JARVIS] Terminating backend server...');
    backendProcess.kill('SIGTERM');
    backendProcess = null;
  }
});
