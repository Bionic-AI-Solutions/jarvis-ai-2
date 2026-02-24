/**
 * RecoverySuggestions — displays AI-generated recovery suggestions from error snapshots.
 * Sprint 7 Story 3.8: AI Recovery Suggestions.
 */
import React, { useCallback, useState } from 'react';
import type { RecoverySuggestionResult, RecoverySuggestionItem } from '../types';

interface RecoverySuggestionsProps {
  executionId: string;
  snapshotId: string;
  apiBase?: string;
}

const RecoverySuggestions: React.FC<RecoverySuggestionsProps> = ({
  executionId,
  snapshotId,
  apiBase = 'http://localhost:9000',
}) => {
  const [result, setResult] = useState<RecoverySuggestionResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(
        `${apiBase}/api/executions/${executionId}/context-snapshots/${snapshotId}/suggestions`,
        { method: 'POST' },
      );
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: RecoverySuggestionResult = await resp.json();
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to get suggestions');
    } finally {
      setLoading(false);
    }
  }, [apiBase, executionId, snapshotId]);

  const confidenceClass = (c: number) => {
    if (c >= 0.7) return 'confidence-high';
    if (c >= 0.4) return 'confidence-medium';
    return 'confidence-low';
  };

  return (
    <div className="recovery-suggestions" data-testid="recovery-suggestions">
      {!result && !loading && (
        <button
          className="btn btn-secondary btn-sm"
          onClick={fetchSuggestions}
          data-testid="get-suggestions-btn"
        >
          Get AI Suggestions
        </button>
      )}

      {loading && (
        <div className="suggestions-loading" data-testid="suggestions-loading">
          Analyzing error context…
        </div>
      )}

      {error && (
        <div className="suggestions-error" data-testid="suggestions-error" role="alert">
          {error}
        </div>
      )}

      {result && (
        <div className="suggestions-result" data-testid="suggestions-result">
          <div className="suggestion-diagnosis">
            <strong>Diagnosis:</strong> {result.diagnosis}
          </div>

          {result.can_auto_recover && (
            <div className="suggestion-auto-recover" data-testid="auto-recover-badge">
              ✓ Can auto-recover: {result.auto_recovery_action}
            </div>
          )}

          <div className="suggestion-list">
            {result.suggestions.map((s: RecoverySuggestionItem, idx: number) => (
              <div
                key={idx}
                className={`suggestion-item ${confidenceClass(s.confidence)}`}
                data-testid={`suggestion-${idx}`}
              >
                <div className="suggestion-header">
                  <span className="suggestion-action">{s.action}</span>
                  <span className="suggestion-confidence">
                    {Math.round(s.confidence * 100)}%
                  </span>
                </div>
                <p className="suggestion-description">{s.description}</p>
              </div>
            ))}
          </div>

          <div className="suggestion-meta">
            Model: {result.model_used} · Generated:{' '}
            {new Date(result.generated_at).toLocaleTimeString()}
          </div>
        </div>
      )}
    </div>
  );
};

export default RecoverySuggestions;
