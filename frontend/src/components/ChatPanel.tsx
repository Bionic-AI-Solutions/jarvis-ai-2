/**
 * JARVIS AI — Chat panel component.
 */

import { useState, useRef, useEffect } from 'react';
import { useChatStore } from '../stores/chatStore';

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
        {messages.map((msg) => (
          <div key={msg.id} className={`message message-${msg.role}`}>
            <div className="message-role">{msg.role === 'user' ? 'You' : 'JARVIS'}</div>
            <div className="message-content">{msg.content}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>

      <div className="input-container">
        <textarea
          className="chat-input"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder="Type a message..."
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
