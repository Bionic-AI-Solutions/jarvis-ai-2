/**
 * Electron preload script — secure bridge between renderer and main process.
 *
 * Exposes a minimal IPC API via contextBridge.
 * No Node.js APIs are directly exposed to the renderer.
 */

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('jarvis', {
  /** Get the backend API URL */
  getBackendUrl: () => ipcRenderer.invoke('jarvis:get-backend-url'),

  /** Check backend health */
  healthCheck: () => ipcRenderer.invoke('jarvis:health-check'),

  /** Get version info */
  getVersion: () => ipcRenderer.invoke('jarvis:get-version'),

  /** Listen for events from main process */
  on: (channel, callback) => {
    const validChannels = ['jarvis:notification', 'jarvis:lock-state'];
    if (validChannels.includes(channel)) {
      ipcRenderer.on(channel, (_event, ...args) => callback(...args));
    }
  },

  /** Remove listener */
  removeListener: (channel, callback) => {
    ipcRenderer.removeListener(channel, callback);
  },
});
