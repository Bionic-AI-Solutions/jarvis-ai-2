/**
 * JARVIS AI — Main layout with sidebar navigation.
 */

import { type ReactNode } from 'react';
import { NavLink } from 'react-router-dom';
import { useAuthStore } from '../stores/authStore';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  const { isAuthenticated, lock } = useAuthStore();

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
