'use client';

import React, { useEffect, useState } from 'react';
import { endpoint } from '@/app/lib/api-constants';
import { useParams } from 'next/navigation';

interface AgentDetails {
  id: string;
  name: string;
  agent_type: string;
  description?: string;
  status: string;
}

export default function AgentExecutePage() {
  const params = useParams();
  const agentId = params.id as string;

  const [agent, setAgent] = useState<AgentDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [executing, setExecuting] = useState(false);
  const [inputs, setInputs] = useState<Record<string, any>>({});
  const [result, setResult] = useState<any>(null);

  useEffect(() => {
    if (agentId) {
      fetchAgent();
    }
  }, [agentId]);

  const fetchAgent = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint(`/agents/${agentId}`), {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      
      if (res.ok) {
        const data = await res.json();
        setAgent(data.data || data);
      } else {
        setError('Failed to load agent');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agent');
    } finally {
      setLoading(false);
    }
  };

  const handleExecute = async () => {
    try {
      setExecuting(true);
      setError(null);
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint(`/agents/${agentId}/execute`), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          inputs: inputs,
        }),
      });
      
      if (res.ok) {
        const data = await res.json();
        setResult(data);
      } else {
        const data = await res.json();
        setError(data.detail || 'Execution failed');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Execution failed');
    } finally {
      setExecuting(false);
    }
  };

  const getInputTemplate = () => {
    const templates: Record<string, Record<string, string>> = {
      portfolio: {
        portfolio_data: '{"assets": [{"symbol": "AAPL", "weight": 0.4}]}',
        benchmark: 'S&P 500',
      },
      risk: {
        asset_data: '{"symbols": ["AAPL", "MSFT"]}',
        time_horizon: '1y',
      },
      market: {
        market_data: '{}',
        asset_type: 'equity',
      },
      compliance: {
        transaction_data: '{}',
        regulation_type: 'general',
      },
      summarizer: {
        content: 'Enter text to summarize...',
      },
      researcher: {
        query: 'What is the current market trend?',
        topic: 'finance',
      },
      qa: {
        question: 'What is portfolio diversification?',
      },
    };
    return templates[agent?.agent_type || 'qa'] || {};
  };

  if (loading) {
    return <div className="text-center py-8">Loading agent...</div>;
  }

  if (!agent) {
    return (
      <div className="text-center py-8">
        <p className="text-red-600">Agent not found</p>
      </div>
    );
  }

  const template = getInputTemplate();

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">🤖 Execute Agent</h1>
        <p className="text-gray-600 mt-1">Run {agent.name}</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Agent Details */}
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow p-6 sticky top-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Agent Details</h2>
            
            <div className="space-y-3">
              <div>
                <p className="text-xs text-gray-500 font-semibold">NAME</p>
                <p className="text-gray-900 font-medium">{agent.name}</p>
              </div>

              <div>
                <p className="text-xs text-gray-500 font-semibold">TYPE</p>
                <span className="inline-block px-2 py-1 bg-purple-100 text-purple-800 rounded text-sm font-medium mt-1">
                  {agent.agent_type}
                </span>
              </div>

              <div>
                <p className="text-xs text-gray-500 font-semibold">STATUS</p>
                <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-medium mt-1">
                  {agent.status || 'Ready'}
                </span>
              </div>

              {agent.description && (
                <div>
                  <p className="text-xs text-gray-500 font-semibold">DESCRIPTION</p>
                  <p className="text-gray-600 text-sm mt-1">{agent.description}</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Execution Interface */}
        <div className="lg:col-span-2 space-y-6">
          {/* Input Section */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Input Parameters</h2>
            
            <div className="space-y-4">
              {Object.entries(template).map(([key, defaultValue]) => (
                <div key={key}>
                  <label className="block text-sm font-medium text-gray-700 mb-1 capitalize">
                    {key.replace(/_/g, ' ')}
                  </label>
                  {key.includes('data') || key.includes('content') ? (
                    <textarea
                      value={inputs[key] ?? defaultValue}
                      onChange={(e) => setInputs({ ...inputs, [key]: e.target.value })}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono text-sm"
                      placeholder={defaultValue}
                    />
                  ) : (
                    <input
                      type="text"
                      value={inputs[key] ?? defaultValue}
                      onChange={(e) => setInputs({ ...inputs, [key]: e.target.value })}
                      className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder={defaultValue}
                    />
                  )}
                </div>
              ))}
            </div>

            <button
              onClick={handleExecute}
              disabled={executing}
              className="w-full mt-6 px-4 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
            >
              {executing ? '⏳ Executing...' : '▶️ Execute Agent'}
            </button>
          </div>

          {/* Result Section */}
          {result && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Execution Result</h2>
              
              <div className="space-y-4">
                <div>
                  <p className="text-xs text-gray-500 font-semibold mb-2">STATUS</p>
                  <span className="inline-block px-2 py-1 bg-green-100 text-green-800 rounded text-sm font-medium">
                    {result.status || 'Completed'}
                  </span>
                </div>

                {result.duration_ms && (
                  <div>
                    <p className="text-xs text-gray-500 font-semibold mb-2">DURATION</p>
                    <p className="text-gray-900">{result.duration_ms}ms</p>
                  </div>
                )}

                {result.timestamp && (
                  <div>
                    <p className="text-xs text-gray-500 font-semibold mb-2">TIMESTAMP</p>
                    <p className="text-gray-900 text-sm">{new Date(result.timestamp).toLocaleString()}</p>
                  </div>
                )}

                <div>
                  <p className="text-xs text-gray-500 font-semibold mb-2">OUTPUT</p>
                  <div className="bg-gray-50 rounded-lg p-4 border border-gray-200 max-h-96 overflow-auto">
                    <pre className="text-xs text-gray-700 whitespace-pre-wrap break-words font-mono">
                      {JSON.stringify(result.output || result.result || result, null, 2)}
                    </pre>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
