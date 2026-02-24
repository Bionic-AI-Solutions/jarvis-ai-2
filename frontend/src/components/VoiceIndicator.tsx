/**
 * VoiceIndicator — Shows transcription results with confidence display.
 * Story 1.2: Confidence score display.
 * Story 1.5: Threshold indicators (auto-accept, re-speak).
 */
import { useMemo } from 'react';
import type { TranscriptionResult } from '../types';

interface VoiceIndicatorProps {
  result: TranscriptionResult | null;
  threshold?: number;
  onAccept?: (text: string) => void;
  onReSpeak?: () => void;
  className?: string;
}

function getConfidenceColor(confidence: number): string {
  if (confidence >= 0.9) return 'var(--color-success, #4caf50)';
  if (confidence >= 0.7) return 'var(--color-warning, #ff9800)';
  return 'var(--color-error, #f44336)';
}

function getConfidenceLabel(confidence: number): string {
  if (confidence >= 0.9) return 'High';
  if (confidence >= 0.7) return 'Medium';
  return 'Low';
}

export default function VoiceIndicator({
  result,
  threshold = 0.9,
  onAccept,
  onReSpeak,
  className = '',
}: VoiceIndicatorProps) {
  const confidencePct = useMemo(
    () => (result ? Math.round(result.confidence * 100) : 0),
    [result],
  );

  if (!result) return null;

  return (
    <div className={`voice-indicator ${className}`} data-testid="voice-indicator">
      {/* Transcribed text */}
      <div className="voice-indicator__text">
        <span className="voice-indicator__label">Transcribed:</span>
        <p className="voice-indicator__content">
          {result.text || <em>No speech detected</em>}
        </p>
      </div>

      {/* Confidence bar */}
      <div className="voice-indicator__confidence">
        <div className="voice-indicator__bar-container">
          <div
            className="voice-indicator__bar"
            style={{
              width: `${confidencePct}%`,
              backgroundColor: getConfidenceColor(result.confidence),
            }}
            data-testid="confidence-bar"
          />
        </div>
        <span
          className="voice-indicator__score"
          style={{ color: getConfidenceColor(result.confidence) }}
        >
          {confidencePct}% — {getConfidenceLabel(result.confidence)}
        </span>
      </div>

      {/* Language */}
      <div className="voice-indicator__meta">
        <span>Language: {result.language}</span>
        <span>Duration: {Math.round(result.duration_ms)}ms</span>
      </div>

      {/* Action buttons */}
      <div className="voice-indicator__actions">
        {result.auto_accepted && (
          <span className="voice-indicator__badge voice-indicator__badge--accepted">
            ✓ Auto-accepted
          </span>
        )}

        {result.needs_re_speak && (
          <div className="voice-indicator__re-speak">
            <span className="voice-indicator__badge voice-indicator__badge--low">
              ⚠ Low confidence
            </span>
            {onReSpeak && (
              <button
                className="voice-indicator__btn"
                onClick={onReSpeak}
                data-testid="re-speak-btn"
              >
                🎤 Re-speak
              </button>
            )}
          </div>
        )}

        {!result.auto_accepted && !result.needs_re_speak && result.text && onAccept && (
          <button
            className="voice-indicator__btn voice-indicator__btn--accept"
            onClick={() => onAccept(result.text)}
            data-testid="accept-btn"
          >
            ✓ Accept
          </button>
        )}
      </div>
    </div>
  );
}
