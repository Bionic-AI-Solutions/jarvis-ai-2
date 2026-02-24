/**
 * PatternSuggestion — Notification cards for learned execution patterns.
 *
 * Sprint 8 Story 6.2: Suggest Workflows
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { ExecutionPattern } from '../types';

const BACKEND_URL = 'http://localhost:9000';

interface PatternSuggestionProps {
  /** Auto-refresh interval in seconds (0 = disabled) */
  refreshInterval?: number;
  /** Max suggestions to show */
  maxSuggestions?: number;
}

const PatternSuggestion: React.FC<PatternSuggestionProps> = ({
  refreshInterval = 30,
  maxSuggestions = 5,
}) => {
  const [suggestions, setSuggestions] = useState<ExecutionPattern[]>([]);
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState<string | null>(null);

  const fetchSuggestions = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `${BACKEND_URL}/api/learning/suggestions?limit=${maxSuggestions}`,
      );
      if (res.ok) {
        const data = await res.json();
        setSuggestions(data.suggestions ?? []);
      }
    } catch {
      // Silently ignore
    } finally {
      setLoading(false);
    }
  }, [maxSuggestions]);

  useEffect(() => {
    fetchSuggestions();
  }, [fetchSuggestions]);

  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchSuggestions, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, fetchSuggestions]);

  const handleAccept = useCallback(
    async (patternId: string) => {
      setActionLoading(patternId);
      try {
        await fetch(`${BACKEND_URL}/api/learning/suggestions/${patternId}/accept`, {
          method: 'POST',
        });
        setSuggestions((prev) => prev.filter((s) => s.id !== patternId));
      } catch {
        // ignore
      } finally {
        setActionLoading(null);
      }
    },
    [],
  );

  const handleDismiss = useCallback(
    async (patternId: string) => {
      setActionLoading(patternId);
      try {
        await fetch(`${BACKEND_URL}/api/learning/suggestions/${patternId}/dismiss`, {
          method: 'POST',
        });
        setSuggestions((prev) => prev.filter((s) => s.id !== patternId));
      } catch {
        // ignore
      } finally {
        setActionLoading(null);
      }
    },
    [],
  );

  if (loading && suggestions.length === 0) {
    return null; // Don't show empty loader
  }

  if (suggestions.length === 0) return null;

  return (
    <div className="pattern-suggestions" data-testid="pattern-suggestions">
      <h4 className="pattern-suggestions-title">Suggested Workflows</h4>
      {suggestions.map((pattern) => (
        <div
          key={pattern.id}
          className="pattern-suggestion-card"
          data-testid="suggestion-card"
        >
          <div className="pattern-suggestion-header">
            <span className="pattern-intent">{pattern.intent}</span>
            <span
              className="pattern-confidence"
              data-testid="suggestion-confidence"
              title={`Confidence: ${Math.round(pattern.confidence * 100)}%`}
            >
              {Math.round(pattern.confidence * 100)}%
            </span>
          </div>
          <div className="pattern-suggestion-meta">
            <span>Seen {pattern.frequency}× • {Math.round(pattern.success_rate * 100)}% success</span>
          </div>
          <div className="pattern-suggestion-steps">
            {pattern.steps.map((step, i) => (
              <span key={i} className="pattern-step-chip">
                {step.agent}: {step.action}
              </span>
            ))}
          </div>
          <div className="pattern-suggestion-actions">
            <button
              className="pattern-accept-btn"
              onClick={() => handleAccept(pattern.id)}
              disabled={actionLoading === pattern.id}
              data-testid="accept-suggestion-btn"
            >
              Accept
            </button>
            <button
              className="pattern-dismiss-btn"
              onClick={() => handleDismiss(pattern.id)}
              disabled={actionLoading === pattern.id}
              data-testid="dismiss-suggestion-btn"
            >
              Dismiss
            </button>
          </div>
        </div>
      ))}
    </div>
  );
};

export default PatternSuggestion;
