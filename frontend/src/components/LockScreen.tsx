/**
 * LockScreen — Padlock overlay for system-locked state.
 *
 * Sprint 8 Story 5.2: Locked Mode + UI overlay
 */

import React, { useState, useCallback } from 'react';
import type { PassphraseStrength } from '../types';

const BACKEND_URL = 'http://localhost:9000';

interface LockScreenProps {
  /** Whether the system is currently locked */
  isLocked: boolean;
  /** Whether a passphrase has been configured */
  hasPassphrase: boolean;
  /** Callback after successful unlock */
  onUnlocked?: (token: string) => void;
  /** Callback to engage the lock */
  onLock?: () => void;
}

const LockScreen: React.FC<LockScreenProps> = ({
  isLocked,
  hasPassphrase,
  onUnlocked,
  onLock,
}) => {
  const [passphrase, setPassphrase] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [attemptsRemaining, setAttemptsRemaining] = useState<number | null>(null);
  const [lockedOut, setLockedOut] = useState(false);
  const [lockoutSeconds, setLockoutSeconds] = useState(0);

  const handleUnlock = useCallback(async () => {
    if (!passphrase.trim()) {
      setError('Please enter your passphrase.');
      return;
    }
    setLoading(true);
    setError('');
    try {
      const res = await fetch(`${BACKEND_URL}/api/auth/unlock`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ passphrase }),
      });
      const data = await res.json();
      if (data.ok && data.token) {
        setPassphrase('');
        setAttemptsRemaining(null);
        onUnlocked?.(data.token);
      } else {
        setError(data.message || 'Incorrect passphrase.');
        setAttemptsRemaining(data.attempts_remaining ?? null);
        setLockedOut(data.locked_out ?? false);
        setLockoutSeconds(data.lockout_remaining_seconds ?? 0);
      }
    } catch {
      setError('Unable to reach the backend.');
    } finally {
      setLoading(false);
    }
  }, [passphrase, onUnlocked]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (e.key === 'Enter') handleUnlock();
    },
    [handleUnlock],
  );

  if (!isLocked) return null;

  return (
    <div className="lock-screen-overlay" data-testid="lock-screen">
      <div className="lock-screen-card">
        <div className="lock-screen-icon" aria-label="Locked">🔒</div>
        <h2 className="lock-screen-title">System Locked</h2>

        {!hasPassphrase ? (
          <p className="lock-screen-hint">
            No passphrase configured. Please set one in Settings first.
          </p>
        ) : (
          <>
            <input
              type="password"
              className="lock-screen-input"
              placeholder="Enter passphrase"
              value={passphrase}
              onChange={(e) => setPassphrase(e.target.value)}
              onKeyDown={handleKeyDown}
              disabled={loading || lockedOut}
              autoFocus
              data-testid="lock-passphrase-input"
            />

            {error && <p className="lock-screen-error" data-testid="lock-error">{error}</p>}

            {attemptsRemaining !== null && attemptsRemaining > 0 && !lockedOut && (
              <p className="lock-screen-attempts">
                {attemptsRemaining} attempt{attemptsRemaining !== 1 ? 's' : ''} remaining
              </p>
            )}

            {lockedOut && (
              <p className="lock-screen-lockout" data-testid="lock-lockout">
                Locked out for {lockoutSeconds}s. Please wait.
              </p>
            )}

            <button
              className="lock-screen-btn"
              onClick={handleUnlock}
              disabled={loading || lockedOut}
              data-testid="lock-unlock-btn"
            >
              {loading ? 'Unlocking…' : 'Unlock'}
            </button>
          </>
        )}
      </div>
    </div>
  );
};

export default LockScreen;
