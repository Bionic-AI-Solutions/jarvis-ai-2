/**
 * JARVIS AI — Sprint 7 Frontend Tests.
 *
 * Tests for: WorkflowList, WorkflowExecuteDialog, PauseResumeControls,
 *            WorkflowExport, RecoverySuggestions
 *
 * Stories: 4.1–4.7 (Workflow), 2.6 (Pause/Resume), 3.7 (Error Context),
 *          3.8 (AI Recovery Suggestions)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import WorkflowList from '../components/WorkflowList';
import WorkflowExecuteDialog from '../components/WorkflowExecuteDialog';
import PauseResumeControls from '../components/PauseResumeControls';
import WorkflowExport from '../components/WorkflowExport';
import RecoverySuggestions from '../components/RecoverySuggestions';
import type {
  WorkflowItem,
  WorkflowExecuteResponse,
  RecoverySuggestionResult,
} from '../types';

// ═══════════════════════════════════════════════════════════════
// Test Fixtures
// ═══════════════════════════════════════════════════════════════

const mockWorkflowRegular: WorkflowItem = {
  id: 'wf-001',
  name: 'Daily Report',
  description: 'Generates a daily status report',
  steps_json: JSON.stringify([
    { agent: 'data-collector', action: 'gather', parameters: { source: '{data_source}' } },
    { agent: 'report-gen', action: 'format', parameters: { output: '{output_dir}/report.pdf' } },
  ]),
  is_active: true,
  tags: 'automation,report',
  success_rate: 0.92,
  execution_count: 14,
  is_template: false,
  template_category: null,
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-15T00:00:00',
};

const mockWorkflowTemplate: WorkflowItem = {
  id: 'wf-tpl-001',
  name: 'Git Commit & Push',
  description: 'Stage, commit, and push changes',
  steps_json: JSON.stringify([
    { agent: 'git-agent', action: 'commit', parameters: { message: '{commit_message}' } },
  ]),
  is_active: true,
  tags: 'development,git',
  success_rate: 0.99,
  execution_count: 200,
  is_template: true,
  template_category: 'development',
  created_at: '2026-01-01T00:00:00',
  updated_at: '2026-01-01T00:00:00',
};

const mockWorkflowNoParams: WorkflowItem = {
  id: 'wf-002',
  name: 'Simple Task',
  description: null,
  steps_json: JSON.stringify([
    { agent: 'basic', action: 'run', parameters: { fixed: 'value' } },
  ]),
  is_active: true,
  tags: null,
  success_rate: 1.0,
  execution_count: 3,
  is_template: false,
  template_category: null,
  created_at: '2026-01-05T00:00:00',
  updated_at: '2026-01-05T00:00:00',
};

const mockExecuteResponse: WorkflowExecuteResponse = {
  execution_id: 'exec-777',
  workflow_id: 'wf-001',
  status: 'running',
  total_steps: 2,
};

const mockSuggestionResult: RecoverySuggestionResult = {
  diagnosis: 'Agent timed out due to high response latency',
  suggestions: [
    { action: 'increase_timeout', description: 'Increase the agent timeout to 60s', confidence: 0.85 },
    { action: 'retry', description: 'Retry the step with the same parameters', confidence: 0.6 },
    { action: 'skip', description: 'Skip this step and continue', confidence: 0.3 },
  ],
  can_auto_recover: true,
  auto_recovery_action: 'increase_timeout',
  generated_at: '2026-01-20T10:00:00Z',
  model_used: 'qwen2.5:3b',
};


// ═══════════════════════════════════════════════════════════════
// WorkflowList Tests
// ═══════════════════════════════════════════════════════════════

describe('WorkflowList', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/workflows/search')) {
        return new Response(JSON.stringify([mockWorkflowRegular]), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/workflows')) {
        return new Response(
          JSON.stringify([mockWorkflowRegular, mockWorkflowTemplate, mockWorkflowNoParams]),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response(null, { status: 404 });
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the workflow list container', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('workflow-list')).toBeInTheDocument();
    });
  });

  it('renders search form', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('workflow-search-form')).toBeInTheDocument();
      expect(screen.getByTestId('workflow-search-input')).toBeInTheDocument();
      expect(screen.getByTestId('workflow-search-btn')).toBeInTheDocument();
    });
  });

  it('renders workflow cards after loading', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByText('Daily Report')).toBeInTheDocument();
      expect(screen.getByText('Git Commit & Push')).toBeInTheDocument();
      expect(screen.getByText('Simple Task')).toBeInTheDocument();
    });
  });

  it('shows template badge on template workflows', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('template-badge')).toBeInTheDocument();
      expect(screen.getByText('Template')).toBeInTheDocument();
    });
  });

  it('shows description when available', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByText('Generates a daily status report')).toBeInTheDocument();
    });
  });

  it('shows execution stats', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByText(/14 runs/)).toBeInTheDocument();
      expect(screen.getByText(/92% success/)).toBeInTheDocument();
    });
  });

  it('shows tags as chips', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getAllByText('automation').length).toBeGreaterThanOrEqual(1);
      expect(screen.getAllByText('report').length).toBeGreaterThanOrEqual(1);
    });
  });

  it('renders templates-only toggle', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('workflow-templates-toggle')).toBeInTheDocument();
    });
  });

  it('shows execute button for non-template workflows', async () => {
    const onExecute = vi.fn();
    render(<WorkflowList onExecute={onExecute} />);
    await waitFor(() => {
      expect(screen.getByTestId('execute-btn-wf-001')).toBeInTheDocument();
    });
  });

  it('shows clone button for template workflows', async () => {
    const onClone = vi.fn();
    render(<WorkflowList onClone={onClone} />);
    await waitFor(() => {
      expect(screen.getByTestId('clone-btn-wf-tpl-001')).toBeInTheDocument();
    });
  });

  it('shows export button for all workflows', async () => {
    const onExport = vi.fn();
    render(<WorkflowList onExport={onExport} />);
    await waitFor(() => {
      const exportBtns = screen.getAllByText('Export');
      expect(exportBtns.length).toBe(3);
    });
  });

  it('calls onExecute when execute button clicked', async () => {
    const onExecute = vi.fn();
    render(<WorkflowList onExecute={onExecute} />);
    await waitFor(() => {
      fireEvent.click(screen.getByTestId('execute-btn-wf-001'));
    });
    expect(onExecute).toHaveBeenCalledWith(mockWorkflowRegular);
  });

  it('calls onClone when clone button clicked', async () => {
    const onClone = vi.fn();
    render(<WorkflowList onClone={onClone} />);
    await waitFor(() => {
      fireEvent.click(screen.getByTestId('clone-btn-wf-tpl-001'));
    });
    expect(onClone).toHaveBeenCalledWith(mockWorkflowTemplate);
  });

  it('calls search API when search form submitted', async () => {
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('workflow-search-input')).toBeInTheDocument();
    });

    const input = screen.getByTestId('workflow-search-input');
    fireEvent.change(input, { target: { value: 'report' } });
    fireEvent.submit(screen.getByTestId('workflow-search-form'));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/workflows/search'),
        expect.objectContaining({ method: 'POST' }),
      );
    });
  });

  it('shows empty state when no workflows', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify([]), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('workflow-empty')).toBeInTheDocument();
      expect(screen.getByText('No workflows found.')).toBeInTheDocument();
    });
  });

  it('shows error when fetch fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network error'));
    render(<WorkflowList />);
    await waitFor(() => {
      expect(screen.getByTestId('workflow-error')).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });
});


// ═══════════════════════════════════════════════════════════════
// WorkflowExecuteDialog Tests
// ═══════════════════════════════════════════════════════════════

describe('WorkflowExecuteDialog', () => {
  const mockOnClose = vi.fn();
  const mockOnExecuted = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockExecuteResponse), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders dialog with workflow name', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    expect(screen.getByTestId('execute-dialog')).toBeInTheDocument();
    expect(screen.getByText(/Execute: Daily Report/)).toBeInTheDocument();
  });

  it('detects parameters from steps_json', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    expect(screen.getByTestId('execute-params')).toBeInTheDocument();
    expect(screen.getByTestId('param-input-data_source')).toBeInTheDocument();
    expect(screen.getByTestId('param-input-output_dir')).toBeInTheDocument();
  });

  it('shows no-params message for parameterless workflows', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowNoParams} onClose={mockOnClose} />,
    );
    expect(screen.getByTestId('no-params-msg')).toBeInTheDocument();
    expect(screen.getByText(/no configurable parameters/)).toBeInTheDocument();
  });

  it('shows description when available', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    expect(screen.getByText('Generates a daily status report')).toBeInTheDocument();
  });

  it('has run and cancel buttons', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    expect(screen.getByTestId('execute-run-btn')).toBeInTheDocument();
    expect(screen.getByTestId('execute-cancel-btn')).toBeInTheDocument();
    expect(screen.getByText('Run Workflow')).toBeInTheDocument();
  });

  it('calls onClose when close button clicked', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    fireEvent.click(screen.getByTestId('execute-dialog-close'));
    expect(mockOnClose).toHaveBeenCalledOnce();
  });

  it('calls onClose when cancel button clicked', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    fireEvent.click(screen.getByTestId('execute-cancel-btn'));
    expect(mockOnClose).toHaveBeenCalledOnce();
  });

  it('calls execute API and fires onExecuted', async () => {
    render(
      <WorkflowExecuteDialog
        workflow={mockWorkflowRegular}
        onClose={mockOnClose}
        onExecuted={mockOnExecuted}
      />,
    );
    fireEvent.click(screen.getByTestId('execute-run-btn'));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/workflows/${mockWorkflowRegular.id}/execute`),
        expect.objectContaining({ method: 'POST' }),
      );
    });

    await waitFor(() => {
      expect(mockOnExecuted).toHaveBeenCalledWith(mockExecuteResponse);
      expect(mockOnClose).toHaveBeenCalled();
    });
  });

  it('updates parameter values on input change', () => {
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    const input = screen.getByTestId('param-input-data_source') as HTMLInputElement;
    fireEvent.change(input, { target: { value: 'my_database' } });
    expect(input.value).toBe('my_database');
  });

  it('shows error when API call fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ detail: 'Workflow not found' }), {
        status: 404,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    render(
      <WorkflowExecuteDialog workflow={mockWorkflowRegular} onClose={mockOnClose} />,
    );
    fireEvent.click(screen.getByTestId('execute-run-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('execute-error')).toBeInTheDocument();
      expect(screen.getByText('Workflow not found')).toBeInTheDocument();
    });
  });
});


// ═══════════════════════════════════════════════════════════════
// PauseResumeControls Tests
// ═══════════════════════════════════════════════════════════════

describe('PauseResumeControls', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/pause-status')) {
        return new Response(JSON.stringify({ paused: false }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/pause') || url.includes('/resume')) {
        return new Response(JSON.stringify({ status: 'ok' }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(null, { status: 404 });
    });
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders controls container', async () => {
    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('pause-resume-controls')).toBeInTheDocument();
    });
  });

  it('shows pause button when not paused', async () => {
    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('pause-btn')).toBeInTheDocument();
      expect(screen.getByText(/Pause/)).toBeInTheDocument();
    });
  });

  it('returns null when isRunning is false', () => {
    const { container } = render(
      <PauseResumeControls executionId="exec-1" isRunning={false} />,
    );
    expect(container.firstChild).toBeNull();
  });

  it('shows resume button after pause', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/pause-status')) {
        return new Response(JSON.stringify({ paused: true }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(JSON.stringify({ status: 'ok' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });

    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('resume-btn')).toBeInTheDocument();
      expect(screen.getByText(/Resume/)).toBeInTheDocument();
    });
  });

  it('shows auto-resume message when paused', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async () => {
      return new Response(JSON.stringify({ paused: true }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });

    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('pause-status')).toBeInTheDocument();
      expect(screen.getByText(/auto-resumes in 30 min/)).toBeInTheDocument();
    });
  });

  it('calls pause API when pause button clicked', async () => {
    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('pause-btn')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('pause-btn'));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/executions/exec-1/pause'),
        expect.objectContaining({ method: 'POST' }),
      );
    });
  });

  it('calls resume API when resume button clicked', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/pause-status')) {
        return new Response(JSON.stringify({ paused: true }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(JSON.stringify({ status: 'ok' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      });
    });

    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('resume-btn')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('resume-btn'));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/executions/exec-1/resume'),
        expect.objectContaining({ method: 'POST' }),
      );
    });
  });

  it('shows error when pause API fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/pause-status')) {
        return new Response(JSON.stringify({ paused: false }), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      return new Response(JSON.stringify({ detail: 'Already paused' }), {
        status: 400,
        headers: { 'Content-Type': 'application/json' },
      });
    });

    render(<PauseResumeControls executionId="exec-1" />);
    await waitFor(() => {
      expect(screen.getByTestId('pause-btn')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByTestId('pause-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('pause-error')).toBeInTheDocument();
      expect(screen.getByText('Already paused')).toBeInTheDocument();
    });
  });
});


// ═══════════════════════════════════════════════════════════════
// WorkflowExport Tests
// ═══════════════════════════════════════════════════════════════

describe('WorkflowExport', () => {
  const mockOnClose = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(
        JSON.stringify({
          workflow: { name: 'Test WF', steps: [] },
          format: 'json',
          exported_at: '2026-01-20T10:00:00Z',
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );
    // Mock URL.createObjectURL and URL.revokeObjectURL
    globalThis.URL.createObjectURL = vi.fn(() => 'blob:test-url');
    globalThis.URL.revokeObjectURL = vi.fn();
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders export container', () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    expect(screen.getByTestId('workflow-export')).toBeInTheDocument();
    expect(screen.getByText('Export Workflow')).toBeInTheDocument();
  });

  it('renders JSON and CSV radio buttons', () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    expect(screen.getByTestId('export-json-radio')).toBeInTheDocument();
    expect(screen.getByTestId('export-csv-radio')).toBeInTheDocument();
  });

  it('has JSON selected by default', () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    const jsonRadio = screen.getByTestId('export-json-radio') as HTMLInputElement;
    const csvRadio = screen.getByTestId('export-csv-radio') as HTMLInputElement;
    expect(jsonRadio.checked).toBe(true);
    expect(csvRadio.checked).toBe(false);
  });

  it('switches to CSV format on selection', () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    fireEvent.click(screen.getByTestId('export-csv-radio'));
    const csvRadio = screen.getByTestId('export-csv-radio') as HTMLInputElement;
    expect(csvRadio.checked).toBe(true);
    expect(screen.getByText('Download CSV')).toBeInTheDocument();
  });

  it('shows download button with correct format label', () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    expect(screen.getByTestId('export-download-btn')).toBeInTheDocument();
    expect(screen.getByText('Download JSON')).toBeInTheDocument();
  });

  it('shows cancel button when onClose provided', () => {
    render(
      <WorkflowExport
        workflowId="wf-001"
        workflowName="Daily Report"
        onClose={mockOnClose}
      />,
    );
    expect(screen.getByTestId('export-cancel-btn')).toBeInTheDocument();
  });

  it('does not show cancel button without onClose', () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    expect(screen.queryByTestId('export-cancel-btn')).not.toBeInTheDocument();
  });

  it('calls export API on download click', async () => {
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    fireEvent.click(screen.getByTestId('export-download-btn'));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/workflows/wf-001/export'),
        expect.objectContaining({ method: 'POST' }),
      );
    });
  });

  it('calls onClose when cancel button clicked', () => {
    render(
      <WorkflowExport
        workflowId="wf-001"
        workflowName="Daily Report"
        onClose={mockOnClose}
      />,
    );
    fireEvent.click(screen.getByTestId('export-cancel-btn'));
    expect(mockOnClose).toHaveBeenCalledOnce();
  });

  it('shows error when export fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(null, { status: 500 }),
    );
    render(
      <WorkflowExport workflowId="wf-001" workflowName="Daily Report" />,
    );
    fireEvent.click(screen.getByTestId('export-download-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('export-error')).toBeInTheDocument();
      expect(screen.getByText(/HTTP 500/)).toBeInTheDocument();
    });
  });
});


// ═══════════════════════════════════════════════════════════════
// RecoverySuggestions Tests
// ═══════════════════════════════════════════════════════════════

describe('RecoverySuggestions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockSuggestionResult), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders container', () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    expect(screen.getByTestId('recovery-suggestions')).toBeInTheDocument();
  });

  it('shows get suggestions button initially', () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    expect(screen.getByTestId('get-suggestions-btn')).toBeInTheDocument();
    expect(screen.getByText('Get AI Suggestions')).toBeInTheDocument();
  });

  it('shows loading state when fetching', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      () => new Promise(() => {}), // Never resolves
    );
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('suggestions-loading')).toBeInTheDocument();
      expect(screen.getByText(/Analyzing error context/)).toBeInTheDocument();
    });
  });

  it('displays diagnosis after fetching', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('suggestions-result')).toBeInTheDocument();
      expect(screen.getByText(/Agent timed out/)).toBeInTheDocument();
    });
  });

  it('shows auto-recover badge', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('auto-recover-badge')).toBeInTheDocument();
      expect(screen.getByText(/Can auto-recover/)).toBeInTheDocument();
      expect(screen.getByTestId('auto-recover-badge').textContent).toContain('increase_timeout');
    });
  });

  it('renders all suggestion items', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('suggestion-0')).toBeInTheDocument();
      expect(screen.getByTestId('suggestion-1')).toBeInTheDocument();
      expect(screen.getByTestId('suggestion-2')).toBeInTheDocument();
    });
  });

  it('displays suggestion actions and descriptions', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByText('increase_timeout')).toBeInTheDocument();
      expect(screen.getByText('Increase the agent timeout to 60s')).toBeInTheDocument();
      expect(screen.getByText('retry')).toBeInTheDocument();
      expect(screen.getByText('skip')).toBeInTheDocument();
    });
  });

  it('shows confidence percentages', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByText('85%')).toBeInTheDocument();
      expect(screen.getByText('60%')).toBeInTheDocument();
      expect(screen.getByText('30%')).toBeInTheDocument();
    });
  });

  it('shows model name in metadata', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByText(/qwen2\.5:3b/)).toBeInTheDocument();
    });
  });

  it('calls correct API endpoint', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(globalThis.fetch).toHaveBeenCalledWith(
        expect.stringContaining(
          '/api/executions/exec-1/context-snapshots/snap-1/suggestions',
        ),
        expect.objectContaining({ method: 'POST' }),
      );
    });
  });

  it('hides get-suggestions button after results load', async () => {
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.queryByTestId('get-suggestions-btn')).not.toBeInTheDocument();
    });
  });

  it('shows error on fetch failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Network error'));
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('suggestions-error')).toBeInTheDocument();
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('does not show auto-recover badge when cannot auto-recover', async () => {
    const noAutoResult = { ...mockSuggestionResult, can_auto_recover: false };
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(noAutoResult), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
    render(
      <RecoverySuggestions executionId="exec-1" snapshotId="snap-1" />,
    );
    fireEvent.click(screen.getByTestId('get-suggestions-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('suggestions-result')).toBeInTheDocument();
      expect(screen.queryByTestId('auto-recover-badge')).not.toBeInTheDocument();
    });
  });
});
