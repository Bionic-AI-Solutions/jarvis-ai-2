/**
 * JARVIS AI — Sprint 6 Frontend Tests.
 *
 * Tests for: VoiceButton, VoiceIndicator, VoiceSettings, RecoveryDialog
 * Stories 1.1–1.5 (Voice), 3.1–3.6 (Recovery)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import VoiceButton from '../components/VoiceButton';
import VoiceIndicator from '../components/VoiceIndicator';
import VoiceSettings from '../components/VoiceSettings';
import RecoveryDialog from '../components/RecoveryDialog';
import type { TranscriptionResult, VoiceConfig, RecoveryNotification } from '../types';

// ── Test Fixtures ──────────────────────────────────

const mockTranscription: TranscriptionResult = {
  text: 'Open the browser and go to google.com',
  confidence: 0.95,
  language: 'en',
  duration_ms: 2340,
  auto_accepted: false,
  needs_re_speak: false,
  source: 'voice',
};

const mockHighConfidence: TranscriptionResult = {
  ...mockTranscription,
  confidence: 0.98,
  auto_accepted: true,
};

const mockLowConfidence: TranscriptionResult = {
  ...mockTranscription,
  confidence: 0.55,
  needs_re_speak: true,
  auto_accepted: false,
};

const mockMediumConfidence: TranscriptionResult = {
  ...mockTranscription,
  confidence: 0.82,
  needs_re_speak: false,
  auto_accepted: false,
};

const mockVoiceConfig: VoiceConfig = {
  confidence_threshold: 0.9,
  auto_accept_threshold: 0.9,
  re_speak_threshold: 0.8,
  silence_db_threshold: 5.0,
  silence_duration: 1.5,
  max_recording_seconds: 30,
  language: 'auto',
  device_id: null,
};

const mockL5Notification: RecoveryNotification = {
  type: 'recovery',
  level: 5,
  message: 'Step failed after 4 recovery attempts. What would you like to do?',
  execution_id: 'exec-r1',
  step_index: 2,
  options: ['retry', 'skip', 'cancel'],
};

const mockL6Notification: RecoveryNotification = {
  type: 'recovery',
  level: 6,
  message: 'This step has been marked as impossible to complete automatically.',
  execution_id: 'exec-r2',
  step_index: 5,
};


// ── VoiceButton Tests ──────────────────────────────

describe('VoiceButton', () => {
  const mockOnTranscription = vi.fn();
  const mockOnError = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders in idle state by default', () => {
    render(
      <VoiceButton onTranscription={mockOnTranscription} />,
    );
    const btn = screen.getByTestId('voice-button');
    expect(btn).toBeInTheDocument();
    expect(btn.textContent).toContain('🎤');
  });

  it('has correct title in idle state', () => {
    render(
      <VoiceButton onTranscription={mockOnTranscription} />,
    );
    const btn = screen.getByTestId('voice-button');
    expect(btn.getAttribute('title')).toBe('Start Recording');
  });

  it('is disabled when disabled prop is true', () => {
    render(
      <VoiceButton onTranscription={mockOnTranscription} disabled />,
    );
    const btn = screen.getByTestId('voice-button');
    expect(btn).toBeDisabled();
  });

  it('applies custom className', () => {
    const { container } = render(
      <VoiceButton onTranscription={mockOnTranscription} className="custom-voice" />,
    );
    expect(container.querySelector('.custom-voice')).toBeInTheDocument();
  });

  it('does not show timer in idle state', () => {
    render(
      <VoiceButton onTranscription={mockOnTranscription} />,
    );
    const btn = screen.getByTestId('voice-button');
    expect(btn.querySelector('.voice-button__timer')).toBeNull();
  });

  it('does not show pause button in idle state', () => {
    render(
      <VoiceButton onTranscription={mockOnTranscription} />,
    );
    expect(screen.queryByTestId('voice-pause-btn')).not.toBeInTheDocument();
  });
});

// ── VoiceIndicator Tests ──────────────────────────────

describe('VoiceIndicator', () => {
  it('returns null when no result', () => {
    const { container } = render(
      <VoiceIndicator result={null} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders transcription text', () => {
    render(<VoiceIndicator result={mockTranscription} />);
    expect(screen.getByText(mockTranscription.text)).toBeInTheDocument();
  });

  it('shows confidence percentage', () => {
    render(<VoiceIndicator result={mockTranscription} />);
    expect(screen.getByText(/95%/)).toBeInTheDocument();
  });

  it('displays "High" label for 95% confidence', () => {
    render(<VoiceIndicator result={mockTranscription} />);
    expect(screen.getByText(/High/)).toBeInTheDocument();
  });

  it('displays "Medium" label for medium confidence', () => {
    render(<VoiceIndicator result={mockMediumConfidence} />);
    expect(screen.getByText(/Medium/)).toBeInTheDocument();
  });

  it('displays "Low" label for low confidence', () => {
    render(<VoiceIndicator result={mockLowConfidence} />);
    const score = screen.getByTestId('confidence-bar');
    expect(score.style.width).toBe('55%');
    // Score text contains "Low" label in the score span
    expect(screen.getByText(/55% — Low/)).toBeInTheDocument();
  });

  it('shows confidence bar with correct width', () => {
    render(<VoiceIndicator result={mockTranscription} />);
    const bar = screen.getByTestId('confidence-bar');
    expect(bar.style.width).toBe('95%');
  });

  it('shows green bar for high confidence', () => {
    render(<VoiceIndicator result={mockHighConfidence} />);
    const bar = screen.getByTestId('confidence-bar');
    expect(bar.style.backgroundColor).toContain('4caf50');
  });

  it('shows auto-accepted badge', () => {
    render(<VoiceIndicator result={mockHighConfidence} />);
    expect(screen.getByText(/Auto-accepted/)).toBeInTheDocument();
  });

  it('shows re-speak warning for low confidence', () => {
    render(<VoiceIndicator result={mockLowConfidence} onReSpeak={vi.fn()} />);
    expect(screen.getByText(/Low confidence/)).toBeInTheDocument();
  });

  it('shows re-speak button with handler', () => {
    const onReSpeak = vi.fn();
    render(<VoiceIndicator result={mockLowConfidence} onReSpeak={onReSpeak} />);
    const btn = screen.getByTestId('re-speak-btn');
    fireEvent.click(btn);
    expect(onReSpeak).toHaveBeenCalledOnce();
  });

  it('shows accept button for medium confidence', () => {
    const onAccept = vi.fn();
    render(<VoiceIndicator result={mockMediumConfidence} onAccept={onAccept} />);
    const btn = screen.getByTestId('accept-btn');
    fireEvent.click(btn);
    expect(onAccept).toHaveBeenCalledWith(mockMediumConfidence.text);
  });

  it('shows language and duration metadata', () => {
    render(<VoiceIndicator result={mockTranscription} />);
    expect(screen.getByText(/Language: en/)).toBeInTheDocument();
    expect(screen.getByText(/Duration: 2340ms/)).toBeInTheDocument();
  });

  it('shows "No speech detected" when text is empty', () => {
    const emptyResult = { ...mockTranscription, text: '' };
    render(<VoiceIndicator result={emptyResult} />);
    expect(screen.getByText(/No speech detected/)).toBeInTheDocument();
  });
});

// ── VoiceSettings Tests ──────────────────────────────

describe('VoiceSettings', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    // Mock the api module globally
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/voice/config')) {
        return new Response(JSON.stringify(mockVoiceConfig), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(null, { status: 404 });
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('shows loading state initially', () => {
    render(<VoiceSettings />);
    expect(screen.getByText(/Loading voice settings/)).toBeInTheDocument();
  });

  it('renders settings panel after loading', async () => {
    render(<VoiceSettings />);
    await waitFor(() => {
      expect(screen.getByTestId('voice-settings')).toBeInTheDocument();
    });
  });

  it('displays confidence threshold value', async () => {
    render(<VoiceSettings />);
    await waitFor(() => {
      const slider = screen.getByTestId('confidence-slider') as HTMLInputElement;
      expect(slider.value).toBe('90');
    });
  });

  it('renders all sliders', async () => {
    render(<VoiceSettings />);
    await waitFor(() => {
      expect(screen.getByTestId('confidence-slider')).toBeInTheDocument();
      expect(screen.getByTestId('auto-accept-slider')).toBeInTheDocument();
      expect(screen.getByTestId('re-speak-slider')).toBeInTheDocument();
      expect(screen.getByTestId('silence-db-slider')).toBeInTheDocument();
      expect(screen.getByTestId('silence-duration-slider')).toBeInTheDocument();
      expect(screen.getByTestId('max-recording-slider')).toBeInTheDocument();
    });
  });

  it('has a save button', async () => {
    render(<VoiceSettings />);
    await waitFor(() => {
      expect(screen.getByTestId('voice-save-btn')).toBeInTheDocument();
    });
  });
});

// ── RecoveryDialog Tests ──────────────────────────────

describe('RecoveryDialog', () => {
  const mockOnAction = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('returns null when no notification', () => {
    const { container } = render(
      <RecoveryDialog notification={null} onAction={mockOnAction} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('renders L5 dialog with correct level label', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    expect(screen.getByTestId('recovery-dialog')).toBeInTheDocument();
    expect(screen.getByText('User Decision (L5)')).toBeInTheDocument();
  });

  it('shows step number in L5 dialog', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    expect(screen.getByText('Step 3')).toBeInTheDocument();
  });

  it('shows message text', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    expect(screen.getByText(mockL5Notification.message)).toBeInTheDocument();
  });

  it('renders L5 retry/skip/cancel buttons', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    expect(screen.getByTestId('recovery-retry')).toBeInTheDocument();
    expect(screen.getByTestId('recovery-skip')).toBeInTheDocument();
    expect(screen.getByTestId('recovery-cancel')).toBeInTheDocument();
  });

  it('fires onAction with correct args when retry clicked', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-retry'));
    expect(mockOnAction).toHaveBeenCalledWith('exec-r1', 2, 'retry');
  });

  it('fires onAction with skip', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-skip'));
    expect(mockOnAction).toHaveBeenCalledWith('exec-r1', 2, 'skip');
  });

  it('disables buttons after selection', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-retry'));
    expect(screen.getByTestId('recovery-skip')).toBeDisabled();
    expect(screen.getByTestId('recovery-cancel')).toBeDisabled();
  });

  it('shows processing text after selection', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-retry'));
    expect(screen.getByText(/Processing: retry/)).toBeInTheDocument();
  });

  it('renders L6 dialog with impossible label', () => {
    render(
      <RecoveryDialog notification={mockL6Notification} onAction={mockOnAction} />,
    );
    expect(screen.getByText('Impossible (L6)')).toBeInTheDocument();
  });

  it('renders L6 special buttons', () => {
    render(
      <RecoveryDialog notification={mockL6Notification} onAction={mockOnAction} />,
    );
    expect(screen.getByTestId('recovery-try-manually')).toBeInTheDocument();
    expect(screen.getByTestId('recovery-abort')).toBeInTheDocument();
    expect(screen.getByTestId('recovery-save')).toBeInTheDocument();
  });

  it('fires onAction for L6 try-manually', () => {
    render(
      <RecoveryDialog notification={mockL6Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-try-manually'));
    expect(mockOnAction).toHaveBeenCalledWith('exec-r2', 5, 'try_manually');
  });

  it('fires onAction for L6 abort', () => {
    render(
      <RecoveryDialog notification={mockL6Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-abort'));
    expect(mockOnAction).toHaveBeenCalledWith('exec-r2', 5, 'abort');
  });

  it('fires onAction for L6 save-for-later', () => {
    render(
      <RecoveryDialog notification={mockL6Notification} onAction={mockOnAction} />,
    );
    fireEvent.click(screen.getByTestId('recovery-save'));
    expect(mockOnAction).toHaveBeenCalledWith('exec-r2', 5, 'save_for_later');
  });

  it('applies custom className', () => {
    render(
      <RecoveryDialog notification={mockL5Notification} onAction={mockOnAction} className="custom-recovery" />,
    );
    const dialog = screen.getByTestId('recovery-dialog');
    expect(dialog.className).toContain('custom-recovery');
  });
});
