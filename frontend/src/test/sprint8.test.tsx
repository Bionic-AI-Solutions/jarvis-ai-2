/**
 * JARVIS AI — Sprint 8 Frontend Tests.
 *
 * Tests for: LockScreen, PassphraseStrengthMeter, AuditLogViewer, PatternSuggestion
 *
 * Stories: 5.1–5.7 (Security Hardening), 6.1–6.3 (Learning Engine)
 */

import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import LockScreen from '../components/LockScreen';
import PassphraseStrengthMeter from '../components/PassphraseStrengthMeter';
import AuditLogViewer from '../components/AuditLogViewer';
import PatternSuggestion from '../components/PatternSuggestion';
import type {
  AuditEntry,
  AuditVerifyResult,
  ExecutionPattern,
  PassphraseStrength,
} from '../types';

// ═══════════════════════════════════════════════════════════════
// Test Fixtures
// ═══════════════════════════════════════════════════════════════

const mockAuditEntries: AuditEntry[] = [
  {
    id: 'aud-001',
    actor: 'system',
    action: 'login',
    resource_type: 'user',
    resource_id: 'u-001',
    detail: 'Successful login',
    ip_address: '127.0.0.1',
    result: 'success',
    entry_hash: 'abc123def456abc123def456abc123de',
    prev_hash: null,
    timestamp: '2026-02-01T10:00:00',
  },
  {
    id: 'aud-002',
    actor: 'admin',
    action: 'update_config',
    resource_type: 'config',
    resource_id: 'cfg-1',
    detail: 'Changed timeout',
    ip_address: '192.168.1.10',
    result: 'success',
    entry_hash: 'def789ghi012def789ghi012def789gh',
    prev_hash: 'abc123def456abc123def456abc123de',
    timestamp: '2026-02-01T11:30:00',
  },
];

const mockVerifyResult: AuditVerifyResult = {
  valid: true,
  entries_checked: 42,
  first_broken_id: null,
  message: 'All 42 entries verified.',
};

const mockVerifyBroken: AuditVerifyResult = {
  valid: false,
  entries_checked: 10,
  first_broken_id: 'aud-005',
  message: 'Chain broken at entry aud-005.',
};

const mockPatterns: ExecutionPattern[] = [
  {
    id: 'pat-001',
    pattern_hash: 'hash1',
    intent: 'Deploy Backend',
    steps: [
      { agent: 'build-agent', action: 'compile' },
      { agent: 'deploy-agent', action: 'push' },
    ],
    frequency: 8,
    success_rate: 0.95,
    confidence: 0.76,
    suggested: true,
    accepted: false,
    last_seen: '2026-02-10T14:00:00',
  },
  {
    id: 'pat-002',
    pattern_hash: 'hash2',
    intent: 'Run Tests',
    steps: [
      { agent: 'test-runner', action: 'execute' },
    ],
    frequency: 15,
    success_rate: 0.88,
    confidence: 0.92,
    suggested: true,
    accepted: false,
    last_seen: '2026-02-10T15:00:00',
  },
];

const mockStrengthWeak: PassphraseStrength = {
  strong: false,
  score: 0,
  feedback: ['Add uppercase letters', 'Add a digit', 'Add a special character'],
};

const mockStrengthStrong: PassphraseStrength = {
  strong: true,
  score: 4,
  feedback: [],
};

// ═══════════════════════════════════════════════════════════════
// LockScreen Tests
// ═══════════════════════════════════════════════════════════════

describe('LockScreen', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders nothing when not locked', () => {
    const { container } = render(
      <LockScreen isLocked={false} hasPassphrase={true} />,
    );
    expect(container.innerHTML).toBe('');
  });

  it('renders overlay when locked', () => {
    render(<LockScreen isLocked={true} hasPassphrase={true} />);
    expect(screen.getByTestId('lock-screen')).toBeInTheDocument();
    expect(screen.getByText('System Locked')).toBeInTheDocument();
  });

  it('shows passphrase input when hasPassphrase is true', () => {
    render(<LockScreen isLocked={true} hasPassphrase={true} />);
    expect(screen.getByTestId('lock-passphrase-input')).toBeInTheDocument();
    expect(screen.getByTestId('lock-unlock-btn')).toBeInTheDocument();
  });

  it('shows hint when no passphrase configured', () => {
    render(<LockScreen isLocked={true} hasPassphrase={false} />);
    expect(screen.getByText(/No passphrase configured/)).toBeInTheDocument();
    expect(screen.queryByTestId('lock-passphrase-input')).toBeNull();
  });

  it('shows error when submitting empty passphrase', async () => {
    render(<LockScreen isLocked={true} hasPassphrase={true} />);
    fireEvent.click(screen.getByTestId('lock-unlock-btn'));
    await waitFor(() => {
      expect(screen.getByTestId('lock-error')).toHaveTextContent('Please enter your passphrase.');
    });
  });

  it('calls onUnlocked on successful unlock', async () => {
    const onUnlocked = vi.fn();
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true, token: 'jwt-123' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    render(
      <LockScreen isLocked={true} hasPassphrase={true} onUnlocked={onUnlocked} />,
    );
    const input = screen.getByTestId('lock-passphrase-input');
    fireEvent.change(input, { target: { value: 'mySecretPass1!' } });
    fireEvent.click(screen.getByTestId('lock-unlock-btn'));

    await waitFor(() => {
      expect(onUnlocked).toHaveBeenCalledWith('jwt-123');
    });
  });

  it('shows error and attempts remaining on failed unlock', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          ok: false,
          message: 'Incorrect passphrase.',
          attempts_remaining: 2,
          locked_out: false,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );

    render(<LockScreen isLocked={true} hasPassphrase={true} />);
    fireEvent.change(screen.getByTestId('lock-passphrase-input'), {
      target: { value: 'wrong' },
    });
    fireEvent.click(screen.getByTestId('lock-unlock-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('lock-error')).toHaveTextContent('Incorrect passphrase.');
      expect(screen.getByText(/2 attempts remaining/)).toBeInTheDocument();
    });
  });

  it('shows lockout message when locked out', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(
        JSON.stringify({
          ok: false,
          message: 'Too many attempts.',
          attempts_remaining: 0,
          locked_out: true,
          lockout_remaining_seconds: 60,
        }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      ),
    );

    render(<LockScreen isLocked={true} hasPassphrase={true} />);
    fireEvent.change(screen.getByTestId('lock-passphrase-input'), {
      target: { value: 'wrong' },
    });
    fireEvent.click(screen.getByTestId('lock-unlock-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('lock-lockout')).toHaveTextContent('Locked out for 60s');
    });
  });

  it('shows network error when fetch fails', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValueOnce(new Error('Network error'));

    render(<LockScreen isLocked={true} hasPassphrase={true} />);
    fireEvent.change(screen.getByTestId('lock-passphrase-input'), {
      target: { value: 'test' },
    });
    fireEvent.click(screen.getByTestId('lock-unlock-btn'));

    await waitFor(() => {
      expect(screen.getByTestId('lock-error')).toHaveTextContent('Unable to reach the backend.');
    });
  });

  it('handles Enter key to unlock', async () => {
    const onUnlocked = vi.fn();
    vi.spyOn(globalThis, 'fetch').mockResolvedValueOnce(
      new Response(JSON.stringify({ ok: true, token: 'jwt-key' }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    render(
      <LockScreen isLocked={true} hasPassphrase={true} onUnlocked={onUnlocked} />,
    );
    const input = screen.getByTestId('lock-passphrase-input');
    fireEvent.change(input, { target: { value: 'Str0ng!Pass' } });
    fireEvent.keyDown(input, { key: 'Enter' });

    await waitFor(() => {
      expect(onUnlocked).toHaveBeenCalledWith('jwt-key');
    });
  });
});

// ═══════════════════════════════════════════════════════════════
// PassphraseStrengthMeter Tests
// ═══════════════════════════════════════════════════════════════

describe('PassphraseStrengthMeter', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.useFakeTimers();
  });
  afterEach(() => {
    vi.useRealTimers();
    vi.restoreAllMocks();
  });

  it('renders nothing when passphrase is empty', () => {
    const { container } = render(<PassphraseStrengthMeter passphrase="" />);
    expect(container.innerHTML).toBe('');
  });

  it('renders container when passphrase is provided', () => {
    render(<PassphraseStrengthMeter passphrase="a" debounceMs={0} />);
    expect(screen.getByTestId('passphrase-strength')).toBeInTheDocument();
  });

  it('shows Checking… during API call', async () => {
    let resolvePromise!: (value: Response) => void;
    vi.spyOn(globalThis, 'fetch').mockImplementation(
      () => new Promise((resolve) => { resolvePromise = resolve; }),
    );

    render(<PassphraseStrengthMeter passphrase="test" debounceMs={100} />);
    await act(async () => {
      vi.advanceTimersByTime(100);
    });

    expect(screen.getByText('Checking…')).toBeInTheDocument();
    // resolve to prevent hanging
    resolvePromise(
      new Response(JSON.stringify(mockStrengthWeak), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );
  });

  it('displays Weak label with feedback for weak passphrase', async () => {
    vi.useRealTimers();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockStrengthWeak), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    render(<PassphraseStrengthMeter passphrase="weak" debounceMs={0} />);

    await waitFor(() => {
      expect(screen.getByTestId('strength-label')).toHaveTextContent('Weak');
      expect(screen.getByTestId('strength-feedback')).toBeInTheDocument();
      expect(screen.getByText('Add uppercase letters')).toBeInTheDocument();
    });
  });

  it('displays Strong label with no feedback', async () => {
    vi.useRealTimers();
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockStrengthStrong), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    render(<PassphraseStrengthMeter passphrase="Str0ng!Pass123" debounceMs={0} />);

    await waitFor(() => {
      expect(screen.getByTestId('strength-label')).toHaveTextContent('Strong');
      expect(screen.queryByTestId('strength-feedback')).toBeNull();
    });
  });

  it('debounces API calls', async () => {
    const fetchSpy = vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify(mockStrengthWeak), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const { rerender } = render(
      <PassphraseStrengthMeter passphrase="a" debounceMs={300} />,
    );

    // Rerender before debounce fires
    await act(async () => {
      vi.advanceTimersByTime(100);
    });
    rerender(<PassphraseStrengthMeter passphrase="ab" debounceMs={300} />);
    await act(async () => {
      vi.advanceTimersByTime(100);
    });
    rerender(<PassphraseStrengthMeter passphrase="abc" debounceMs={300} />);
    await act(async () => {
      vi.advanceTimersByTime(300);
    });

    // Should only have been called once (for the final "abc" value)
    expect(fetchSpy).toHaveBeenCalledTimes(1);
  });
});

// ═══════════════════════════════════════════════════════════════
// AuditLogViewer Tests
// ═══════════════════════════════════════════════════════════════

describe('AuditLogViewer', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/audit/verify')) {
        return new Response(JSON.stringify(mockVerifyResult), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/audit')) {
        return new Response(
          JSON.stringify({ entries: mockAuditEntries, total: 2 }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response(null, { status: 404 });
    });
  });
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('renders the viewer container', async () => {
    render(<AuditLogViewer />);
    await waitFor(() => {
      expect(screen.getByTestId('audit-log-viewer')).toBeInTheDocument();
    });
  });

  it('renders title and verify button', async () => {
    render(<AuditLogViewer />);
    await waitFor(() => {
      expect(screen.getByText('Audit Trail')).toBeInTheDocument();
      expect(screen.getByTestId('verify-chain-btn')).toBeInTheDocument();
    });
  });

  it('loads and displays audit entries', async () => {
    render(<AuditLogViewer />);
    await waitFor(() => {
      expect(screen.getByTestId('audit-table')).toBeInTheDocument();
      expect(screen.getAllByTestId('audit-row')).toHaveLength(2);
      expect(screen.getByText('system')).toBeInTheDocument();
      expect(screen.getByText('login')).toBeInTheDocument();
      expect(screen.getByText('admin')).toBeInTheDocument();
      expect(screen.getByText('update_config')).toBeInTheDocument();
    });
  });

  it('renders filter inputs', async () => {
    render(<AuditLogViewer />);
    await waitFor(() => {
      expect(screen.getByTestId('filter-actor')).toBeInTheDocument();
      expect(screen.getByTestId('filter-action')).toBeInTheDocument();
    });
  });

  it('shows verify result with valid chain', async () => {
    render(<AuditLogViewer />);
    await waitFor(() => expect(screen.getByTestId('verify-chain-btn')).toBeInTheDocument());

    fireEvent.click(screen.getByTestId('verify-chain-btn'));

    await waitFor(() => {
      const result = screen.getByTestId('verify-result');
      expect(result).toBeInTheDocument();
      expect(result).toHaveTextContent('All 42 entries verified');
      expect(result).toHaveTextContent('42 entries checked');
      expect(result.querySelector('.audit-verify-icon')?.textContent).toBe('✅');
    });
  });

  it('shows verify result with broken chain', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/audit/verify')) {
        return new Response(JSON.stringify(mockVerifyBroken), {
          status: 200,
          headers: { 'Content-Type': 'application/json' },
        });
      }
      if (url.includes('/api/audit')) {
        return new Response(
          JSON.stringify({ entries: mockAuditEntries, total: 2 }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      return new Response(null, { status: 404 });
    });

    render(<AuditLogViewer />);
    await waitFor(() => expect(screen.getByTestId('verify-chain-btn')).toBeInTheDocument());
    fireEvent.click(screen.getByTestId('verify-chain-btn'));

    await waitFor(() => {
      const result = screen.getByTestId('verify-result');
      expect(result).toHaveClass('invalid');
      expect(result.querySelector('.audit-verify-icon')?.textContent).toBe('❌');
      expect(result).toHaveTextContent('Chain broken');
    });
  });

  it('shows empty state when no entries', async () => {
    vi.spyOn(globalThis, 'fetch').mockImplementation(async () => {
      return new Response(
        JSON.stringify({ entries: [], total: 0 }),
        { status: 200, headers: { 'Content-Type': 'application/json' } },
      );
    });

    render(<AuditLogViewer />);
    await waitFor(() => {
      expect(screen.getByTestId('audit-empty')).toHaveTextContent('No audit entries found.');
    });
  });

  it('shows error state on fetch failure', async () => {
    vi.spyOn(globalThis, 'fetch').mockRejectedValue(new Error('Server down'));

    render(<AuditLogViewer />);
    await waitFor(() => {
      expect(screen.getByTestId('audit-error')).toBeInTheDocument();
    });
  });

  it('renders hash column with truncated hashes', async () => {
    render(<AuditLogViewer />);
    await waitFor(() => {
      // Each hash is truncated to 8 chars followed by …
      const hashCells = screen.getByTestId('audit-table').querySelectorAll('.audit-hash');
      expect(hashCells.length).toBe(2);
      expect(hashCells[0].textContent).toBe('abc123de…');
    });
  });
});

// ═══════════════════════════════════════════════════════════════
// PatternSuggestion Tests
// ═══════════════════════════════════════════════════════════════

describe('PatternSuggestion', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.spyOn(globalThis, 'fetch').mockImplementation(async (input: RequestInfo | URL) => {
      const url = typeof input === 'string' ? input : input.toString();
      if (url.includes('/api/learning/suggestions') && !url.includes('/accept') && !url.includes('/dismiss')) {
        return new Response(
          JSON.stringify({ suggestions: mockPatterns }),
          { status: 200, headers: { 'Content-Type': 'application/json' } },
        );
      }
      if (url.includes('/accept') || url.includes('/dismiss')) {
        return new Response(JSON.stringify({ ok: true }), {
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

  it('renders suggestions container', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      expect(screen.getByTestId('pattern-suggestions')).toBeInTheDocument();
    });
  });

  it('renders title', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      expect(screen.getByText('Suggested Workflows')).toBeInTheDocument();
    });
  });

  it('renders suggestion cards with correct data', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      const cards = screen.getAllByTestId('suggestion-card');
      expect(cards).toHaveLength(2);

      expect(screen.getByText('Deploy Backend')).toBeInTheDocument();
      expect(screen.getByText('Run Tests')).toBeInTheDocument();
    });
  });

  it('shows confidence percentage', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      const confidences = screen.getAllByTestId('suggestion-confidence');
      expect(confidences[0]).toHaveTextContent('76%');
      expect(confidences[1]).toHaveTextContent('92%');
    });
  });

  it('shows step chips (agent: action)', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      expect(screen.getByText('build-agent: compile')).toBeInTheDocument();
      expect(screen.getByText('deploy-agent: push')).toBeInTheDocument();
      expect(screen.getByText('test-runner: execute')).toBeInTheDocument();
    });
  });

  it('shows frequency and success rate meta', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      expect(screen.getByText(/Seen 8×/)).toBeInTheDocument();
      expect(screen.getByText(/95% success/)).toBeInTheDocument();
      expect(screen.getByText(/Seen 15×/)).toBeInTheDocument();
    });
  });

  it('renders accept and dismiss buttons', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      const acceptBtns = screen.getAllByTestId('accept-suggestion-btn');
      const dismissBtns = screen.getAllByTestId('dismiss-suggestion-btn');
      expect(acceptBtns).toHaveLength(2);
      expect(dismissBtns).toHaveLength(2);
    });
  });

  it('removes card on accept', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      expect(screen.getAllByTestId('suggestion-card')).toHaveLength(2);
    });

    const acceptBtns = screen.getAllByTestId('accept-suggestion-btn');
    fireEvent.click(acceptBtns[0]);

    await waitFor(() => {
      expect(screen.getAllByTestId('suggestion-card')).toHaveLength(1);
      expect(screen.queryByText('Deploy Backend')).toBeNull();
      expect(screen.getByText('Run Tests')).toBeInTheDocument();
    });
  });

  it('removes card on dismiss', async () => {
    render(<PatternSuggestion refreshInterval={0} />);
    await waitFor(() => {
      expect(screen.getAllByTestId('suggestion-card')).toHaveLength(2);
    });

    const dismissBtns = screen.getAllByTestId('dismiss-suggestion-btn');
    fireEvent.click(dismissBtns[1]); // Dismiss the second one (Run Tests)

    await waitFor(() => {
      expect(screen.getAllByTestId('suggestion-card')).toHaveLength(1);
      expect(screen.getByText('Deploy Backend')).toBeInTheDocument();
      expect(screen.queryByText('Run Tests')).toBeNull();
    });
  });

  it('renders nothing when no suggestions', async () => {
    vi.spyOn(globalThis, 'fetch').mockResolvedValue(
      new Response(JSON.stringify({ suggestions: [] }), {
        status: 200,
        headers: { 'Content-Type': 'application/json' },
      }),
    );

    const { container } = render(<PatternSuggestion refreshInterval={0} />);
    // Wait for the fetch to complete and component to update
    await waitFor(() => {
      expect(container.querySelector('[data-testid="pattern-suggestions"]')).toBeNull();
    });
  });
});
