/**
 * JARVIS AI — Execution Timeline View.
 *
 * Story 2.4: Interactive timeline showing major milestones with durations,
 * confidence scores, color coding, and expandable nested steps.
 */

import { useState } from 'react';
import { useExecutionStore } from '../stores/executionStore';
import type { ExecutionStep, StepStatus } from '../types';

const STATUS_COLORS: Record<StepStatus, string> = {
  pending: 'var(--accent-yellow)',
  running: 'var(--accent-blue)',
  completed: 'var(--accent-green)',
  failed: 'var(--accent-red)',
  skipped: 'var(--text-muted)',
};

interface TimelineNodeProps {
  step: ExecutionStep;
  isLast: boolean;
  onClick: (step: ExecutionStep) => void;
}

function TimelineNode({ step, isLast, onClick }: TimelineNodeProps) {
  const [expanded, setExpanded] = useState(false);
  const color = STATUS_COLORS[step.status];

  const duration =
    step.startedAt && step.completedAt
      ? Math.round(
          (new Date(step.completedAt).getTime() - new Date(step.startedAt).getTime()) / 1000,
        )
      : null;

  return (
    <div className="timeline-node" data-testid={`timeline-node-${step.index}`}>
      <div className="timeline-connector">
        <div className="timeline-dot" style={{ backgroundColor: color }} />
        {!isLast && <div className="timeline-line" />}
      </div>

      <div
        className={`timeline-content timeline-${step.status}`}
        onClick={() => {
          setExpanded(!expanded);
          onClick(step);
        }}
      >
        <div className="timeline-header">
          <span className="timeline-step-name">{step.name}</span>
          <span className="timeline-status" style={{ color }}>
            {step.status.toUpperCase()}
          </span>
        </div>

        <div className="timeline-meta">
          <span className="timeline-agent">{step.agent}</span>
          {duration !== null && <span className="timeline-duration">{duration}s</span>}
          {step.result &&
            typeof step.result === 'object' &&
            (step.result as Record<string, unknown>).confidence !== undefined && (
              <ConfidenceBadge
                value={(step.result as Record<string, unknown>).confidence as number}
              />
            )}
        </div>

        {expanded && (
          <div className="timeline-details">
            <div className="timeline-detail-row">
              <span className="detail-label">Action:</span>
              <span className="detail-value mono">{step.action}</span>
            </div>
            {step.startedAt && (
              <div className="timeline-detail-row">
                <span className="detail-label">Started:</span>
                <span className="detail-value">{new Date(step.startedAt).toLocaleTimeString()}</span>
              </div>
            )}
            {step.completedAt && (
              <div className="timeline-detail-row">
                <span className="detail-label">Completed:</span>
                <span className="detail-value">
                  {new Date(step.completedAt).toLocaleTimeString()}
                </span>
              </div>
            )}
            {step.error && (
              <div className="timeline-error">{step.error}</div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function ConfidenceBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const badgeClass = pct >= 90 ? 'confidence-high' : pct >= 70 ? 'confidence-med' : 'confidence-low';

  return (
    <span className={`confidence-badge ${badgeClass}`} data-testid="confidence-badge">
      {pct}%
    </span>
  );
}

export function ExecutionTimeline() {
  const activeExecution = useExecutionStore((s) => s.activeExecution());

  if (!activeExecution) {
    return (
      <div className="timeline-empty" data-testid="timeline-empty">
        <p>No execution timeline available.</p>
      </div>
    );
  }

  const handleStepClick = (_step: ExecutionStep) => {
    // Future: jump to chat section related to this step
  };

  const totalDuration =
    activeExecution.startedAt
      ? Math.round((Date.now() - new Date(activeExecution.startedAt).getTime()) / 1000)
      : 0;

  return (
    <div className="execution-timeline" data-testid="execution-timeline">
      <div className="timeline-title">
        <h3>Execution Timeline</h3>
        <span className="timeline-total-duration">{totalDuration}s total</span>
      </div>

      <div className="timeline-nodes">
        {activeExecution.steps.map((step, idx) => (
          <TimelineNode
            key={step.index}
            step={step}
            isLast={idx === activeExecution.steps.length - 1}
            onClick={handleStepClick}
          />
        ))}
      </div>
    </div>
  );
}
