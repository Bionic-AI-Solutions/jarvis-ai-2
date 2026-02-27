/**
 * JARVIS AI — Execution store (Zustand).
 *
 * Story 2.1: Real-Time Step Progress
 * Tracks active execution state with step-by-step updates from WebSocket.
 */

import { create } from 'zustand';
import type { ExecutionProgress, ExecutionStep, StepStatus, RecoveryNotification } from '../types';
import { wsClient } from '../services/ws';

interface ExecutionStore {
  /** Currently tracked executions */
  executions: Map<string, ExecutionProgress>;

  /** Currently focused execution ID */
  activeExecutionId: string | null;

  /** Active recovery notification (L5/L6 dialog) */
  recoveryNotification: RecoveryNotification | null;

  /** Get the active execution */
  activeExecution: () => ExecutionProgress | null;

  /** Start tracking a new execution */
  trackExecution: (executionId: string, workflowId: string, steps: ExecutionStep[]) => void;

  /** Update a specific step's status */
  updateStep: (executionId: string, stepIndex: number, status: StepStatus, result?: unknown, error?: string) => void;

  /** Set the active execution */
  setActiveExecution: (executionId: string | null) => void;

  /** Mark entire execution as completed/failed */
  completeExecution: (executionId: string, status: 'completed' | 'failed') => void;

  /** Clear a finished execution from tracking */
  removeExecution: (executionId: string) => void;

  /** Show recovery dialog */
  showRecovery: (notification: RecoveryNotification) => void;

  /** Clear recovery dialog after user acts */
  clearRecovery: () => void;

  /** Initialize WebSocket listeners */
  initWsListeners: () => () => void;
}

export const useExecutionStore = create<ExecutionStore>((set, get) => ({
  executions: new Map(),
  activeExecutionId: null,
  recoveryNotification: null,

  activeExecution: () => {
    const { executions, activeExecutionId } = get();
    return activeExecutionId ? executions.get(activeExecutionId) ?? null : null;
  },

  trackExecution: (executionId, workflowId, steps) => {
    set((state) => {
      const newMap = new Map(state.executions);
      newMap.set(executionId, {
        executionId,
        workflowId,
        steps,
        currentStep: 0,
        totalSteps: steps.length,
        status: 'pending',
        startedAt: new Date().toISOString(),
      });
      return { executions: newMap, activeExecutionId: executionId };
    });
  },

  updateStep: (executionId, stepIndex, status, result, error) => {
    set((state) => {
      const newMap = new Map(state.executions);
      const exec = newMap.get(executionId);
      if (!exec) return state;

      const updatedSteps = [...exec.steps];
      updatedSteps[stepIndex] = {
        ...updatedSteps[stepIndex],
        status,
        result,
        error,
        ...(status === 'running' ? { startedAt: new Date().toISOString() } : {}),
        ...(status === 'completed' || status === 'failed'
          ? { completedAt: new Date().toISOString() }
          : {}),
      };

      newMap.set(executionId, {
        ...exec,
        steps: updatedSteps,
        currentStep: status === 'running' ? stepIndex : exec.currentStep,
        status: 'running',
      });

      return { executions: newMap };
    });
  },

  setActiveExecution: (executionId) => {
    set({ activeExecutionId: executionId });
  },

  completeExecution: (executionId, status) => {
    set((state) => {
      const newMap = new Map(state.executions);
      const exec = newMap.get(executionId);
      if (!exec) return state;

      newMap.set(executionId, { ...exec, status });
      return { executions: newMap };
    });
  },

  removeExecution: (executionId) => {
    set((state) => {
      const newMap = new Map(state.executions);
      newMap.delete(executionId);
      const activeId = state.activeExecutionId === executionId ? null : state.activeExecutionId;
      return { executions: newMap, activeExecutionId: activeId };
    });
  },

  showRecovery: (notification) => {
    set({ recoveryNotification: notification });
  },

  clearRecovery: () => {
    set({ recoveryNotification: null });
  },

  initWsListeners: () => {
    const unsubs: (() => void)[] = [];

    unsubs.push(
      wsClient.on('plan_ready', (msg) => {
        const steps: ExecutionStep[] = ((msg.steps as unknown[]) || []).map(
          (s: unknown, i: number) => {
            const step = s as Record<string, unknown>;
            return {
              index: i,
              name: (step.name as string) || `Step ${i + 1}`,
              agent: (step.agent as string) || '',
              action: (step.action as string) || '',
              status: 'pending' as StepStatus,
            };
          },
        );
        get().trackExecution(
          msg.execution_id as string,
          (msg.workflow_id as string) || '',
          steps,
        );
      }),
    );

    unsubs.push(
      wsClient.on('step_started', (msg) => {
        get().updateStep(
          msg.execution_id as string,
          msg.step_index as number,
          'running',
        );
      }),
    );

    unsubs.push(
      wsClient.on('step_complete', (msg) => {
        get().updateStep(
          msg.execution_id as string,
          msg.step_index as number,
          (msg.status as StepStatus) || 'completed',
          msg.result,
          msg.error as string | undefined,
        );
      }),
    );

    unsubs.push(
      wsClient.on('workflow_complete', (msg) => {
        get().completeExecution(
          msg.execution_id as string,
          (msg.status as 'completed' | 'failed') || 'completed',
        );
      }),
    );

    unsubs.push(
      wsClient.on('error', (msg) => {
        if (msg.execution_id) {
          get().completeExecution(msg.execution_id as string, 'failed');
        }
      }),
    );

    // Recovery dialog events (L5/L6 user confirmation)
    unsubs.push(
      wsClient.on('recovery', (msg) => {
        const notification: RecoveryNotification = {
          type: 'recovery',
          level: (msg.level as number) || 5,
          message: (msg.message as string) || 'Recovery in progress',
          execution_id: msg.execution_id as string,
          step_index: (msg.step_index as number) || 0,
          options: msg.options as string[] | undefined,
        };
        get().showRecovery(notification);
      }),
    );

    // Return cleanup function
    return () => unsubs.forEach((u) => u());
  },
}));
