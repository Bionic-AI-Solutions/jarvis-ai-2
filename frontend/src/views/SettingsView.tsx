/**
 * JARVIS AI — Settings view.
 */

import { useEffect, useState } from 'react';
import { useAuthStore } from '../stores/authStore';

export function SettingsView() {
  const { hasPassphrase, isAuthenticated, setPassphrase, checkStatus } = useAuthStore();
  const [newPassphrase, setNewPassphrase] = useState('');
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    checkStatus();
  }, [checkStatus]);

  const handleSetPassphrase = async () => {
    if (newPassphrase.length < 8) return;
    await setPassphrase(newPassphrase);
    setNewPassphrase('');
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="settings-view" data-testid="settings-view">
      <div className="view-header">
        <h2>Settings</h2>
      </div>

      <div className="settings-section">
        <h3>Security</h3>
        <div className="setting-item">
          <label>Passphrase</label>
          <div className="setting-value">
            {hasPassphrase ? (
              <span className="badge badge-success">Set ✓</span>
            ) : (
              <span className="badge badge-warning">Not Set</span>
            )}
          </div>
        </div>
        <div className="setting-item">
          <label>{hasPassphrase ? 'Change Passphrase' : 'Set Passphrase'}</label>
          <div className="setting-input-group">
            <input
              type="password"
              value={newPassphrase}
              onChange={(e) => setNewPassphrase(e.target.value)}
              placeholder="Min 8 characters"
              className="input"
              data-testid="passphrase-input"
            />
            <button
              className="btn btn-primary"
              onClick={handleSetPassphrase}
              disabled={newPassphrase.length < 8}
            >
              Save
            </button>
          </div>
          {saved && <span className="success-msg">Passphrase saved!</span>}
        </div>
        <div className="setting-item">
          <label>Status</label>
          <div className="setting-value">
            {isAuthenticated ? (
              <span className="badge badge-success">Authenticated</span>
            ) : (
              <span className="badge badge-warning">Locked</span>
            )}
          </div>
        </div>
      </div>

      <div className="settings-section">
        <h3>Ollama Configuration</h3>
        <div className="setting-item">
          <label>Model Path</label>
          <div className="setting-value mono">F:/models</div>
        </div>
        <div className="setting-item">
          <label>Default Model</label>
          <div className="setting-value mono">qwen2.5:3b</div>
        </div>
        <div className="setting-item">
          <label>Endpoint</label>
          <div className="setting-value mono">http://localhost:11434</div>
        </div>
      </div>
    </div>
  );
}
