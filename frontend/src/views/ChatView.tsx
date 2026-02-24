/**
 * JARVIS AI — Chat view (main page).
 */

import { useEffect } from 'react';
import { ChatPanel } from '../components/ChatPanel';
import { StepProgress } from '../components/StepProgress';
import { useChatStore } from '../stores/chatStore';
import { useExecutionStore } from '../stores/executionStore';
import { wsClient } from '../services/ws';

export function ChatView() {
  const { loadSessions, createSession, sessions, activeSessionId, selectSession } = useChatStore();
  const initWsListeners = useExecutionStore((s) => s.initWsListeners);

  useEffect(() => {
    loadSessions();
    wsClient.connect();
    const cleanup = initWsListeners();
    return () => {
      cleanup();
      wsClient.disconnect();
    };
  }, [loadSessions, initWsListeners]);

  return (
    <div className="chat-view" data-testid="chat-view">
      <div className="chat-sidebar">
        <div className="chat-sidebar-header">
          <h3>Conversations</h3>
          <button className="btn btn-primary btn-sm" onClick={() => createSession()}>
            + New
          </button>
        </div>
        <div className="session-list">
          {sessions.map((session) => (
            <div
              key={session.id}
              className={`session-item ${session.id === activeSessionId ? 'active' : ''}`}
              onClick={() => selectSession(session.id)}
            >
              <span className="session-title">{session.title}</span>
              <span className="session-date">
                {new Date(session.created_at).toLocaleDateString()}
              </span>
            </div>
          ))}
        </div>
      </div>

      <div className="chat-main">
        <ChatPanel />
      </div>

      <div className="chat-progress-panel">
        <StepProgress />
      </div>
    </div>
  );
}
