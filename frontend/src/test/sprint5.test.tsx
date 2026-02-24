/**
 * JARVIS AI — Sprint 5 Frontend Tests.
 *
 * Tests for: ExecutionTimeline, StepConfidence, FallbackTextInput
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { ExecutionTimeline } from '../components/ExecutionTimeline';
import { StepConfidence, calculateConfidence } from '../components/StepConfidence';
import { FallbackTextInput } from '../components/FallbackTextInput';
import { useExecutionStore } from '../stores/executionStore';
import type { StepStatus } from '../types';

// ── ExecutionTimeline ──────────────────────────────────

describe('ExecutionTimeline', () => {
  beforeEach(() => {
    useExecutionStore.setState({
      executions: new Map(),
      activeExecutionId: null,
    });
  });

  it('shows empty state when no execution', () => {
    render(<ExecutionTimeline />);
    expect(screen.getByTestId('timeline-empty')).toBeInTheDocument();
  });

  it('renders timeline nodes for active execution', () => {
    const steps = [
      { index: 0, name: 'Plan', agent: 'planner', action: 'plan', status: 'completed' as StepStatus, startedAt: '2024-01-01T00:00:00Z', completedAt: '2024-01-01T00:00:02Z' },
      { index: 1, name: 'Execute', agent: 'executor', action: 'exec', status: 'running' as StepStatus, startedAt: '2024-01-01T00:00:02Z' },
      { index: 2, name: 'Verify', agent: 'verifier', action: 'verify', status: 'pending' as StepStatus },
    ];

    const execMap = new Map();
    execMap.set('exec-t1', {
      executionId: 'exec-t1',
      workflowId: 'wf-t1',
      steps,
      currentStep: 1,
      totalSteps: 3,
      status: 'running',
      startedAt: '2024-01-01T00:00:00Z',
    });

    useExecutionStore.setState({ executions: execMap, activeExecutionId: 'exec-t1' });

    render(<ExecutionTimeline />);

    expect(screen.getByTestId('execution-timeline')).toBeInTheDocument();
    expect(screen.getByText('Plan')).toBeInTheDocument();
    expect(screen.getByText('Execute')).toBeInTheDocument();
    expect(screen.getByText('Verify')).toBeInTheDocument();
  });

  it('expands timeline node on click', () => {
    const steps = [
      { index: 0, name: 'Analyze', agent: 'analyzer', action: 'analyze', status: 'completed' as StepStatus, startedAt: '2024-01-01T00:00:00Z', completedAt: '2024-01-01T00:00:05Z' },
    ];

    const execMap = new Map();
    execMap.set('exec-t2', {
      executionId: 'exec-t2',
      workflowId: 'wf-t2',
      steps,
      currentStep: 0,
      totalSteps: 1,
      status: 'completed',
      startedAt: '2024-01-01T00:00:00Z',
    });

    useExecutionStore.setState({ executions: execMap, activeExecutionId: 'exec-t2' });

    render(<ExecutionTimeline />);
    fireEvent.click(screen.getByText('Analyze'));

    // After clicking, the details should show action
    expect(screen.getByText('analyze')).toBeInTheDocument();
  });
});

// ── StepConfidence ─────────────────────────────────────

describe('StepConfidence', () => {
  it('renders high confidence badge (>= 90%)', () => {
    render(<StepConfidence confidence={0.95} stepIndex={0} />);
    expect(screen.getByText('Confidence: 95%')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('renders medium confidence badge (70-89%)', () => {
    render(<StepConfidence confidence={0.78} stepIndex={1} />);
    expect(screen.getByText('Confidence: 78%')).toBeInTheDocument();
    expect(screen.getByText('Medium')).toBeInTheDocument();
  });

  it('renders low confidence badge (< 70%)', () => {
    render(<StepConfidence confidence={0.55} stepIndex={2} />);
    expect(screen.getByText('Confidence: 55%')).toBeInTheDocument();
    expect(screen.getByText('Low')).toBeInTheDocument();
  });

  it('shows tooltip on hover with sources', () => {
    const sources = [
      { name: 'Moondream', value: 0.80, description: 'Detected button' },
      { name: 'System', value: 0.95, description: 'Click verified' },
    ];

    render(<StepConfidence confidence={0.87} stepIndex={3} sources={sources} />);

    const badge = screen.getByTestId('step-confidence-3');
    fireEvent.mouseEnter(badge);

    expect(screen.getByTestId('confidence-tooltip')).toBeInTheDocument();
    expect(screen.getByText('Moondream')).toBeInTheDocument();
    expect(screen.getByText('80%')).toBeInTheDocument();
  });

  it('hides tooltip on mouse leave', () => {
    const sources = [{ name: 'Test', value: 0.90 }];
    render(<StepConfidence confidence={0.90} stepIndex={4} sources={sources} />);

    const badge = screen.getByTestId('step-confidence-4');
    fireEvent.mouseEnter(badge);
    expect(screen.getByTestId('confidence-tooltip')).toBeInTheDocument();

    fireEvent.mouseLeave(badge);
    expect(screen.queryByTestId('confidence-tooltip')).not.toBeInTheDocument();
  });
});

describe('calculateConfidence', () => {
  it('returns average of sources', () => {
    const sources = [
      { name: 'A', value: 0.80 },
      { name: 'B', value: 0.90 },
    ];
    expect(calculateConfidence(sources)).toBeCloseTo(0.85);
  });

  it('returns 0 for empty sources', () => {
    expect(calculateConfidence([])).toBe(0);
  });
});

// ── FallbackTextInput ──────────────────────────────────

describe('FallbackTextInput', () => {
  it('renders text input', () => {
    render(<FallbackTextInput />);
    expect(screen.getByTestId('fallback-input')).toBeInTheDocument();
    expect(screen.getByTestId('fallback-send-btn')).toBeInTheDocument();
  });

  it('shows voice active indicator', () => {
    render(<FallbackTextInput voiceActive={true} />);
    expect(screen.getByText(/Voice active/)).toBeInTheDocument();
  });

  it('calls onSubmit with typed source', () => {
    const onSubmit = vi.fn();
    render(<FallbackTextInput onSubmit={onSubmit} />);

    const input = screen.getByTestId('fallback-input');
    fireEvent.change(input, { target: { value: 'test message' } });
    fireEvent.click(screen.getByTestId('fallback-send-btn'));

    expect(onSubmit).toHaveBeenCalledWith('test message', 'typed');
  });

  it('disables send button when input is empty', () => {
    render(<FallbackTextInput />);
    const btn = screen.getByTestId('fallback-send-btn');
    expect(btn).toBeDisabled();
  });

  it('handles Enter key to submit', () => {
    const onSubmit = vi.fn();
    render(<FallbackTextInput onSubmit={onSubmit} />);

    const input = screen.getByTestId('fallback-input');
    fireEvent.change(input, { target: { value: 'enter test' } });
    fireEvent.keyDown(input, { key: 'Enter', shiftKey: false });

    expect(onSubmit).toHaveBeenCalledWith('enter test', 'typed');
  });
});
