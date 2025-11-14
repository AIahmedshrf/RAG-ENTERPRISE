'use client';

import React, { useEffect, useState } from 'react';
import { endpoint } from '@/app/lib/api-constants';

interface AgentStats {
  total_agents: number;
  active_agents: number;
  total_conversations: number;
  avg_response_time: number;
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
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState<string | null>(null);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');
      
      const res = await fetch(endpoint('/agents/'), {
        headers: token ? { Authorization: `Bearer ${token}` } : undefined,
      });
      
      if (res.ok) {
        const data = await res.json();
        const agents = data.agents || [];
        setAgents(agents);
        
        // Calculate stats
        setStats({
          total_agents: agents.length,
          active_agents: agents.filter((a: Agent) => a.is_active).length,
          total_conversations: 0, // TODO: fetch from API
          avg_response_time: 0, // TODO: fetch from API
        });
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load agents');
    } finally {
      setLoading(false);
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
          <p className="text-gray-600 mt-1">Create and manage AI agents</p>
        </div>
        <a
          href="/admin/agents/create"
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium"
        >
          ➕ Create Agent
        </a>
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
          href="/admin/agents/create"
        />
        <ActionCard
          title="Agent Templates"
          description="Use predefined templates to create agents quickly"
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
            No agents created yet. <a href="/admin/agents/create" className="text-blue-600 hover:underline">Create one</a>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {agents.map((agent) => (
              <div key={agent.id} className="p-6 hover:bg-gray-50 transition-colors">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="text-lg font-semibold text-gray-900">{agent.name}</h3>
                      <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                        agent.is_active
                          ? 'bg-green-100 text-green-800'
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {agent.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                    {agent.description && (
                      <p className="text-gray-600 mt-1">{agent.description}</p>
                    )}
                    {agent.dataset_ids && agent.dataset_ids.length > 0 && (
                      <div className="flex gap-2 mt-2 flex-wrap">
                        {agent.dataset_ids.map((id) => (
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
                      Configure
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
            ))}
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  const colorClass = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
    purple: 'bg-purple-50 border-purple-200',
  }[color] || 'bg-gray-50 border-gray-200';

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

function ActionCard({ title, description, icon, href }: any) {
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
