/**
 * JARVIS AI — Main layout with sidebar navigation + conversations list.
 */

import { type ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';
import { useChatStore } from '../stores/chatStore';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { isAuthenticated, lock } = useAuthStore();
  const { sessions, activeSessionId, selectSession, createSession } = useChatStore();

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <div className="logo">
            <span className="logo-icon">⚡</span>
            <span className="logo-text">JARVIS AI</span>
          </div>
        </div>

        <nav className="sidebar-nav">
          <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
            <span className="nav-icon">💬</span>
            <span>Chat</span>
          </NavLink>
          <NavLink
            to="/workflows"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">🔄</span>
            <span>Workflows</span>
          </NavLink>
          <NavLink
            to="/settings"
            className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
          >
            <span className="nav-icon">⚙️</span>
            <span>Settings</span>
          </NavLink>
        </nav>

        {/* Conversations list — below nav */}
        <div className="sidebar-conversations">
          <div className="sidebar-conversations-header">
            <span className="sidebar-section-title">Conversations</span>
            <button className="btn-icon btn-new-chat" onClick={() => createSession()} title="New chat">
              +
            </button>
          </div>
          <div className="sidebar-session-list">
            {sessions.map((session) => (
              <div
                key={session.id}
                className={`sidebar-session-item ${session.id === activeSessionId ? 'active' : ''}`}
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

        <div className="sidebar-footer">
          {isAuthenticated && (
            <button className="btn btn-secondary btn-sm" onClick={() => lock()}>
              🔒 Lock
            </button>
          )}
          <div className="version-info">v0.1.0</div>
        </div>
      </aside>

      <main className="main-content">{children}</main>
    </div>
  );
}
