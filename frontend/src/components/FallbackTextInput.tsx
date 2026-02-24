/**
 * JARVIS AI — Fallback Text Input (always visible).
 *
 * Story 1.8: Chat box always visible, user can type even if voice is active.
 * If mic not available, hide voice hotkey and show text input.
 * Typed input processed same as voice (through RAG Agent).
 * Labeled as "typed" not "voice".
 */

import { useState, useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';

interface FallbackTextInputProps {
  /** Whether voice input is currently active */
  voiceActive?: boolean;
  /** Called when user submits typed text */
  onSubmit?: (text: string, source: 'typed' | 'voice') => void;
}

export function FallbackTextInput({ voiceActive = false, onSubmit }: FallbackTextInputProps) {
  const [input, setInput] = useState('');
  const [micAvailable, setMicAvailable] = useState(false);
  const { sendMessage, isLoading } = useChatStore();

  // Check microphone availability
  useEffect(() => {
    async function checkMic() {
      try {
        const devices = await navigator.mediaDevices.enumerateDevices();
        const hasMic = devices.some((d) => d.kind === 'audioinput');
        setMicAvailable(hasMic);
      } catch {
        setMicAvailable(false);
      }
    }
    // Only check if mediaDevices API exists (may not in test environments)
    if (typeof navigator !== 'undefined' && navigator.mediaDevices?.enumerateDevices) {
      checkMic();
    }
  }, []);

  const handleSubmit = async () => {
    if (!input.trim() || isLoading) return;
    const text = input.trim();
    setInput('');

    if (onSubmit) {
      onSubmit(text, 'typed');
    } else {
      await sendMessage(text);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <div className="fallback-text-input" data-testid="fallback-text-input">
      <div className="input-row">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={voiceActive ? 'Type override (voice active)...' : 'Type your intent...'}
          disabled={isLoading}
          rows={1}
          data-testid="fallback-input"
        />
        <button
          className="btn btn-primary send-btn"
          onClick={handleSubmit}
          disabled={!input.trim() || isLoading}
          data-testid="fallback-send-btn"
        >
          Send
        </button>
      </div>

      <div className="input-status">
        {voiceActive && <span className="status-voice">🎤 Voice active</span>}
        {!micAvailable && !voiceActive && (
          <span className="status-no-mic" data-testid="no-mic-indicator">
            ⌨️ Text-only mode (no microphone detected)
          </span>
        )}
      </div>
    </div>
  );
}
