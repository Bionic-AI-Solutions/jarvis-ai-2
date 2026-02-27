/**
 * JARVIS AI — Chat view (main page).
 * 
 * Layout: Chat main area with optional right panel (only during execution).
 * Voice mode toggle switches between text chat and JARVIS orb UI.
 */

import { useEffect, useCallback, useState, useRef } from 'react';
import { ChatPanel } from '../components/ChatPanel';
import { StepProgress } from '../components/StepProgress';
import { ExecutionTimeline } from '../components/ExecutionTimeline';
import { LearnedWorkflowsPanel } from '../components/LearnedWorkflowsPanel';
import RecoveryDialog from '../components/RecoveryDialog';
import VoiceOrb from '../components/VoiceOrb';
import type { OrbState, VoiceOrbHandle } from '../components/VoiceOrb';
import { useChatStore } from '../stores/chatStore';
import { useExecutionStore } from '../stores/executionStore';
import { wsClient } from '../services/ws';
import { api } from '../services/api';
import type { TranscriptionResult } from '../types';

export function ChatView() {
  const { loadSessions, createSession, sessions, activeSessionId, selectSession, sendMessage } = useChatStore();
  const initWsListeners = useExecutionStore((s) => s.initWsListeners);
  const recoveryNotification = useExecutionStore((s) => s.recoveryNotification);
  const clearRecovery = useExecutionStore((s) => s.clearRecovery);
  
  const [voiceMode, setVoiceMode] = useState(false);
  const [showRightPanel, setShowRightPanel] = useState(false);
  const [orbState, setOrbState] = useState<OrbState>('idle');
  const voiceOrbRef = useRef<{ speak: (text: string) => Promise<void> }>(null);

  // Track if there's an active execution to show/hide right panel
  const activeExecution = useExecutionStore((s) => s.activeExecution);
  useEffect(() => {
    const exec = activeExecution();
    if (exec) setShowRightPanel(true);
  }, [activeExecution]);

  // Listen for assistant messages and trigger TTS in voice mode
  const lastMessageRef = useRef<string | null>(null);
  const messagesInSession = activeSessionId
    ? sessions.find((s) => s.id === activeSessionId)?.messages || []
    : [];
  useEffect(() => {
    if (!voiceMode || !voiceOrbRef.current) return;
    const msgs = messagesInSession.sort((a, b) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime());
    const lastMsg = msgs[msgs.length - 1];
    if (lastMsg?.role === 'assistant' && lastMsg.content !== lastMessageRef.current) {
      lastMessageRef.current = lastMsg.content;
      voiceOrbRef.current.speak(lastMsg.content);
    }
  }, [messagesInSession, voiceMode]);

  useEffect(() => {
    loadSessions();
    wsClient.connect();
    const cleanup = initWsListeners();
    return () => {
      cleanup();
      wsClient.disconnect();
    };
  }, [loadSessions, initWsListeners]);

  const handleRecoveryAction = useCallback(
    async (executionId: string, stepIndex: number, action: string) => {
      try {
        await api.resolveRecovery(executionId, stepIndex, action);
      } catch (err) {
        console.error('[Recovery] Failed to resolve:', err);
      } finally {
        clearRecovery();
      }
    },
    [clearRecovery],
  );

  /** Handle voice transcription in voice mode — auto-sends */
  const handleVoiceTranscription = useCallback(
    async (result: TranscriptionResult) => {
      if (!result.text.trim()) return;
      await sendMessage(result.text.trim());
    },
    [sendMessage],
  );

  return (
    <div className="chat-view" data-testid="chat-view">
      <div className="chat-main">
        {/* Voice/Text mode toggle */}
        <div className="mode-toggle-bar">
          <button
            className={`mode-toggle-btn ${!voiceMode ? 'active' : ''}`}
            onClick={() => setVoiceMode(false)}
          >
            💬 Chat
          </button>
          <button
            className={`mode-toggle-btn ${voiceMode ? 'active' : ''}`}
            onClick={() => setVoiceMode(true)}
          >
            🎤 Voice
          </button>
          <div className="mode-toggle-spacer" />
          <button
            className={`panel-toggle-btn ${showRightPanel ? 'active' : ''}`}
            onClick={() => setShowRightPanel(!showRightPanel)}
            title={showRightPanel ? 'Hide details' : 'Show details'}
          >
            {showRightPanel ? '◀' : '▶'} Details
          </button>
        </div>

        {/* Main content area — chat or voice orb */}
        {voiceMode ? (
          <div className="voice-mode-container">
            <VoiceOrb
              ref={voiceOrbRef}
              onTranscription={handleVoiceTranscription}
              onError={(err) => console.error('[Voice]', err)}
              onStateChange={setOrbState}
            />
          </div>
        ) : (
          <ChatPanel />
        )}
      </div>

      {/* Right panel — collapsed by default, shown during execution */}
      {showRightPanel && (
        <div className="chat-progress-panel">
          <StepProgress />
          <ExecutionTimeline />
          <LearnedWorkflowsPanel />
        </div>
      )}

      {/* Recovery Dialog — shown when orchestrator reaches L5/L6 */}
      <RecoveryDialog
        notification={recoveryNotification}
        onAction={handleRecoveryAction}
      />
    </div>
  );
}
