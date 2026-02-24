/**
 * PauseResumeControls — pause and resume running workflow executions.
 * Sprint 7 Story 2.6: Pause & Resume Execution.
 */
import React, { useCallback, useEffect, useState } from 'react';

interface PauseResumeControlsProps {
  executionId: string;
  apiBase?: string;
  /** External running status — if false, hides controls */
  isRunning?: boolean;
}

const PauseResumeControls: React.FC<PauseResumeControlsProps> = ({
  executionId,
  apiBase = 'http://localhost:9000',
  isRunning = true,
}) => {
  const [paused, setPaused] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkStatus = useCallback(async () => {
    try {
      const resp = await fetch(`${apiBase}/api/executions/${executionId}/pause-status`);
      if (resp.ok) {
        const data = await resp.json();
        setPaused(data.paused);
      }
    } catch {
      // Silently ignore — best effort check
    }
  }, [apiBase, executionId]);

  useEffect(() => {
    if (isRunning) {
      checkStatus();
      const interval = setInterval(checkStatus, 3000);
      return () => clearInterval(interval);
    }
  }, [isRunning, checkStatus]);

  const handlePause = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${apiBase}/api/executions/${executionId}/pause`, {
        method: 'POST',
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${resp.status}`);
      }
      setPaused(true);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Pause failed');
    } finally {
      setLoading(false);
    }
  };

  const handleResume = async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${apiBase}/api/executions/${executionId}/resume`, {
        method: 'POST',
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${resp.status}`);
      }
      setPaused(false);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Resume failed');
    } finally {
      setLoading(false);
    }
  };

  if (!isRunning) return null;

  return (
    <div className="pause-resume-controls" data-testid="pause-resume-controls">
      {paused ? (
        <button
          className="btn btn-primary btn-sm"
          onClick={handleResume}
          disabled={loading}
          data-testid="resume-btn"
        >
          {loading ? 'Resuming…' : '▶ Resume'}
        </button>
      ) : (
        <button
          className="btn btn-warning btn-sm"
          onClick={handlePause}
          disabled={loading}
          data-testid="pause-btn"
        >
          {loading ? 'Pausing…' : '⏸ Pause'}
        </button>
      )}

      {paused && (
        <span className="pause-status" data-testid="pause-status">
          Paused — auto-resumes in 30 min
        </span>
      )}

      {error && (
        <span className="pause-error" data-testid="pause-error" role="alert">
          {error}
        </span>
      )}
    </div>
  );
};

export default PauseResumeControls;
