/**
 * JARVIS AI — API client for backend communication.
 *
 * All API calls go through this module.
 * Reads backend URL from Electron IPC or falls back to env/proxy.
 */

// Determine base URL based on environment
const getBaseUrl = (): string => {
  // Check if running in Electron (preload exposes window.jarvis)
  const isElectron = !!(window as any).jarvis;
  // Also check if we're on file:// protocol (Electron production)
  const isFileProtocol = window.location.protocol === 'file:';
  
  if (isElectron || isFileProtocol) {
    // Production (Electron): Use direct backend URL
    return 'http://127.0.0.1:9000/api';
  } else {
    // Development: Use Vite proxy (routes /api to backend)
    return '/api';
  }
};

const BASE_URL = getBaseUrl();

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

  async health() {
    // Health endpoint is at /health (no /api prefix)
    const isElectron = !!(window as any).jarvis || window.location.protocol === 'file:';
    const healthUrl = isElectron
      ? 'http://127.0.0.1:9000/health'
      : '/health';
    
    const response = await fetch(healthUrl);
    if (!response.ok) throw new ApiError(response.status, 'Health check failed', {});
    return response.json() as Promise<HealthResponse>;
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
    return this.request<ChatMessage>(`/chats/${chatId}/messages`, {
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

  cancelExecution(executionId: string, reason?: string) {
    return this.request(`/executions/${executionId}/cancel`, {
      method: 'POST',
      body: { reason: reason ?? null },
    });
  }

  resolveRecovery(executionId: string, stepIndex: number, action: string) {
    return this.request(`/executions/${executionId}/recovery/${stepIndex}`, {
      method: 'POST',
      body: { action },
    });
  }

  // ── Settings ────────────────────────────────────────────

  getSettings() {
    return this.request('/settings');
  }

  updateSetting(key: string, value: string) {
    return this.request('/settings', { method: 'PUT', body: { key, value } });
  }

  // ── Voice ───────────────────────────────────────────────

  transcribeAudio(audiob64: string) {
    return this.request<{ text: string }>('/voice/transcribe', {
      method: 'POST',
      body: { audio_b64: audiob64 },
    });
  }

  detectSilence(audiob64: string, sampleRate: number = 16000, sampleWidth: number = 2) {
    return this.request<SilenceResponse>('/voice/silence', {
      method: 'POST',
      body: { audio_b64: audiob64, sample_rate: sampleRate, sample_width: sampleWidth },
    });
  }

  getVoiceConfig() {
    return this.request('/voice/config');
  }

  updateVoiceConfig(config: { confidence_threshold?: number; silence_duration?: number; max_recording_seconds?: number }) {
    return this.request('/voice/config', { method: 'PUT', body: config });
  }

  /**
   * Synthesize text to speech via edge-tts.
   * Returns an ArrayBuffer of MP3 audio data.
   */
  async synthesizeSpeech(text: string, voice?: string): Promise<ArrayBuffer> {
    const isElectron = !!(window as any).jarvis || window.location.protocol === 'file:';
    const url = isElectron
      ? `http://127.0.0.1:9000/api/voice/tts`
      : `${this.baseUrl}/voice/tts`;

    const response = await fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...(this.token ? { Authorization: `Bearer ${this.token}` } : {}),
      },
      body: JSON.stringify({ text, voice: voice || undefined }),
    });

    if (!response.ok) {
      throw new ApiError(response.status, 'TTS synthesis failed', {});
    }

    return response.arrayBuffer();
  }

  /** Check TTS engine availability */
  getTTSStatus() {
    return this.request<{ available: boolean; engine: string; voices: string[] }>('/voice/tts/status');
  }

  // ── Learning ────────────────────────────────────────────

  listPatterns(minConfidence?: number) {
    const params = minConfidence != null ? `?min_confidence=${minConfidence}` : '';
    return this.request<PatternListResponse>(`/learning/patterns${params}`);
  }

  listSuggestions(intent?: string) {
    const params = intent ? `?intent=${encodeURIComponent(intent)}` : '';
    return this.request<SuggestionListResponse>(`/learning/suggestions${params}`);
  }

  acceptSuggestion(patternId: string) {
    return this.request(`/learning/suggestions/${patternId}/accept`, { method: 'POST' });
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
  updated_at: string;
  messages?: ChatMessage[];
}

/** Pipeline metadata attached to assistant responses */
export interface MessageMetadata {
  message_type: 'chat' | 'clarification' | 'safety_blocked' | 'task_success' | 'task_error' | 'task';
  pipeline_stages?: string[];
  duration_ms?: number;
  plan?: {
    steps: Array<{ action: string; description: string }>;
    confidence: number;
  };
  execution?: {
    success: boolean;
    steps_executed: number;
    steps_total: number;
    duration_ms: number;
    step_results: Array<{
      success: boolean;
      description: string;
      error?: string;
      duration_ms: number;
    }>;
  };
  observation?: Record<string, unknown>;
}

export interface ChatMessage {
  id: string;
  role: string;
  content: string;
  sequence: number;
  created_at: string;
  metadata?: MessageMetadata;
}

export interface Workflow {
  id: string;
  name: string;
  description?: string;
  steps_json?: string;
  trigger_type: string;
  is_active: boolean;
  version: number;
  tags?: string;
  success_rate: number;
  execution_count: number;
  is_template: boolean;
  created_at: string;
  updated_at: string;
}

export interface SilenceResponse {
  is_silent: boolean;
  avg_db: number;
  duration_seconds: number;
  should_submit: boolean;
}

export interface PatternItem {
  id: string;
  pattern_hash: string;
  intent: string;
  steps: Array<{ agent: string; action: string }>;
  frequency: number;
  success_rate: number;
  confidence: number;
  suggested: boolean;
  accepted: boolean;
  last_seen: string;
}

export interface PatternListResponse {
  patterns: PatternItem[];
  total: number;
}

export interface SuggestionItem {
  id: string;
  intent: string;
  steps: Array<{ agent: string; action: string }>;
  confidence: number;
  success_rate: number;
  frequency: number;
}

export interface SuggestionListResponse {
  suggestions: SuggestionItem[];
  total: number;
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
