/**
 * VoiceButton — Mic activation button with recording state.
 * Story 1.1: Global hotkey activation (Ctrl+Shift+Alt+S via Electron).
 * Story 1.3: Pause & Resume control.
 */
import { useState, useCallback, useRef, useEffect } from 'react';
import type { TranscriptionResult } from '../types';
import { api } from '../services/api';

interface VoiceButtonProps {
  onTranscription: (result: TranscriptionResult) => void;
  onError?: (error: string) => void;
  disabled?: boolean;
  className?: string;
}

type RecordingState = 'idle' | 'recording' | 'paused' | 'processing';

const STATE_ICONS: Record<RecordingState, string> = {
  idle: '🎤',
  recording: '🔴',
  paused: '⏸',
  processing: '⏳',
};

const STATE_LABELS: Record<RecordingState, string> = {
  idle: 'Start Recording',
  recording: 'Recording... Click to stop',
  paused: 'Paused — Click to resume',
  processing: 'Processing...',
};

export default function VoiceButton({
  onTranscription,
  onError,
  disabled = false,
  className = '',
}: VoiceButtonProps) {
  const [state, setState] = useState<RecordingState>('idle');
  const [elapsed, setElapsed] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval>>();
  const streamRef = useRef<MediaStream | null>(null);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, []);

  // Listen for global hotkey from Electron
  useEffect(() => {
    const handleHotkey = () => {
      if (state === 'idle') startRecording();
      else if (state === 'recording') stopRecording();
      else if (state === 'paused') resumeRecording();
    };

    if (window.jarvis) {
      window.jarvis.on('voice-hotkey', handleHotkey);
      return () => {
        window.jarvis?.removeListener('voice-hotkey', handleHotkey);
      };
    }
  }, [state]);

  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: { sampleRate: 16000, channelCount: 1 },
      });
      streamRef.current = stream;

      const recorder = new MediaRecorder(stream, { mimeType: 'audio/webm' });
      mediaRecorderRef.current = recorder;
      chunksRef.current = [];

      recorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      recorder.onstop = async () => {
        const blob = new Blob(chunksRef.current, { type: 'audio/webm' });
        await processAudio(blob);
      };

      recorder.start(250); // Collect data every 250ms
      setState('recording');
      setElapsed(0);

      timerRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    } catch (err) {
      onError?.('Microphone access denied or unavailable');
    }
  }, [onError]);

  const stopRecording = useCallback(() => {
    if (timerRef.current) {
      clearInterval(timerRef.current);
      timerRef.current = undefined;
    }

    const recorder = mediaRecorderRef.current;
    if (recorder && recorder.state !== 'inactive') {
      setState('processing');
      recorder.stop();
    }

    streamRef.current?.getTracks().forEach((t) => t.stop());
    streamRef.current = null;
  }, []);

  const pauseRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'recording') {
      mediaRecorderRef.current.pause();
      setState('paused');
      if (timerRef.current) clearInterval(timerRef.current);
    }
  }, []);

  const resumeRecording = useCallback(() => {
    if (mediaRecorderRef.current?.state === 'paused') {
      mediaRecorderRef.current.resume();
      setState('recording');
      timerRef.current = setInterval(() => {
        setElapsed((prev) => prev + 1);
      }, 1000);
    }
  }, []);

  const processAudio = async (blob: Blob) => {
    try {
      const arrayBuffer = await blob.arrayBuffer();
      const b64 = btoa(
        new Uint8Array(arrayBuffer).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          '',
        ),
      );

      const resp = await api.request<TranscriptionResult>('/api/voice/transcribe', {
        method: 'POST',
        body: JSON.stringify({ audio_b64: b64 }),
      });

      onTranscription(resp);
    } catch (err) {
      onError?.(err instanceof Error ? err.message : 'Transcription failed');
    } finally {
      setState('idle');
      setElapsed(0);
    }
  };

  const handleClick = () => {
    if (disabled) return;
    switch (state) {
      case 'idle':
        startRecording();
        break;
      case 'recording':
        stopRecording();
        break;
      case 'paused':
        resumeRecording();
        break;
      // processing: do nothing
    }
  };

  const handlePause = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (state === 'recording') pauseRecording();
    else if (state === 'paused') resumeRecording();
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`voice-button-container ${className}`}>
      <button
        className={`voice-button voice-button--${state}`}
        onClick={handleClick}
        disabled={disabled || state === 'processing'}
        title={STATE_LABELS[state]}
        data-testid="voice-button"
      >
        <span className="voice-button__icon">{STATE_ICONS[state]}</span>
        {state !== 'idle' && (
          <span className="voice-button__timer">{formatTime(elapsed)}</span>
        )}
      </button>

      {(state === 'recording' || state === 'paused') && (
        <button
          className="voice-pause-btn"
          onClick={handlePause}
          title={state === 'recording' ? 'Pause' : 'Resume'}
          data-testid="voice-pause-btn"
        >
          {state === 'recording' ? '⏸' : '▶'}
        </button>
      )}
    </div>
  );
}
