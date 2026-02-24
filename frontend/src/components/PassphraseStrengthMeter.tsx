/**
 * PassphraseStrengthMeter — Visual feedback on passphrase strength.
 *
 * Sprint 8 Story 5.1: Passphrase strength indicator
 */

import React, { useState, useEffect } from 'react';
import type { PassphraseStrength } from '../types';

const BACKEND_URL = 'http://localhost:9000';

interface PassphraseStrengthMeterProps {
  /** Current passphrase value to check */
  passphrase: string;
  /** Debounce interval in ms */
  debounceMs?: number;
}

const STRENGTH_LABELS = ['Weak', 'Fair', 'Good', 'Strong'];
const STRENGTH_COLORS = ['#e53935', '#fb8c00', '#43a047', '#1b5e20'];

const PassphraseStrengthMeter: React.FC<PassphraseStrengthMeterProps> = ({
  passphrase,
  debounceMs = 300,
}) => {
  const [strength, setStrength] = useState<PassphraseStrength | null>(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!passphrase || passphrase.length < 1) {
      setStrength(null);
      return;
    }

    const timeout = setTimeout(async () => {
      setLoading(true);
      try {
        const res = await fetch(`${BACKEND_URL}/api/auth/passphrase/strength`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ passphrase }),
        });
        if (res.ok) {
          const data: PassphraseStrength = await res.json();
          setStrength(data);
        }
      } catch {
        // Silently ignore fetch errors
      } finally {
        setLoading(false);
      }
    }, debounceMs);

    return () => clearTimeout(timeout);
  }, [passphrase, debounceMs]);

  if (!passphrase) return null;

  const score = strength?.score ?? 0;
  const barWidth = `${((score + (strength ? 0 : 0)) / 4) * 100}%`;
  const color = STRENGTH_COLORS[Math.min(score, 3)];
  const label = strength ? STRENGTH_LABELS[Math.min(score, 3)] : '';

  return (
    <div className="passphrase-strength" data-testid="passphrase-strength">
      <div className="passphrase-strength-bar-bg">
        <div
          className="passphrase-strength-bar-fill"
          style={{ width: barWidth, backgroundColor: color }}
          data-testid="strength-bar"
        />
      </div>
      <div className="passphrase-strength-info">
        {loading ? (
          <span className="passphrase-strength-loading">Checking…</span>
        ) : (
          <>
            {label && (
              <span
                className="passphrase-strength-label"
                style={{ color }}
                data-testid="strength-label"
              >
                {label}
              </span>
            )}
            {strength?.feedback && strength.feedback.length > 0 && (
              <ul className="passphrase-strength-feedback" data-testid="strength-feedback">
                {strength.feedback.map((tip, i) => (
                  <li key={i}>{tip}</li>
                ))}
              </ul>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default PassphraseStrengthMeter;
