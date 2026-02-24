/**
 * JARVIS AI — Real-Time Step Progress Display.
 *
 * Story 2.1: Shows live workflow execution progress with step-by-step updates.
 */

import { useExecutionStore } from '../stores/executionStore';
import type { ExecutionStep, StepStatus } from '../types';

const STATUS_ICONS: Record<StepStatus, string> = {
  pending: '⏳',
  running: '🔄',
  completed: '✅',
  failed: '❌',
  skipped: '⏭️',
};

const STATUS_LABELS: Record<StepStatus, string> = {
  pending: 'Pending',
  running: 'Running',
  completed: 'Completed',
  failed: 'Failed',
  skipped: 'Skipped',
};

function StepItem({ step }: { step: ExecutionStep }) {
  return (
    <div className={`step-item step-${step.status}`} data-testid={`step-${step.index}`}>
      <div className="step-indicator">
        <span className="step-icon">{STATUS_ICONS[step.status]}</span>
        <span className="step-number">{step.index + 1}</span>
      </div>
      <div className="step-info">
        <div className="step-name">{step.name}</div>
        <div className="step-meta">
          <span className="step-agent">{step.agent}</span>
          <span className="step-status-label">{STATUS_LABELS[step.status]}</span>
        </div>
        {step.error && <div className="step-error">{step.error}</div>}
      </div>
    </div>
  );
}

export function StepProgress() {
  const activeExecution = useExecutionStore((s) => s.activeExecution());
  const executions = useExecutionStore((s) => s.executions);

  if (!activeExecution) {
    return (
      <div className="step-progress empty" data-testid="step-progress-empty">
        <p>No active execution. Start a workflow to see progress here.</p>
      </div>
    );
  }

  const completedCount = activeExecution.steps.filter(
    (s) => s.status === 'completed' || s.status === 'skipped',
  ).length;
  const progress = activeExecution.totalSteps > 0
    ? Math.round((completedCount / activeExecution.totalSteps) * 100)
    : 0;

  return (
    <div className="step-progress" data-testid="step-progress">
      <div className="progress-header">
        <h3>Execution Progress</h3>
        <span className={`execution-status status-${activeExecution.status}`}>
          {activeExecution.status.toUpperCase()}
        </span>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar"
          style={{ width: `${progress}%` }}
          data-testid="progress-bar"
        />
        <span className="progress-text">
          {completedCount} / {activeExecution.totalSteps} steps ({progress}%)
        </span>
      </div>

      <div className="steps-list" data-testid="steps-list">
        {activeExecution.steps.map((step) => (
          <StepItem key={step.index} step={step} />
        ))}
      </div>

      {executions.size > 1 && (
        <div className="execution-count">
          Tracking {executions.size} execution(s)
        </div>
      )}
    </div>
  );
}
