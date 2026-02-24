/**
 * JARVIS AI — API client for backend communication.
 *
 * All API calls go through this module.
 * Reads backend URL from Electron IPC or falls back to env/proxy.
 */

const BASE_URL = '/api';

interface RequestOptions {
  method?: string;
  body?: unknown;
  headers?: Record<string, string>;
  token?: string;
}

class ApiClient {
  private baseUrl: string;
  private token: string | null = null;

  constructor(baseUrl: string = BASE_URL) {
    this.baseUrl = baseUrl;
  }

  setToken(token: string | null) {
    this.token = token;
  }

  private async request<T>(path: string, options: RequestOptions = {}): Promise<T> {
    const { method = 'GET', body, headers = {} } = options;

    const fetchHeaders: Record<string, string> = {
      'Content-Type': 'application/json',
      ...headers,
    };

    if (this.token) {
      fetchHeaders['Authorization'] = `Bearer ${this.token}`;
    }

    const response = await fetch(`${this.baseUrl}${path}`, {
      method,
      headers: fetchHeaders,
      body: body ? JSON.stringify(body) : undefined,
    });

    if (!response.ok) {
      const errorBody = await response.json().catch(() => ({}));
      throw new ApiError(response.status, errorBody.message || response.statusText, errorBody);
    }

    return response.json();
  }

  // ── Health ──────────────────────────────────────────────

  health() {
    return this.request<HealthResponse>('/health'.replace('/api', ''), { method: 'GET' });
  }

  // ── Auth ────────────────────────────────────────────────

  setPassphrase(passphrase: string) {
    return this.request('/auth/passphrase', { method: 'POST', body: { passphrase } });
  }

  verifyPassphrase(passphrase: string) {
    return this.request<AuthResponse>('/auth/verify', { method: 'POST', body: { passphrase } });
  }

  getAuthStatus() {
    return this.request<LockStatusResponse>('/auth/status');
  }

  lock() {
    return this.request('/auth/lock', { method: 'POST' });
  }

  unlock(passphrase: string) {
    return this.request('/auth/unlock', { method: 'POST', body: { passphrase } });
  }

  // ── Chats ───────────────────────────────────────────────

  listChats() {
    return this.request<ChatSession[]>('/chats');
  }

  createChat(data: { title?: string; mode?: string }) {
    return this.request<ChatSession>('/chats', { method: 'POST', body: data });
  }

  getChat(id: string) {
    return this.request<ChatSession>(`/chats/${id}`);
  }

  sendMessage(chatId: string, content: string, role: string = 'user') {
    return this.request(`/chats/${chatId}/messages`, {
      method: 'POST',
      body: { role, content },
    });
  }

  // ── Workflows ───────────────────────────────────────────

  listWorkflows() {
    return this.request<Workflow[]>('/workflows');
  }

  createWorkflow(data: { name: string; description?: string; steps: unknown[] }) {
    return this.request<Workflow>('/workflows', { method: 'POST', body: data });
  }

  // ── Executions ──────────────────────────────────────────

  listExecutions() {
    return this.request<Execution[]>('/executions');
  }

  startExecution(workflowId: string) {
    return this.request<Execution>('/executions', {
      method: 'POST',
      body: { workflow_id: workflowId },
    });
  }

  cancelExecution(executionId: string) {
    return this.request(`/executions/${executionId}/cancel`, { method: 'POST' });
  }

  // ── Settings ────────────────────────────────────────────

  getSettings() {
    return this.request('/settings');
  }

  updateSetting(key: string, value: string) {
    return this.request('/settings', { method: 'PUT', body: { key, value } });
  }
}

// ── Types ──────────────────────────────────────────────────

export interface HealthResponse {
  status: string;
  version: string;
  uptime_seconds: number;
  components: { name: string; status: string }[];
}

export interface AuthResponse {
  authenticated: boolean;
  token: string | null;
  message: string;
}

export interface LockStatusResponse {
  is_locked: boolean;
  locked_out: boolean;
  lockout_remaining_seconds: number;
  has_passphrase: boolean;
  auto_lock_timeout_mins: number;
}

export interface ChatSession {
  id: string;
  title: string;
  mode: string;
  is_active: boolean;
  created_at: string;
  messages: ChatMessage[];
}

export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  sequence: number;
  created_at: string;
}

export interface Workflow {
  id: string;
  name: string;
  description: string;
  steps: unknown[];
  version: number;
  is_active: boolean;
}

export interface Execution {
  id: string;
  workflow_id: string;
  status: string;
  current_step: number;
  total_steps: number;
  started_at: string | null;
  completed_at: string | null;
}

export class ApiError extends Error {
  status: number;
  body: unknown;

  constructor(status: number, message: string, body: unknown) {
    super(message);
    this.name = 'ApiError';
    this.status = status;
    this.body = body;
  }
}

// Singleton
export const api = new ApiClient();
