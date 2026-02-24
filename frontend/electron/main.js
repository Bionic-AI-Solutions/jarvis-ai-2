/**
 * Electron main process — JARVIS AI Desktop Shell
 *
 * Story 7.11: Electron UI Shell
 * - Creates BrowserWindow pointing at React dev server (dev) or built files (prod)
 * - IPC bridge for backend communication
 * - System tray and global shortcuts
 */

const { app, BrowserWindow, ipcMain, globalShortcut } = require('electron');
const path = require('path');

const isDev = process.env.NODE_ENV !== 'production';
const BACKEND_URL = process.env.JARVIS_BACKEND_URL || 'http://127.0.0.1:9000';

let mainWindow = null;

function createWindow() {
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
      sandbox: true,
    },
  });

  if (isDev) {
    mainWindow.loadURL('http://localhost:3000');
    mainWindow.webContents.openDevTools();
  } else {
    mainWindow.loadFile(path.join(__dirname, '../dist/index.html'));
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

app.whenReady().then(() => {
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
});
