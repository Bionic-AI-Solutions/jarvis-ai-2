/**
 * WorkflowExport — export a workflow as JSON or CSV.
 * Sprint 7 Story 4.7: Export Workflows.
 */
import React, { useState } from 'react';
import type { WorkflowExportFormat } from '../types';

interface WorkflowExportProps {
  workflowId: string;
  workflowName: string;
  apiBase?: string;
  onClose?: () => void;
}

const WorkflowExport: React.FC<WorkflowExportProps> = ({
  workflowId,
  workflowName,
  apiBase = 'http://localhost:9000',
  onClose,
}) => {
  const [format, setFormat] = useState<WorkflowExportFormat>('json');
  const [exporting, setExporting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleExport = async () => {
    setExporting(true);
    setError(null);
    try {
      const resp = await fetch(`${apiBase}/api/workflows/${workflowId}/export`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ format }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data = await resp.json();

      // Trigger download
      const content =
        format === 'json'
          ? JSON.stringify(data.workflow, null, 2)
          : data.workflow; // CSV is already a string
      const blob = new Blob([content], {
        type: format === 'json' ? 'application/json' : 'text/csv',
      });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${workflowName.replace(/\s+/g, '_')}.${format}`;
      a.click();
      URL.revokeObjectURL(url);

      onClose?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setExporting(false);
    }
  };

  return (
    <div className="workflow-export" data-testid="workflow-export">
      <h3>Export Workflow</h3>
      <div className="export-format-selector">
        <label>
          <input
            type="radio"
            name="exportFormat"
            value="json"
            checked={format === 'json'}
            onChange={() => setFormat('json')}
            data-testid="export-json-radio"
          />
          JSON
        </label>
        <label>
          <input
            type="radio"
            name="exportFormat"
            value="csv"
            checked={format === 'csv'}
            onChange={() => setFormat('csv')}
            data-testid="export-csv-radio"
          />
          CSV
        </label>
      </div>

      {error && (
        <div className="export-error" data-testid="export-error" role="alert">
          {error}
        </div>
      )}

      <div className="export-actions">
        {onClose && (
          <button className="btn btn-ghost btn-sm" onClick={onClose} data-testid="export-cancel-btn">
            Cancel
          </button>
        )}
        <button
          className="btn btn-primary btn-sm"
          onClick={handleExport}
          disabled={exporting}
          data-testid="export-download-btn"
        >
          {exporting ? 'Exporting…' : `Download ${format.toUpperCase()}`}
        </button>
      </div>
    </div>
  );
};

export default WorkflowExport;
