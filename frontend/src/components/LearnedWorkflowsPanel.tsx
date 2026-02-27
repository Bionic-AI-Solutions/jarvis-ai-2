/**
 * JARVIS AI — Learned Workflows Panel.
 *
 * Displays workflow patterns that JARVIS has learned from past executions.
 * Users can review, accept suggestions, and trigger re-execution of
 * previously learned workflows.
 */

import { useState, useEffect, useCallback } from 'react';
import { api, type PatternItem, type SuggestionItem } from '../services/api';

type ViewMode = 'patterns' | 'suggestions';

export function LearnedWorkflowsPanel() {
  const [mode, setMode] = useState<ViewMode>('suggestions');
  const [patterns, setPatterns] = useState<PatternItem[]>([]);
  const [suggestions, setSuggestions] = useState<SuggestionItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      if (mode === 'patterns') {
        const resp = await api.listPatterns(0.5);
        setPatterns(resp.patterns ?? []);
      } else {
        const resp = await api.listSuggestions();
        setSuggestions(resp.suggestions ?? []);
      }
    } catch (err) {
      setError((err as Error).message);
    } finally {
      setLoading(false);
    }
  }, [mode]);

  useEffect(() => {
    load();
  }, [load]);

  const handleAccept = async (patternId: string) => {
    try {
      await api.acceptSuggestion(patternId);
      // Refresh after accepting
      await load();
    } catch (err) {
      setError((err as Error).message);
    }
  };

  return (
    <div className="learned-workflows-panel" data-testid="learned-workflows">
      <div className="lwp-header">
        <h3>Learned Workflows</h3>
        <div className="lwp-tabs">
          <button
            className={`lwp-tab ${mode === 'suggestions' ? 'active' : ''}`}
            onClick={() => setMode('suggestions')}
          >
            Suggestions
          </button>
          <button
            className={`lwp-tab ${mode === 'patterns' ? 'active' : ''}`}
            onClick={() => setMode('patterns')}
          >
            All Patterns
          </button>
        </div>
      </div>

      {error && <div className="lwp-error">{error}</div>}

      {loading ? (
        <div className="lwp-loading">Loading...</div>
      ) : mode === 'suggestions' ? (
        <SuggestionList items={suggestions} onAccept={handleAccept} />
      ) : (
        <PatternList items={patterns} />
      )}
    </div>
  );
}

function SuggestionList({
  items,
  onAccept,
}: {
  items: SuggestionItem[];
  onAccept: (id: string) => void;
}) {
  if (items.length === 0) {
    return <div className="lwp-empty">No suggestions yet. JARVIS learns from your workflows.</div>;
  }

  return (
    <ul className="lwp-list">
      {items.map((s) => (
        <li key={s.id} className="lwp-item">
          <div className="lwp-item-header">
            <span className="lwp-intent">{s.intent}</span>
            <span className="lwp-confidence">{Math.round(s.confidence * 100)}%</span>
          </div>
          <div className="lwp-steps">
            {s.steps.map((step, i) => (
              <span key={i} className="lwp-step-chip">
                {step.action}
              </span>
            ))}
          </div>
          <div className="lwp-item-footer">
            <span className="lwp-meta">
              {s.frequency}x used · {Math.round(s.success_rate * 100)}% success
            </span>
            <button className="btn btn-sm btn-primary" onClick={() => onAccept(s.id)}>
              Accept
            </button>
          </div>
        </li>
      ))}
    </ul>
  );
}

function PatternList({ items }: { items: PatternItem[] }) {
  if (items.length === 0) {
    return <div className="lwp-empty">No learned patterns yet.</div>;
  }

  return (
    <ul className="lwp-list">
      {items.map((p) => (
        <li key={p.id} className={`lwp-item ${p.accepted ? 'lwp-accepted' : ''}`}>
          <div className="lwp-item-header">
            <span className="lwp-intent">{p.intent}</span>
            <span className="lwp-confidence">{Math.round(p.confidence * 100)}%</span>
          </div>
          <div className="lwp-steps">
            {p.steps.map((step, i) => (
              <span key={i} className="lwp-step-chip">
                {step.action}
              </span>
            ))}
          </div>
          <div className="lwp-item-footer">
            <span className="lwp-meta">
              {p.frequency}x · {Math.round(p.success_rate * 100)}% success
              {p.accepted && ' · Accepted'}
            </span>
          </div>
        </li>
      ))}
    </ul>
  );
}
