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
