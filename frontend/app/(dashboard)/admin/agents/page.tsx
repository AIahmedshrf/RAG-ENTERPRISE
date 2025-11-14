'use client';

import React, { useEffect, useState } from 'react';
import { endpoint } from '@/app/lib/api-constants';

interface AgentStats {
  total_agents: number;
  active_agents: number;
  total_conversations: number;
  avg_response_time: number;
}

interface DifyAgent {
  id: string;
  name: string;
  agent_type: string;
  description?: string;
  status: string;
  created_at?: string;
  updated_at?: string;
}

interface Agent {
  id: string;
  name: string;
  description?: string;
  is_active: boolean;
  created_at?: string;
  owner_id?: string;
  dataset_ids?: string[];
}

export default function AgentsAdminPage() {
  const [stats, setStats] = useState<AgentStats>({
    total_agents: 0,
    active_agents: 0,
    total_conversations: 0,
    avg_response_time: 0,
  });
  const [agents, setAgents] = useState<(Agent | DifyAgent)[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [newAgent, setNewAgent] = useState({ name: '', agent_type: 'qa', description: '' });

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      // Try to fetch Dify agents first
      try {
        const res = await fetch(endpoint('/agents'), {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        
        if (res.ok) {
          const data = await res.json();
          const difyAgents = data.data || [];
          setAgents(difyAgents);
          
          setStats({
            total_agents: difyAgents.length,
            active_agents: difyAgents.filter((a: DifyAgent) => a.status === 'created').length,
            total_conversations: 0,
            avg_response_time: 0,
          });
        }
      } catch (err) {
        console.log('Dify agents fetch error:', err);
        // Fallback to legacy agents endpoint
        const res = await fetch(endpoint('/agents/'), {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        
        if (res.ok) {
          const data = await res.json();
          const legacyAgents = data.agents || [];
          setAgents(legacyAgents);
          
          setStats({
            total_agents: legacyAgents.length,
            active_agents: legacyAgents.filter((a: Agent) => a.is_active).length,
            total_conversations: 0,
            avg_response_time: 0,
          });
        }
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateAgent = async () => {
    if (!newAgent.name.trim()) {
      setError('Agent name is required');
      return;
    }

    try {
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint('/agents'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token ? { Authorization: `Bearer ${token}` } : {}),
        },
        body: JSON.stringify({
          name: newAgent.name,
          agent_type: newAgent.agent_type,
          description: newAgent.description,
        }),
      });
      
      if (res.ok) {
        setShowModal(false);
        setNewAgent({ name: '', agent_type: 'qa', description: '' });
        await fetchAgents();
      } else {
        const error = await res.json();
        setError(error.detail || 'Failed to create agent');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Creation failed');
    }
  };

  const handleDeleteAgent = async (agentId: string) => {
    try {
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint(`/agents/${agentId}`), {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      
      if (res.ok) {
        await fetchAgents();
        setShowDeleteConfirm(null);
      } else {
        setError('Failed to delete agent');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Delete failed');
    }
  };

  if (loading) {
    return <div className="text-center py-8">Loading Agents...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🤖 Agents Management</h1>
          <p className="text-gray-600 mt-1">Create and manage AI agents powered by Dify</p>
        </div>
        <button
          onClick={() => setShowModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          ➕ Create Agent
        </button>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Agents"
          value={stats.total_agents}
          icon="🤖"
          color="blue"
        />
        <StatCard
          title="Active"
          value={stats.active_agents}
          icon="✅"
          color="green"
        />
        <StatCard
          title="Conversations"
          value={stats.total_conversations}
          icon="💬"
          color="purple"
        />
        <StatCard
          title="Avg Response"
          value={`${stats.avg_response_time}ms`}
          icon="⚡"
          color="orange"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <ActionCard
          title="Create New Agent"
          description="Build a new AI agent with custom configuration"
          icon="➕"
          onClick={() => setShowModal(true)}
        />
        <ActionCard
          title="Agent Templates"
          description="Use predefined agent types (Portfolio, Risk, Market, etc.)"
          icon="📋"
          href="/admin/agents/templates"
        />
      </div>

      {/* Agents List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">All Agents</h2>
        </div>
        
        {agents.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No agents created yet. <button onClick={() => setShowModal(true)} className="text-blue-600 hover:underline">Create one</button>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {agents.map((agent: any) => {
              const isDifyAgent = 'agent_type' in agent;
              return (
                <div key={agent.id} className="p-6 hover:bg-gray-50 transition-colors">
                  <div className="flex items-start justify-between">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                          isDifyAgent 
                            ? (agent.status === 'created' ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800')
                            : (agent.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800')
                        }`}>
                          {isDifyAgent ? (agent.status || 'Created') : (agent.is_active ? 'Active' : 'Inactive')}
                        </span>
                      </div>
                      {agent.description && (
                        <p className="text-gray-600 mt-1">{agent.description}</p>
                      )}
                      {isDifyAgent && agent.agent_type && (
                        <div className="flex gap-2 mt-2">
                          <span className="px-2 py-1 bg-purple-50 text-purple-700 rounded text-xs font-medium">
                            {agent.agent_type}
                          </span>
                        </div>
                      )}
                      {agent.dataset_ids && agent.dataset_ids.length > 0 && (
                        <div className="flex gap-2 mt-2 flex-wrap">
                          {agent.dataset_ids.map((id: string) => (
                            <span
                              key={id}
                              className="px-2 py-1 bg-blue-50 text-blue-700 rounded text-xs"
                            >
                              📦 {id}
                            </span>
                          ))}
                        </div>
                      )}
                      {agent.created_at && (
                        <p className="text-sm text-gray-500 mt-2">
                          Created: {new Date(agent.created_at).toLocaleDateString()}
                        </p>
                      )}
                    </div>
                    <div className="flex gap-2 ml-4">
                      <a
                        href={`/admin/agents/${agent.id}`}
                        className="px-3 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors text-sm font-medium"
                      >
                        Execute
                      </a>
                      <button
                        onClick={() => setShowDeleteConfirm(agent.id)}
                        className="px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition-colors text-sm font-medium"
                      >
                        Delete
                      </button>
                    </div>
                  </div>

                  {/* Delete Confirmation */}
                  {showDeleteConfirm === agent.id && (
                    <div className="mt-4 p-4 bg-red-50 border border-red-200 rounded-lg">
                      <p className="text-sm text-red-800 mb-3">
                        Are you sure you want to delete "{agent.name}"?
                      </p>
                      <div className="flex gap-2">
                        <button
                          onClick={() => handleDeleteAgent(agent.id)}
                          className="px-3 py-2 bg-red-600 text-white rounded hover:bg-red-700 text-sm font-medium"
                        >
                          Confirm Delete
                        </button>
                        <button
                          onClick={() => setShowDeleteConfirm(null)}
                          className="px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded hover:bg-gray-50 text-sm font-medium"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Create Agent Modal */}
      {showModal && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg shadow-lg max-w-md w-full mx-4">
            <div className="px-6 py-4 border-b border-gray-200">
              <h2 className="text-lg font-semibold text-gray-900">Create New Agent</h2>
            </div>
            
            <div className="px-6 py-4 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Name *
                </label>
                <input
                  type="text"
                  value={newAgent.name}
                  onChange={(e) => setNewAgent({ ...newAgent, name: e.target.value })}
                  placeholder="e.g., Portfolio Analyst"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Agent Type *
                </label>
                <select
                  value={newAgent.agent_type}
                  onChange={(e) => setNewAgent({ ...newAgent, agent_type: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="qa">Q&A Agent</option>
                  <option value="portfolio">Portfolio Agent</option>
                  <option value="risk">Risk Management Agent</option>
                  <option value="market">Market Analysis Agent</option>
                  <option value="compliance">Compliance Agent</option>
                  <option value="summarizer">Summarizer Agent</option>
                  <option value="researcher">Researcher Agent</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Description
                </label>
                <textarea
                  value={newAgent.description}
                  onChange={(e) => setNewAgent({ ...newAgent, description: e.target.value })}
                  placeholder="Optional description"
                  rows={3}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>

            <div className="px-6 py-4 border-t border-gray-200 flex gap-2">
              <button
                onClick={() => {
                  setShowModal(false);
                  setError(null);
                }}
                className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium"
              >
                Cancel
              </button>
              <button
                onClick={handleCreateAgent}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
              >
                Create
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  const colorMap: any = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
    purple: 'bg-purple-50 border-purple-200',
  };
  const colorClass = colorMap[color as string] || 'bg-gray-50 border-gray-200';

  return (
    <div className={`${colorClass} border rounded-lg p-4`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );
}

function ActionCard({ title, description, icon, href, onClick }: any) {
  if (href) {
    return (
      <a
        href={href}
        className="block bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-blue-400 transition-all"
      >
        <div className="text-3xl mb-2">{icon}</div>
        <h3 className="font-semibold text-gray-900">{title}</h3>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
      </a>
    );
  }

  return (
    <button
      onClick={onClick}
      className="block w-full text-left bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-blue-400 transition-all"
    >
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </button>
  );
}

