/**
 * RecoveryDialog — L5 User Confirmation dialog during recovery.
 * Story 3.5: Show recovery dialog with Retry/Skip/Cancel options.
 * Story 3.6: Mark impossible state display.
 */
import { useState } from 'react';
import type { RecoveryNotification } from '../types';

interface RecoveryDialogProps {
  notification: RecoveryNotification | null;
  onAction: (executionId: string, stepIndex: number, action: string) => void;
  className?: string;
}

const LEVEL_LABELS: Record<number, string> = {
  1: 'Retry (L1)',
  2: 'Alternative Method (L2)',
  3: 'Re-Verification (L3)',
  4: 'AI Replan (L4)',
  5: 'User Decision (L5)',
  6: 'Impossible (L6)',
};

const LEVEL_COLORS: Record<number, string> = {
  1: '#4caf50',
  2: '#2196f3',
  3: '#ff9800',
  4: '#9c27b0',
  5: '#f44336',
  6: '#333',
};

export default function RecoveryDialog({
  notification,
  onAction,
  className = '',
}: RecoveryDialogProps) {
  const [selectedAction, setSelectedAction] = useState<string | null>(null);

  if (!notification) return null;

  const handleAction = (action: string) => {
    setSelectedAction(action);
    onAction(notification.execution_id, notification.step_index, action);
  };

  const options = notification.options || ['retry', 'skip', 'cancel'];
  const isL6 = notification.level === 6;

  return (
    <div className={`recovery-dialog-overlay ${className}`} data-testid="recovery-dialog">
      <div className="recovery-dialog">
        <div
          className="recovery-dialog__header"
          style={{ borderLeftColor: LEVEL_COLORS[notification.level] || '#666' }}
        >
          <span className="recovery-dialog__level">
            {LEVEL_LABELS[notification.level] || `Level ${notification.level}`}
          </span>
          <span className="recovery-dialog__step">
            Step {notification.step_index + 1}
          </span>
        </div>

        <p className="recovery-dialog__message">{notification.message}</p>

        <div className="recovery-dialog__actions">
          {isL6 ? (
            // L6 Impossible: special options
            <>
              <button
                className="recovery-dialog__btn recovery-dialog__btn--retry"
                onClick={() => handleAction('try_manually')}
                disabled={selectedAction !== null}
                data-testid="recovery-try-manually"
              >
                Try Manually
              </button>
              <button
                className="recovery-dialog__btn recovery-dialog__btn--cancel"
                onClick={() => handleAction('abort')}
                disabled={selectedAction !== null}
                data-testid="recovery-abort"
              >
                Abort Workflow
              </button>
              <button
                className="recovery-dialog__btn recovery-dialog__btn--skip"
                onClick={() => handleAction('save_for_later')}
                disabled={selectedAction !== null}
                data-testid="recovery-save"
              >
                Save for Later
              </button>
            </>
          ) : (
            // L5 and general: retry/skip/cancel
            options.map((opt) => (
              <button
                key={opt}
                className={`recovery-dialog__btn recovery-dialog__btn--${opt}`}
                onClick={() => handleAction(opt)}
                disabled={selectedAction !== null}
                data-testid={`recovery-${opt}`}
              >
                {opt.charAt(0).toUpperCase() + opt.slice(1)}
              </button>
            ))
          )}
        </div>

        {selectedAction && (
          <p className="recovery-dialog__processing">
            Processing: {selectedAction}...
          </p>
        )}
      </div>
    </div>
  );
}
