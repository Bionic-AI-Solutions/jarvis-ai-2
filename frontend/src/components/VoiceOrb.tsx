/**
 * VoiceOrb — JARVIS-style glowing orb for voice mode.
 * 
 * States:
 *  - idle: Subtle blue glow, pulsing gently
 *  - listening: Brighter glow, recording indicator
 *  - processing: Spinning animation while transcribing
 *  - speaking: Wave animation while TTS audio plays, bright glow
 * 
 * Click to toggle voice recording on/off.
 * When JARVIS responds in voice mode, it speaks through TTS and the orb glows.
 */
import { useState, useCallback, useRef, useEffect, forwardRef, useImperativeHandle } from 'react';
import type { TranscriptionResult } from '../types';
import { api } from '../services/api';

export type OrbState = 'idle' | 'listening' | 'processing' | 'speaking';

export interface VoiceOrbHandle {
  speak: (text: string) => Promise<void>;
}

interface VoiceOrbProps {
  onTranscription: (result: TranscriptionResult) => void;
  onError?: (error: string) => void;
  onStateChange?: (state: OrbState) => void;
  disabled?: boolean;
}

const VoiceOrbComponent = forwardRef<VoiceOrbHandle, VoiceOrbProps>((
  { onTranscription, onError, onStateChange, disabled = false },
  ref,
) => {
  const [state, setState] = useState<OrbState>('idle');
  const [elapsed, setElapsed] = useState(0);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);
  const timerRef = useRef<ReturnType<typeof setInterval>>();
  const streamRef = useRef<MediaStream | null>(null);
  const audioRef = useRef<HTMLAudioElement | null>(null);

  // Notify parent of state changes
  useEffect(() => {
    onStateChange?.(state);
  }, [state, onStateChange]);

  // Clean up on unmount
  useEffect(() => {
    return () => {
      stopRecording();
      if (timerRef.current) clearInterval(timerRef.current);
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, []);

  // Listen for global hotkey from Electron
  useEffect(() => {
    const handleHotkey = () => {
      if (state === 'idle' || state === 'speaking') startRecording();
      else if (state === 'listening') stopRecording();
    };

    if (window.jarvis) {
      window.jarvis.on('voice-hotkey', handleHotkey);
      return () => {
        window.jarvis?.removeListener('voice-hotkey', handleHotkey);
      };
    }
  }, [state]);

  const startRecording = useCallback(async () => {
    // Stop any playing audio
    if (audioRef.current) {
      audioRef.current.pause();
      audioRef.current = null;
    }

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

      recorder.start(250);
      setState('listening');
      setElapsed(0);
      timerRef.current = setInterval(() => setElapsed((prev) => prev + 1), 1000);
    } catch {
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

  const processAudio = async (blob: Blob) => {
    try {
      const arrayBuffer = await blob.arrayBuffer();
      const b64 = btoa(
        new Uint8Array(arrayBuffer).reduce(
          (data, byte) => data + String.fromCharCode(byte),
          '',
        ),
      );

      const resp = await api.transcribeAudio(b64);
      onTranscription({
        text: resp.text,
        confidence: 0.95,
        language: 'en',
        duration_ms: elapsed,
        auto_accepted: true, // Voice mode auto-sends
        needs_re_speak: false,
        source: 'voice',
      } as TranscriptionResult);
    } catch (err) {
      onError?.(err instanceof Error ? err.message : 'Transcription failed');
    } finally {
      setState('idle');
      setElapsed(0);
    }
  };

  /** Play TTS audio — called externally when assistant responds */
  const speak = useCallback(async (text: string) => {
    try {
      setState('speaking');
      const audioData = await api.synthesizeSpeech(text);
      const blob = new Blob([audioData], { type: 'audio/mpeg' });
      const url = URL.createObjectURL(blob);

      const audio = new Audio(url);
      audioRef.current = audio;

      audio.onended = () => {
        setState('idle');
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };

      audio.onerror = () => {
        setState('idle');
        URL.revokeObjectURL(url);
        audioRef.current = null;
      };

      await audio.play();
    } catch (err) {
      console.error('TTS playback failed:', err);
      setState('idle');
    }
  }, []);

  // Expose speak method via ref for external control
  useImperativeHandle(ref, () => ({ speak }), [speak]);

  const handleClick = () => {
    if (disabled) return;
    switch (state) {
      case 'idle':
      case 'speaking':
        startRecording();
        break;
      case 'listening':
        stopRecording();
        break;
      // processing: do nothing
    }
  };

  const formatTime = (secs: number) => {
    const m = Math.floor(secs / 60);
    const s = secs % 60;
    return `${m}:${s.toString().padStart(2, '0')}`;
  };

  return (
    <div className={`voice-orb-container orb-${state}`} data-testid="voice-orb">
      {/* Outer glow rings */}
      <div className="orb-glow orb-glow-1" />
      <div className="orb-glow orb-glow-2" />
      <div className="orb-glow orb-glow-3" />

      {/* Main orb button */}
      <button
        className={`voice-orb voice-orb--${state}`}
        onClick={handleClick}
        disabled={disabled || state === 'processing'}
        title={
          state === 'idle'
            ? 'Click to speak'
            : state === 'listening'
            ? 'Listening... Click to stop'
            : state === 'processing'
            ? 'Processing...'
            : 'Speaking...'
        }
      >
        <div className="orb-inner">
          <span className="orb-label">J.A.R.V.I.S</span>
          {state === 'listening' && (
            <span className="orb-timer">{formatTime(elapsed)}</span>
          )}
          {state === 'processing' && (
            <span className="orb-status">Processing...</span>
          )}
          {state === 'speaking' && (
            <div className="orb-wave">
              <span /><span /><span /><span /><span />
            </div>
          )}
        </div>
      </button>

      {/* State indicator text below orb */}
      <div className="orb-state-text">
        {state === 'idle' && 'Tap to speak'}
        {state === 'listening' && 'Listening...'}
        {state === 'processing' && 'Thinking...'}
        {state === 'speaking' && 'Speaking...'}
      </div>
    </div>
  );
});

VoiceOrbComponent.displayName = 'VoiceOrb';

export default VoiceOrbComponent;
