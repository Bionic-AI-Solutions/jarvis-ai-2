/**
 * WorkflowExecuteDialog — accepts parameter values and starts execution.
 * Sprint 7 Story 4.2 (Execute), Story 4.3 (Parameters).
 */
import React, { useState } from 'react';
import type { WorkflowItem, WorkflowParameter, WorkflowExecuteResponse } from '../types';

interface WorkflowExecuteDialogProps {
  workflow: WorkflowItem;
  apiBase?: string;
  onClose: () => void;
  onExecuted?: (response: WorkflowExecuteResponse) => void;
}

const WorkflowExecuteDialog: React.FC<WorkflowExecuteDialogProps> = ({
  workflow,
  apiBase = 'http://localhost:9000',
  onClose,
  onExecuted,
}) => {
  // Parse parameters from the workflow
  const parameters: WorkflowParameter[] = (() => {
    try {
      const steps = JSON.parse(workflow.steps_json || '[]');
      // Collect all {placeholder} tokens from step parameters
      const found = new Set<string>();
      for (const step of steps) {
        const params = step.parameters || {};
        for (const val of Object.values(params)) {
          if (typeof val === 'string') {
            const matches = val.match(/\{(\w+)\}/g);
            if (matches) {
              for (const m of matches) {
                found.add(m.slice(1, -1));
              }
            }
          }
        }
      }
      return Array.from(found).map((name) => ({
        name,
        type: 'string',
        description: `Value for {${name}}`,
      }));
    } catch {
      return [];
    }
  })();

  const [values, setValues] = useState<Record<string, string>>(() => {
    const init: Record<string, string> = {};
    for (const p of parameters) {
      init[p.name] = p.default || '';
    }
    return init;
  });
  const [executing, setExecuting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExecute = async () => {
    setExecuting(true);
    setError(null);
    try {
      const resp = await fetch(`${apiBase}/api/workflows/${workflow.id}/execute`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          parameter_values: parameters.length > 0 ? values : undefined,
        }),
      });
      if (!resp.ok) {
        const body = await resp.json().catch(() => ({}));
        throw new Error(body.detail || `HTTP ${resp.status}`);
      }
      const data: WorkflowExecuteResponse = await resp.json();
      onExecuted?.(data);
      onClose();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  return (
    <div className="dialog-overlay" data-testid="execute-dialog">
      <div className="dialog-container">
        <div className="dialog-header">
          <h2>Execute: {workflow.name}</h2>
          <button className="dialog-close" onClick={onClose} data-testid="execute-dialog-close">
            ×
          </button>
        </div>

        {workflow.description && (
          <p className="dialog-description">{workflow.description}</p>
        )}

        {parameters.length > 0 && (
          <div className="dialog-params" data-testid="execute-params">
            <h3>Parameters</h3>
            {parameters.map((p) => (
              <div key={p.name} className="param-field">
                <label htmlFor={`param-${p.name}`}>
                  {p.name}
                  <span className="param-desc">{p.description}</span>
                </label>
                <input
                  id={`param-${p.name}`}
                  type="text"
                  value={values[p.name] || ''}
                  onChange={(e) =>
                    setValues((prev) => ({ ...prev, [p.name]: e.target.value }))
                  }
                  data-testid={`param-input-${p.name}`}
                  className="param-input"
                  placeholder={p.default || `Enter ${p.name}`}
                />
              </div>
            ))}
          </div>
        )}

        {parameters.length === 0 && (
          <p className="dialog-no-params" data-testid="no-params-msg">
            This workflow has no configurable parameters.
          </p>
        )}

        {error && (
          <div className="dialog-error" data-testid="execute-error" role="alert">
            {error}
          </div>
        )}

        <div className="dialog-actions">
          <button
            className="btn btn-ghost"
            onClick={onClose}
            disabled={executing}
            data-testid="execute-cancel-btn"
          >
            Cancel
          </button>
          <button
            className="btn btn-primary"
            onClick={handleExecute}
            disabled={executing}
            data-testid="execute-run-btn"
          >
            {executing ? 'Starting…' : 'Run Workflow'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default WorkflowExecuteDialog;
