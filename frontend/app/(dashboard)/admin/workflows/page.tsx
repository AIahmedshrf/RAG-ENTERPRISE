'use client';

import React, { useEffect, useState } from 'react';
import { endpoint } from '@/app/lib/api-constants';

interface WorkflowTemplate {
  template_type: string;
  name: string;
  description: string;
  steps: number;
  agents: string[];
}

interface Workflow {
  workflow_id: string;
  name: string;
  status: string;
  steps: number;
  created_at?: string;
}

export default function WorkflowsAdminPage() {
  const [templates, setTemplates] = useState<Record<string, WorkflowTemplate>>({});
  const [workflows, setWorkflows] = useState<Workflow[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedTemplate, setSelectedTemplate] = useState<string | null>(null);
  const [workflowName, setWorkflowName] = useState('');
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [executingWorkflow, setExecutingWorkflow] = useState<string | null>(null);

  useEffect(() => {
    fetchTemplates();
  }, []);

  const fetchTemplates = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint('/workflows/templates/available'), {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      
      if (res.ok) {
        const data = await res.json();
        setTemplates(data.data || {});
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load templates');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateWorkflow = async () => {
    if (!selectedTemplate || !workflowName.trim()) {
      setError('Please select a template and enter a name');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint('/workflows/from-template'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          template_type: selectedTemplate,
        }),
      });
      
      if (res.ok) {
        setShowCreateModal(false);
        setSelectedTemplate(null);
        setWorkflowName('');
        setError(null);
        // In real app, would add to workflows list
      } else {
        const data = await res.json();
        setError(data.detail || 'Failed to create workflow');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Creation failed');
    }
  };

  const handleExecuteWorkflow = async (templateType: string) => {
    try {
      setExecutingWorkflow(templateType);
      const token = localStorage.getItem('access_token');
      
      // Create context based on template type
      const context = getContextForTemplate(templateType);
      
      const res = await fetch(endpoint(`/workflows/${templateType}/execute`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          workflow_id: templateType,
          context: context,
        }),
      });
      
      if (res.ok) {
        const data = await res.json();
        console.log('Workflow execution result:', data);
        // Could show results modal here
      } else {
        setError('Failed to execute workflow');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setExecutingWorkflow(null);
    }
  };

  const getContextForTemplate = (templateType: string) => {
    const contexts: Record<string, any> = {
      portfolio_review: {
        portfolio: {
          assets: [
            { symbol: 'AAPL', weight: 0.4, shares: 100 },
            { symbol: 'MSFT', weight: 0.6, shares: 50 }
          ]
        },
        benchmark: 'S&P 500',
        market_data: {},
      },
      compliance_review: {
        transaction: {},
        regulation: 'general',
        assets: [],
      },
      market_analysis: {
        market_data: {},
        asset_type: 'equity',
      },
    };
    return contexts[templateType] || {};
  };

  const previewTemplate = async (templateType: string) => {
    try {
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint(`/workflows/templates/${templateType}/preview`), {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      
      if (res.ok) {
        const data = await res.json();
        console.log('Template preview:', data);
      }
    } catch (err) {
      console.error('Failed to preview template:', err);
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading workflows...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🔄 Workflows Management</h1>
          <p className="text-gray-600 mt-1">Create and execute multi-agent workflows</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          ➕ New Workflow
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Workflow Templates */}
      <div>
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Available Templates</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {Object.entries(templates).map(([key, template]) => (
            <div
              key={key}
              className="bg-white rounded-lg shadow border border-gray-200 hover:shadow-lg transition-shadow"
            >
              <div className="px-6 py-4 border-b border-gray-200">
                <h3 className="text-lg font-semibold text-gray-900">{template.name}</h3>
              </div>
              
              <div className="px-6 py-4 space-y-3">
                <p className="text-gray-600 text-sm">{template.description}</p>
                
                <div className="bg-gray-50 rounded-lg p-3">
                  <p className="text-xs text-gray-500 font-semibold mb-2">WORKFLOW STEPS</p>
                  <ol className="space-y-1">
                    {template.agents.map((agent, idx) => (
                      <li key={idx} className="text-sm text-gray-700">
                        <span className="font-medium">{idx + 1}.</span> {agent}
                      </li>
                    ))}
                  </ol>
                </div>

                <div className="flex gap-2 pt-2">
                  <button
                    onClick={() => {
                      setSelectedTemplate(key);
                      setShowCreateModal(true);
                    }}
                    className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                  >
                    Create
                  </button>
                  <button
                    onClick={() => handleExecuteWorkflow(key)}
                    disabled={executingWorkflow === key}
                    className="flex-1 px-3 py-2 bg-green-50 text-green-600 rounded-lg hover:bg-green-100 transition-colors text-sm font-medium disabled:opacity-50"
                  >
                    {executingWorkflow === key ? 'Running...' : 'Execute'}
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Create Workflow Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Create Workflow</h2>
            </div>
            
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Workflow Name *
                </label>
                <input
                  type="text"
                  value={workflowName}
                  onChange={(e) => setWorkflowName(e.target.value)}
                  placeholder="e.g., Portfolio Analysis 2024"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Template *
                </label>
                <select
                  value={selectedTemplate || ''}
                  onChange={(e) => setSelectedTemplate(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Select a template...</option>
                  {Object.entries(templates).map(([key, template]) => (
                    <option key={key} value={key}>
                      {template.name} ({template.steps} steps)
                    </option>
                  ))}
                </select>
              </div>

              {selectedTemplate && templates[selectedTemplate] && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-xs text-blue-600 font-semibold mb-2">WORKFLOW STEPS</p>
                  <ol className="space-y-1">
                    {templates[selectedTemplate].agents.map((agent, idx) => (
                      <li key={idx} className="text-xs text-blue-700">
                        <span className="font-medium">{idx + 1}.</span> {agent}
                      </li>
                    ))}
                  </ol>
                </div>
              )}
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex gap-2">
              <button
                onClick={() => {
                  setShowCreateModal(false);
                  setSelectedTemplate(null);
                  setWorkflowName('');
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateWorkflow}
                disabled={!selectedTemplate || !workflowName.trim()}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium disabled:opacity-50"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Start</h3>
        <div className="space-y-3">
          <p className="text-gray-600">
            🔄 Workflows combine multiple agents to accomplish complex tasks. Select a template above or create a custom workflow.
          </p>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <p className="text-sm text-blue-900 font-semibold mb-2">💡 Workflow Templates Include:</p>
            <ul className="text-sm text-blue-800 space-y-1">
              <li>✓ Portfolio Review - Complete portfolio analysis with risk assessment</li>
              <li>✓ Compliance Review - Regulatory compliance checks with risk evaluation</li>
              <li>✓ Market Analysis - Market trends and forecasting</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
