/**
 * JARVIS AI — Per-Step Confidence Score display.
 *
 * Story 2.5: Shows confidence percentages with color-coded badges
 * and hover tooltips explaining the confidence breakdown.
 */

import { useState } from 'react';

interface ConfidenceSource {
  name: string;
  value: number;
  description?: string;
}

interface StepConfidenceProps {
  /** Overall confidence score 0.0 - 1.0 */
  confidence: number;
  /** Breakdown of how confidence was calculated */
  sources?: ConfidenceSource[];
  /** Step index for identification */
  stepIndex: number;
}

export function StepConfidence({ confidence, sources = [], stepIndex }: StepConfidenceProps) {
  const [showTooltip, setShowTooltip] = useState(false);
  const pct = Math.round(confidence * 100);

  let badgeClass: string;
  let label: string;

  if (pct >= 90) {
    badgeClass = 'confidence-high';
    label = 'High';
  } else if (pct >= 70) {
    badgeClass = 'confidence-med';
    label = 'Medium';
  } else {
    badgeClass = 'confidence-low';
    label = 'Low';
  }

  return (
    <div
      className="step-confidence"
      data-testid={`step-confidence-${stepIndex}`}
      onMouseEnter={() => setShowTooltip(true)}
      onMouseLeave={() => setShowTooltip(false)}
    >
      <span className={`confidence-badge ${badgeClass}`}>
        Confidence: {pct}%
      </span>
      <span className="confidence-label">{label}</span>

      {showTooltip && sources.length > 0 && (
        <div className="confidence-tooltip" data-testid="confidence-tooltip">
          <div className="tooltip-title">Why {pct}%?</div>
          {sources.map((src, idx) => (
            <div key={idx} className="tooltip-source">
              <span className="source-name">{src.name}</span>
              <span className="source-value">{Math.round(src.value * 100)}%</span>
              {src.description && (
                <span className="source-desc">{src.description}</span>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

/**
 * Calculate a composite confidence score from multiple sources.
 */
export function calculateConfidence(sources: ConfidenceSource[]): number {
  if (sources.length === 0) return 0;
  const sum = sources.reduce((acc, s) => acc + s.value, 0);
  return sum / sources.length;
}
