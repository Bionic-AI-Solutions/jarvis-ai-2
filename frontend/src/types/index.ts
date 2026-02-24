/**
 * JARVIS AI — Global TypeScript type definitions.
 */

/** Electron preload API exposed via contextBridge */
export interface JarvisElectronApi {
  getBackendUrl: () => Promise<string>;
  healthCheck: () => Promise<{ status: string }>;
  getVersion: () => Promise<string>;
  on: (channel: string, callback: (...args: unknown[]) => void) => void;
  removeListener: (channel: string, callback: (...args: unknown[]) => void) => void;
}

declare global {
  interface Window {
    jarvis?: JarvisElectronApi;
  }
}

/** Execution step status */
export type StepStatus = 'pending' | 'running' | 'completed' | 'failed' | 'skipped';

/** Single workflow execution step */
export interface ExecutionStep {
  index: number;
  name: string;
  agent: string;
  action: string;
  status: StepStatus;
  startedAt?: string;
  completedAt?: string;
  result?: unknown;
  error?: string;
}

/** Execution progress data (from WS updates) */
export interface ExecutionProgress {
  executionId: string;
  workflowId: string;
  steps: ExecutionStep[];
  currentStep: number;
  totalSteps: number;
  status: 'pending' | 'running' | 'completed' | 'failed' | 'cancelled';
  startedAt?: string;
}

/** Screenshot capture data */
export interface Screenshot {
  id: string;
  executionId: string;
  stepIndex: number;
  dataUrl: string;
  timestamp: string;
  description?: string;
}

/** Application mode */
export type AppMode = 'chat' | 'agent' | 'workflow';

/** Auth state */
export interface AuthState {
  isLocked: boolean;
  hasPassphrase: boolean;
  isAuthenticated: boolean;
}

/** Voice transcription result */
export interface TranscriptionResult {
  text: string;
  confidence: number;
  language: string;
  duration_ms: number;
  auto_accepted: boolean;
  needs_re_speak: boolean;
  source: 'voice' | 'typed';
}

/** Voice configuration */
export interface VoiceConfig {
  confidence_threshold: number;
  auto_accept_threshold: number;
  re_speak_threshold: number;
  silence_db_threshold: number;
  silence_duration: number;
  max_recording_seconds: number;
  language: string;
  device_id: string | null;
}

/** Voice status */
export interface VoiceStatus {
  service: string;
  config: VoiceConfig;
  whisper: {
    available: boolean;
    models: string[];
    ollama_reachable: boolean;
  };
}

/** Recovery notification from WebSocket */
export interface RecoveryNotification {
  type: 'recovery';
  level: number;
  message: string;
  execution_id: string;
  step_index: number;
  options?: string[];
}

// ── Sprint 7: Workflow Execution Types ──────────────────────

/** Workflow template/item returned from API */
export interface WorkflowItem {
  id: string;
  name: string;
  description: string | null;
  steps_json: string;
  is_active: boolean;
  tags: string | null;
  success_rate: number;
  execution_count: number;
  is_template: boolean;
  template_category: string | null;
  created_at: string;
  updated_at: string;
}

/** Workflow parameter schema */
export interface WorkflowParameter {
  name: string;
  type: string;
  description: string;
  default?: string;
  required?: boolean;
}

/** Search request */
export interface WorkflowSearchRequest {
  query?: string;
  tags?: string[];
  templates_only?: boolean;
}

/** Clone request */
export interface WorkflowCloneRequest {
  new_name: string;
  description?: string;
  tags?: string[];
}

/** Execute request */
export interface WorkflowExecuteRequest {
  parameter_values?: Record<string, string>;
  session_id?: string;
}

/** Execute response */
export interface WorkflowExecuteResponse {
  execution_id: string;
  workflow_id: string;
  status: string;
  total_steps: number;
}

/** Export format */
export type WorkflowExportFormat = 'json' | 'csv';

/** Error context snapshot summary */
export interface ContextSnapshotSummary {
  id: string;
  step_index: number;
  timestamp: string | null;
}

/** Recovery suggestion */
export interface RecoverySuggestionItem {
  action: string;
  description: string;
  confidence: number;
}

/** AI recovery result */
export interface RecoverySuggestionResult {
  diagnosis: string;
  suggestions: RecoverySuggestionItem[];
  can_auto_recover: boolean;
  auto_recovery_action: string | null;
  generated_at: string;
  model_used: string;
}

// ── Sprint 8: Security & Learning Types ─────────────────────

/** Audit trail entry */
export interface AuditEntry {
  id: string;
  actor: string;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  detail: string | null;
  ip_address: string;
  result: string;
  entry_hash: string;
  prev_hash: string | null;
  timestamp: string;
}

/** Audit chain verification result */
export interface AuditVerifyResult {
  valid: boolean;
  entries_checked: number;
  first_broken_id: string | null;
  message: string;
}

/** Active session */
export interface ActiveSession {
  id: string;
  user_id: string;
  token_jti: string;
  ip_address: string;
  user_agent: string | null;
  is_active: boolean;
  created_at: string;
  last_activity: string;
}

/** Queued request item */
export interface QueueItem {
  id: string;
  session_id: string | null;
  request_type: string;
  payload: Record<string, unknown>;
  status: string;
  timestamp: string;
}

/** Execution pattern */
export interface ExecutionPattern {
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

/** Confidence history entry */
export interface ConfidenceHistoryEntry {
  id: string;
  context: string;
  old_value: number;
  new_value: number;
  reason: string;
  timestamp: string;
}

/** Passphrase strength result */
export interface PassphraseStrength {
  strong: boolean;
  score: number;
  feedback: string[];
}

