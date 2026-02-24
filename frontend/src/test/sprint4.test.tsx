/**
 * JARVIS AI — Frontend tests: Sprint 4
 *
 * Tests for: Layout, StepProgress, ChatPanel, stores, API client, WS client
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { Layout } from '../components/Layout';
import { StepProgress } from '../components/StepProgress';
import { ChatPanel } from '../components/ChatPanel';
import { useExecutionStore } from '../stores/executionStore';
import { useChatStore } from '../stores/chatStore';
import { useAuthStore } from '../stores/authStore';
import { ApiError, api } from '../services/api';
import { wsClient } from '../services/ws';
import type { StepStatus } from '../types';

// ── Layout ─────────────────────────────────────────────

describe('Layout', () => {
  it('renders sidebar with logo and navigation', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div>Content</div>
        </Layout>
      </BrowserRouter>,
    );

    expect(screen.getByText('JARVIS AI')).toBeInTheDocument();
    expect(screen.getByText('Chat')).toBeInTheDocument();
    expect(screen.getByText('Workflows')).toBeInTheDocument();
    expect(screen.getByText('Settings')).toBeInTheDocument();
    expect(screen.getByText('Content')).toBeInTheDocument();
  });

  it('renders version info', () => {
    render(
      <BrowserRouter>
        <Layout>
          <div />
        </Layout>
      </BrowserRouter>,
    );
    expect(screen.getByText('v0.1.0')).toBeInTheDocument();
  });

  it('shows lock button when authenticated', () => {
    useAuthStore.setState({ isAuthenticated: true });
    render(
      <BrowserRouter>
        <Layout>
          <div />
        </Layout>
      </BrowserRouter>,
    );
    expect(screen.getByText(/Lock/)).toBeInTheDocument();
  });
});

// ── StepProgress ───────────────────────────────────────

describe('StepProgress', () => {
  beforeEach(() => {
    useExecutionStore.setState({
      executions: new Map(),
      activeExecutionId: null,
    });
  });

  it('shows empty state when no active execution', () => {
    render(<StepProgress />);
    expect(screen.getByTestId('step-progress-empty')).toBeInTheDocument();
    expect(screen.getByText(/No active execution/)).toBeInTheDocument();
  });

  it('renders steps when execution is active', () => {
    const steps = [
      { index: 0, name: 'Analyze', agent: 'analyzer', action: 'run', status: 'completed' as StepStatus },
      { index: 1, name: 'Generate', agent: 'generator', action: 'run', status: 'running' as StepStatus },
      { index: 2, name: 'Review', agent: 'reviewer', action: 'run', status: 'pending' as StepStatus },
    ];

    const execMap = new Map();
    execMap.set('exec-1', {
      executionId: 'exec-1',
      workflowId: 'wf-1',
      steps,
      currentStep: 1,
      totalSteps: 3,
      status: 'running',
    });

    useExecutionStore.setState({
      executions: execMap,
      activeExecutionId: 'exec-1',
    });

    render(<StepProgress />);

    expect(screen.getByTestId('step-progress')).toBeInTheDocument();
    expect(screen.getByText('Analyze')).toBeInTheDocument();
    expect(screen.getByText('Generate')).toBeInTheDocument();
    expect(screen.getByText('Review')).toBeInTheDocument();
    expect(screen.getByText(/1 \/ 3 steps/)).toBeInTheDocument();
  });

  it('shows progress percentage', () => {
    const steps = [
      { index: 0, name: 'Step 1', agent: 'a', action: 'run', status: 'completed' as StepStatus },
      { index: 1, name: 'Step 2', agent: 'a', action: 'run', status: 'completed' as StepStatus },
      { index: 2, name: 'Step 3', agent: 'a', action: 'run', status: 'pending' as StepStatus },
    ];

    const execMap = new Map();
    execMap.set('exec-2', {
      executionId: 'exec-2',
      workflowId: 'wf-2',
      steps,
      currentStep: 2,
      totalSteps: 3,
      status: 'running',
    });

    useExecutionStore.setState({
      executions: execMap,
      activeExecutionId: 'exec-2',
    });

    render(<StepProgress />);
    expect(screen.getByText(/67%/)).toBeInTheDocument();
  });
});

// ── ChatPanel ──────────────────────────────────────────

describe('ChatPanel', () => {
  beforeEach(() => {
    useChatStore.setState({
      sessions: [],
      activeSessionId: null,
      isLoading: false,
      error: null,
    });
  });

  it('shows empty state when no session selected', () => {
    render(<ChatPanel />);
    expect(screen.getByTestId('chat-panel-empty')).toBeInTheDocument();
    expect(screen.getByText(/Welcome to JARVIS AI/)).toBeInTheDocument();
  });

  it('renders chat input when session is active', () => {
    useChatStore.setState({
      sessions: [
        {
          id: 'sess-1',
          title: 'Test Session',
          mode: 'chat',
          is_active: true,
          created_at: new Date().toISOString(),
          messages: [],
        },
      ],
      activeSessionId: 'sess-1',
    });

    render(<ChatPanel />);
    expect(screen.getByTestId('chat-input')).toBeInTheDocument();
    expect(screen.getByTestId('send-btn')).toBeInTheDocument();
  });

  it('renders messages', () => {
    useChatStore.setState({
      sessions: [
        {
          id: 'sess-2',
          title: 'Test',
          mode: 'chat',
          is_active: true,
          created_at: new Date().toISOString(),
          messages: [
            { id: 'msg-1', role: 'user', content: 'Hello JARVIS', sequence: 1, created_at: new Date().toISOString() },
            { id: 'msg-2', role: 'assistant', content: 'Hello! How can I help?', sequence: 2, created_at: new Date().toISOString() },
          ],
        },
      ],
      activeSessionId: 'sess-2',
    });

    render(<ChatPanel />);
    expect(screen.getByText('Hello JARVIS')).toBeInTheDocument();
    expect(screen.getByText('Hello! How can I help?')).toBeInTheDocument();
  });
});

// ── Execution Store ────────────────────────────────────

describe('ExecutionStore', () => {
  beforeEach(() => {
    useExecutionStore.setState({
      executions: new Map(),
      activeExecutionId: null,
    });
  });

  it('tracks a new execution', () => {
    const steps = [
      { index: 0, name: 'Step 1', agent: 'a', action: 'run', status: 'pending' as StepStatus },
    ];
    useExecutionStore.getState().trackExecution('exec-1', 'wf-1', steps);

    const state = useExecutionStore.getState();
    expect(state.executions.size).toBe(1);
    expect(state.activeExecutionId).toBe('exec-1');
    expect(state.executions.get('exec-1')?.status).toBe('pending');
  });

  it('updates step status', () => {
    const steps = [
      { index: 0, name: 'Step 1', agent: 'a', action: 'run', status: 'pending' as StepStatus },
      { index: 1, name: 'Step 2', agent: 'b', action: 'run', status: 'pending' as StepStatus },
    ];
    useExecutionStore.getState().trackExecution('exec-2', 'wf-2', steps);
    useExecutionStore.getState().updateStep('exec-2', 0, 'running');

    const exec = useExecutionStore.getState().executions.get('exec-2');
    expect(exec?.steps[0].status).toBe('running');
    expect(exec?.currentStep).toBe(0);
  });

  it('completes execution', () => {
    const steps = [
      { index: 0, name: 'Step 1', agent: 'a', action: 'run', status: 'pending' as StepStatus },
    ];
    useExecutionStore.getState().trackExecution('exec-3', 'wf-3', steps);
    useExecutionStore.getState().completeExecution('exec-3', 'completed');

    expect(useExecutionStore.getState().executions.get('exec-3')?.status).toBe('completed');
  });

  it('removes execution', () => {
    const steps = [
      { index: 0, name: 'Step 1', agent: 'a', action: 'run', status: 'pending' as StepStatus },
    ];
    useExecutionStore.getState().trackExecution('exec-4', 'wf-4', steps);
    useExecutionStore.getState().removeExecution('exec-4');

    expect(useExecutionStore.getState().executions.size).toBe(0);
    expect(useExecutionStore.getState().activeExecutionId).toBeNull();
  });

  it('returns active execution', () => {
    const steps = [
      { index: 0, name: 'Step 1', agent: 'a', action: 'run', status: 'pending' as StepStatus },
    ];
    useExecutionStore.getState().trackExecution('exec-5', 'wf-5', steps);
    expect(useExecutionStore.getState().activeExecution()?.executionId).toBe('exec-5');
  });
});

// ── API Client ─────────────────────────────────────────

describe('ApiClient', () => {
  it('sets and clears token', () => {
    api.setToken('test-token');
    // Token is private, just verify it doesn't throw
    api.setToken(null);
  });

  it('ApiError has correct properties', () => {
    const error = new ApiError(401, 'Unauthorized', { detail: 'bad token' });
    expect(error.status).toBe(401);
    expect(error.message).toBe('Unauthorized');
    expect(error.body).toEqual({ detail: 'bad token' });
    expect(error.name).toBe('ApiError');
  });
});

// ── WebSocket Client ───────────────────────────────────

describe('WebSocket Client', () => {
  it('registers and unregisters handlers', () => {
    const handler = vi.fn();
    const unsub = wsClient.on('test', handler);
    expect(typeof unsub).toBe('function');
    unsub();
  });

  it('reports disconnected when not connected', () => {
    expect(wsClient.isConnected).toBe(false);
  });

  it('registers wildcard handlers', () => {
    const handler = vi.fn();
    const unsub = wsClient.onAny(handler);
    expect(typeof unsub).toBe('function');
    unsub();
  });
});

// ── Auth Store ─────────────────────────────────────────

describe('AuthStore', () => {
  beforeEach(() => {
    useAuthStore.setState({
      isLocked: true,
      hasPassphrase: false,
      isAuthenticated: false,
      isLoading: false,
      error: null,
    });
  });

  it('has correct initial state', () => {
    const state = useAuthStore.getState();
    expect(state.isLocked).toBe(true);
    expect(state.hasPassphrase).toBe(false);
    expect(state.isAuthenticated).toBe(false);
  });
});
