'use client';

import React, { useEffect, useState } from 'react';
import StatCard from '@/app/components/admin/stat-card';
import DataTable from '@/app/components/admin/data-table';
import FilterBar from '@/app/components/admin/filter-bar';
import Modal from '@/app/components/admin/modal';

interface Agent {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
  created_at: string;
  conversations?: number;
}

export default function AgentsPage() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedAgent, setSelectedAgent] = useState<Agent | null>(null);
  const [filters, setFilters] = useState({});

  const endpoint = (path: string) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${API_URL}${path}`;
  };

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint('/agents'), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setAgents(Array.isArray(data) ? data : data.agents || []);
      }
    } catch (error) {
      console.error('Failed to fetch agents:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAgent = async () => {
    if (!selectedAgent) return;
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint(`/agents/${selectedAgent.id}`), {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        setAgents(agents.filter(a => a.id !== selectedAgent.id));
        setShowDeleteModal(false);
        setSelectedAgent(null);
      }
    } catch (error) {
      console.error('Failed to delete agent:', error);
    }
  };

  const stats = [
    {
      label: 'Total Agents',
      value: agents.length,
      icon: '🤖',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Active Agents',
      value: agents.filter(a => a.is_active).length,
      icon: '✅',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Total Conversations',
      value: agents.reduce((sum, a) => sum + (a.conversations || 0), 0),
      icon: '💬',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'Performance Score',
      value: '98%',
      icon: '📈',
      bgColor: 'bg-yellow-50',
    },
  ];

  const tableColumns: Array<any> = [
    { header: 'Agent Name', accessor: 'name' as const, width: 'w-1/3' },
    { header: 'Status', accessor: (agent: Agent) => (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
        agent.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-700'
      }`}>
        {agent.is_active ? 'Active' : 'Inactive'}
      </span>
    ) },
    { header: 'Conversations', accessor: (agent: Agent) => agent.conversations || 0 },
    { header: 'Created', accessor: (agent: Agent) => new Date(agent.created_at).toLocaleDateString() },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Agents Management</h1>
          <p className="text-gray-600 mt-1">Create and manage AI agents</p>
        </div>
        <button className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors">
          ➕ Create Agent
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatCard key={idx} {...stat} />
        ))}
      </div>

      {/* Filters */}
      <FilterBar
        filters={{
          status: {
            label: 'Status',
            type: 'select',
            options: [
              { label: 'Active', value: 'active' },
              { label: 'Inactive', value: 'inactive' },
            ],
          },
          search: {
            label: 'Search',
            type: 'search',
            placeholder: 'Search agents...',
          },
        }}
        onFilterChange={setFilters}
        onReset={() => {
          setFilters({});
          fetchAgents();
        }}
      />

      {/* Table */}
      <DataTable<Agent>
        columns={tableColumns}
        data={agents}
        isLoading={isLoading}
        emptyMessage="No agents yet. Create your first agent!"
        onRowClick={(agent) => setSelectedAgent(agent)}
        actions={(agent) => (
          <div className="flex gap-2">
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              Configure
            </button>
            <button className="text-green-600 hover:text-green-700 text-sm font-medium">
              Test
            </button>
            <button
              onClick={() => {
                setSelectedAgent(agent);
                setShowDeleteModal(true);
              }}
              className="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Delete
            </button>
          </div>
        )}
      />

      {/* Delete Modal */}
      <Modal
        isOpen={showDeleteModal}
        title="Delete Agent?"
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeleteAgent}
        confirmText="Delete"
        isDangerous={true}
      >
        <p>Are you sure you want to delete <strong>{selectedAgent?.name}</strong>? This action cannot be undone.</p>
      </Modal>
    </div>
  );
}
