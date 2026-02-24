/**
 * WorkflowList — displays workflows with search, tag filtering, and actions.
 * Sprint 7 Story 4.4 (Tags & Search), Story 4.5 (Templates).
 */
import React, { useCallback, useEffect, useState } from 'react';
import type { WorkflowItem } from '../types';

interface WorkflowListProps {
  /** Base backend URL for API calls */
  apiBase?: string;
  /** Called when user selects a workflow to execute */
  onExecute?: (workflow: WorkflowItem) => void;
  /** Called when user wants to clone a template */
  onClone?: (workflow: WorkflowItem) => void;
  /** Called when user clicks export */
  onExport?: (workflow: WorkflowItem) => void;
}

const WorkflowList: React.FC<WorkflowListProps> = ({
  apiBase = 'http://localhost:9000',
  onExecute,
  onClone,
  onExport,
}) => {
  const [workflows, setWorkflows] = useState<WorkflowItem[]>([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [filterTags, setFilterTags] = useState<string[]>([]);
  const [showTemplatesOnly, setShowTemplatesOnly] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchWorkflows = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams();
      if (showTemplatesOnly) params.set('templates_only', 'true');

      const resp = await fetch(`${apiBase}/api/workflows?${params}`);
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: WorkflowItem[] = await resp.json();
      setWorkflows(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load workflows');
    } finally {
      setLoading(false);
    }
  }, [apiBase, showTemplatesOnly]);

  const searchWorkflows = useCallback(async () => {
    if (!searchQuery && filterTags.length === 0) {
      fetchWorkflows();
      return;
    }
    setLoading(true);
    setError(null);
    try {
      const resp = await fetch(`${apiBase}/api/workflows/search`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          query: searchQuery || undefined,
          tags: filterTags.length > 0 ? filterTags : undefined,
          templates_only: showTemplatesOnly,
        }),
      });
      if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
      const data: WorkflowItem[] = await resp.json();
      setWorkflows(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Search failed');
    } finally {
      setLoading(false);
    }
  }, [apiBase, searchQuery, filterTags, showTemplatesOnly, fetchWorkflows]);

  useEffect(() => {
    fetchWorkflows();
  }, [fetchWorkflows]);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    searchWorkflows();
  };

  const addTag = (tag: string) => {
    const trimmed = tag.trim().toLowerCase();
    if (trimmed && !filterTags.includes(trimmed)) {
      setFilterTags([...filterTags, trimmed]);
    }
  };

  const removeTag = (tag: string) => {
    setFilterTags(filterTags.filter((t) => t !== tag));
  };

  const allTags = Array.from(
    new Set(
      workflows
        .filter((w) => w.tags)
        .flatMap((w) => w.tags!.split(',').map((t) => t.trim()))
        .filter(Boolean),
    ),
  );

  return (
    <div className="workflow-list" data-testid="workflow-list">
      {/* Search bar */}
      <form className="workflow-search" onSubmit={handleSearch} data-testid="workflow-search-form">
        <input
          type="text"
          placeholder="Search workflows…"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          data-testid="workflow-search-input"
          className="workflow-search-input"
        />
        <button type="submit" data-testid="workflow-search-btn" className="btn btn-primary btn-sm">
          Search
        </button>
      </form>

      {/* Filters */}
      <div className="workflow-filters">
        <label className="workflow-template-toggle">
          <input
            type="checkbox"
            checked={showTemplatesOnly}
            onChange={(e) => setShowTemplatesOnly(e.target.checked)}
            data-testid="workflow-templates-toggle"
          />
          Templates only
        </label>

        {allTags.length > 0 && (
          <div className="workflow-tag-filters" data-testid="workflow-tag-filters">
            {allTags.map((tag) => (
              <button
                key={tag}
                className={`tag-chip ${filterTags.includes(tag) ? 'active' : ''}`}
                onClick={() => (filterTags.includes(tag) ? removeTag(tag) : addTag(tag))}
                data-testid={`tag-${tag}`}
              >
                {tag}
              </button>
            ))}
          </div>
        )}
      </div>

      {/* Error */}
      {error && (
        <div className="workflow-error" data-testid="workflow-error" role="alert">
          {error}
        </div>
      )}

      {/* Loading */}
      {loading && <div className="workflow-loading" data-testid="workflow-loading">Loading…</div>}

      {/* Workflow items */}
      {!loading && workflows.length === 0 && (
        <div className="workflow-empty" data-testid="workflow-empty">
          No workflows found.
        </div>
      )}

      <div className="workflow-items">
        {workflows.map((wf) => (
          <div key={wf.id} className="workflow-card" data-testid={`workflow-card-${wf.id}`}>
            <div className="workflow-card-header">
              <h3 className="workflow-card-title">{wf.name}</h3>
              {wf.is_template && (
                <span className="workflow-badge template" data-testid="template-badge">
                  Template
                </span>
              )}
              {wf.template_category && (
                <span className="workflow-badge category">{wf.template_category}</span>
              )}
            </div>

            {wf.description && <p className="workflow-card-desc">{wf.description}</p>}

            <div className="workflow-card-meta">
              {wf.tags && (
                <div className="workflow-card-tags">
                  {wf.tags.split(',').map((tag) => (
                    <span key={tag.trim()} className="tag-chip small">
                      {tag.trim()}
                    </span>
                  ))}
                </div>
              )}
              <span className="workflow-card-stats">
                {wf.execution_count} runs · {Math.round(wf.success_rate * 100)}% success
              </span>
            </div>

            <div className="workflow-card-actions">
              {onExecute && !wf.is_template && (
                <button
                  className="btn btn-primary btn-sm"
                  onClick={() => onExecute(wf)}
                  data-testid={`execute-btn-${wf.id}`}
                >
                  Execute
                </button>
              )}
              {onClone && wf.is_template && (
                <button
                  className="btn btn-secondary btn-sm"
                  onClick={() => onClone(wf)}
                  data-testid={`clone-btn-${wf.id}`}
                >
                  Clone
                </button>
              )}
              {onExport && (
                <button
                  className="btn btn-ghost btn-sm"
                  onClick={() => onExport(wf)}
                  data-testid={`export-btn-${wf.id}`}
                >
                  Export
                </button>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default WorkflowList;
