/**
 * JARVIS AI — Chat panel component.
 *
 * Renders user/assistant messages with visual differentiation based on
 * the pipeline's `message_type` metadata (chat, task_success, task_error,
 * clarification, safety_blocked, task).
 */

import { useState, useRef, useEffect, useCallback } from 'react';
import { useChatStore } from '../stores/chatStore';
import VoiceButton from './VoiceButton';
import type { MessageMetadata } from '../services/api';
import type { TranscriptionResult } from '../types';

/** Map message_type → CSS modifier class */
const MESSAGE_TYPE_CLASS: Record<string, string> = {
  chat: 'message-type-chat',
  clarification: 'message-type-clarification',
  safety_blocked: 'message-type-safety',
  task_success: 'message-type-success',
  task_error: 'message-type-error',
  task: 'message-type-task',
};

/** Label shown above the response depending on message type */
const MESSAGE_TYPE_LABEL: Record<string, string> = {
  chat: 'JARVIS',
  clarification: 'JARVIS — Needs Clarification',
  safety_blocked: 'JARVIS — Blocked',
  task_success: 'JARVIS — Task Complete',
  task_error: 'JARVIS — Task Failed',
  task: 'JARVIS — Executing',
};

/** Inline badge for execution results */
function ExecutionBadge({ metadata }: { metadata: MessageMetadata }) {
  if (!metadata.execution) return null;
  const { success, steps_executed, steps_total, duration_ms } = metadata.execution;
  return (
    <div className={`execution-badge ${success ? 'badge-success' : 'badge-error'}`}>
      <span className="badge-icon">{success ? '✓' : '✗'}</span>
      <span className="badge-text">
        {steps_executed}/{steps_total} steps — {(duration_ms / 1000).toFixed(1)}s
      </span>
    </div>
  );
}

/** Collapsible step results inside a task message */
function StepResults({ metadata }: { metadata: MessageMetadata }) {
  const [expanded, setExpanded] = useState(false);
  if (!metadata.execution?.step_results?.length) return null;

  return (
    <div className="step-results">
      <button
        className="step-results-toggle"
        onClick={() => setExpanded(!expanded)}
        type="button"
      >
        {expanded ? '▾ Hide steps' : '▸ Show steps'}
      </button>
      {expanded && (
        <ul className="step-results-list">
          {metadata.execution.step_results.map((step, i) => (
            <li key={i} className={`step-result ${step.success ? 'step-ok' : 'step-fail'}`}>
              <span className="step-icon">{step.success ? '✓' : '✗'}</span>
              <span className="step-desc">{step.description}</span>
              {step.error && <span className="step-error">{step.error}</span>}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

export function ChatPanel() {
  const [input, setInput] = useState('');
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const { activeSessionId, isLoading, sendMessage, activeMessages } = useChatStore();

  const messages = activeMessages();

  useEffect(() => {
    if (messagesEndRef.current && typeof messagesEndRef.current.scrollIntoView === 'function') {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;
    const content = input.trim();
    setInput('');
    await sendMessage(content);
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  /** Handle voice transcription — auto-send high-confidence results */
  const handleTranscription = useCallback(
    async (result: TranscriptionResult) => {
      if (!result.text.trim()) return;
      if (result.auto_accepted) {
        // High-confidence: send immediately
        await sendMessage(result.text.trim());
      } else {
        // Lower confidence: put text in input for user review
        setInput(result.text.trim());
      }
    },
    [sendMessage],
  );

  if (!activeSessionId) {
    return (
      <div className="chat-panel empty" data-testid="chat-panel-empty">
        <div className="empty-state">
          <h2>Welcome to JARVIS AI</h2>
          <p>Select a chat session or create a new one to get started.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="chat-panel" data-testid="chat-panel">
      <div className="messages-container">
        {messages.map((msg) => {
          const metadata = msg.metadata as MessageMetadata | undefined;
          const typeClass = metadata
            ? MESSAGE_TYPE_CLASS[metadata.message_type] ?? ''
            : '';
          const roleLabel =
            msg.role === 'user'
              ? 'You'
              : metadata
                ? MESSAGE_TYPE_LABEL[metadata.message_type] ?? 'JARVIS'
                : 'JARVIS';

          return (
            <div
              key={msg.id}
              className={`message message-${msg.role} ${typeClass}`}
              data-message-type={metadata?.message_type}
            >
              <div className="message-role">{roleLabel}</div>
              <div className="message-content">{msg.content}</div>
              {metadata && msg.role === 'assistant' && (
                <>
                  <ExecutionBadge metadata={metadata} />
                  <StepResults metadata={metadata} />
                  {metadata.duration_ms != null && metadata.duration_ms > 0 && (
                    <div className="message-meta-footer">
                      Pipeline: {(metadata.duration_ms / 1000).toFixed(1)}s
                      {metadata.plan?.confidence != null && (
                        <> · Confidence: {Math.round(metadata.plan.confidence * 100)}%</>
                      )}
                    </div>
                  )}
                </>
              )}
            </div>
          );
        })}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <VoiceButton
          onTranscription={handleTranscription}
          disabled={isLoading}
          className="voice-btn-inline"
        />
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message or use the mic..."
          disabled={isLoading}
          rows={1}
          data-testid="chat-input"
        />
        <button
          className="btn btn-primary send-btn"
          onClick={handleSend}
          disabled={!input.trim() || isLoading}
          data-testid="send-btn"
        >
          {isLoading ? '...' : 'Send'}
        </button>
      </div>
    </div>
  );
}
