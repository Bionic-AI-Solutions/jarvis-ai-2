/**
 * AuditLogViewer — Display audit trail entries with hash-chain verification.
 *
 * Sprint 8 Story 5.5: Audit Logging (UI)
 */

import React, { useState, useEffect, useCallback } from 'react';
import type { AuditEntry, AuditVerifyResult } from '../types';

const BACKEND_URL = 'http://localhost:9000';

interface AuditLogViewerProps {
  /** Auto-refresh interval in seconds (0 = disabled) */
  refreshInterval?: number;
}

const AuditLogViewer: React.FC<AuditLogViewerProps> = ({
  refreshInterval = 0,
}) => {
  const [entries, setEntries] = useState<AuditEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [verifyResult, setVerifyResult] = useState<AuditVerifyResult | null>(null);
  const [verifying, setVerifying] = useState(false);

  // Filters
  const [filterActor, setFilterActor] = useState('');
  const [filterAction, setFilterAction] = useState('');
  const [page, setPage] = useState(0);
  const limit = 20;

  const fetchEntries = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const params = new URLSearchParams();
      params.set('limit', String(limit));
      params.set('offset', String(page * limit));
      if (filterActor) params.set('actor', filterActor);
      if (filterAction) params.set('action', filterAction);

      const res = await fetch(`${BACKEND_URL}/api/audit?${params}`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();
      setEntries(data.entries ?? []);
      setTotal(data.total ?? 0);
    } catch (e: any) {
      setError(e.message || 'Failed to load audit entries.');
    } finally {
      setLoading(false);
    }
  }, [page, filterActor, filterAction]);

  useEffect(() => {
    fetchEntries();
  }, [fetchEntries]);

  useEffect(() => {
    if (refreshInterval > 0) {
      const interval = setInterval(fetchEntries, refreshInterval * 1000);
      return () => clearInterval(interval);
    }
  }, [refreshInterval, fetchEntries]);

  const handleVerify = useCallback(async () => {
    setVerifying(true);
    setVerifyResult(null);
    try {
      const res = await fetch(`${BACKEND_URL}/api/audit/verify`);
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data: AuditVerifyResult = await res.json();
      setVerifyResult(data);
    } catch (e: any) {
      setVerifyResult({ valid: false, entries_checked: 0, first_broken_id: null, message: e.message });
    } finally {
      setVerifying(false);
    }
  }, []);

  const totalPages = Math.ceil(total / limit);

  return (
    <div className="audit-log-viewer" data-testid="audit-log-viewer">
      <div className="audit-header">
        <h3>Audit Trail</h3>
        <button
          className="audit-verify-btn"
          onClick={handleVerify}
          disabled={verifying}
          data-testid="verify-chain-btn"
        >
          {verifying ? 'Verifying…' : 'Verify Hash Chain'}
        </button>
      </div>

      {verifyResult && (
        <div
          className={`audit-verify-result ${verifyResult.valid ? 'valid' : 'invalid'}`}
          data-testid="verify-result"
        >
          <span className="audit-verify-icon">{verifyResult.valid ? '✅' : '❌'}</span>
          <span>{verifyResult.message}</span>
          <span className="audit-verify-count">({verifyResult.entries_checked} entries checked)</span>
        </div>
      )}

      <div className="audit-filters">
        <input
          type="text"
          placeholder="Filter by actor…"
          value={filterActor}
          onChange={(e) => { setFilterActor(e.target.value); setPage(0); }}
          className="audit-filter-input"
          data-testid="filter-actor"
        />
        <input
          type="text"
          placeholder="Filter by action…"
          value={filterAction}
          onChange={(e) => { setFilterAction(e.target.value); setPage(0); }}
          className="audit-filter-input"
          data-testid="filter-action"
        />
      </div>

      {error && <p className="audit-error" data-testid="audit-error">{error}</p>}

      {loading ? (
        <p className="audit-loading">Loading…</p>
      ) : entries.length === 0 ? (
        <p className="audit-empty" data-testid="audit-empty">No audit entries found.</p>
      ) : (
        <table className="audit-table" data-testid="audit-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Actor</th>
              <th>Action</th>
              <th>Resource</th>
              <th>Result</th>
              <th>Hash</th>
            </tr>
          </thead>
          <tbody>
            {entries.map((entry) => (
              <tr key={entry.id} data-testid="audit-row">
                <td>{new Date(entry.timestamp).toLocaleString()}</td>
                <td>{entry.actor}</td>
                <td>{entry.action}</td>
                <td>{entry.resource_type ? `${entry.resource_type}/${entry.resource_id ?? ''}` : '—'}</td>
                <td>
                  <span className={`audit-result-badge ${entry.result}`}>
                    {entry.result}
                  </span>
                </td>
                <td className="audit-hash" title={entry.entry_hash}>
                  {entry.entry_hash.substring(0, 8)}…
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}

      {totalPages > 1 && (
        <div className="audit-pagination" data-testid="audit-pagination">
          <button disabled={page === 0} onClick={() => setPage(page - 1)}>← Prev</button>
          <span>Page {page + 1} of {totalPages}</span>
          <button disabled={page >= totalPages - 1} onClick={() => setPage(page + 1)}>Next →</button>
        </div>
      )}
    </div>
  );
};

export default AuditLogViewer;
