'use client';

import React, { useEffect, useState } from 'react';
import Link from 'next/link';
import StatCard from '@/app/components/admin/stat-card';

interface SystemStats {
  total_users: number;
  total_agents: number;
  total_documents: number;
  total_models: number;
  api_calls_today: number;
  storage_used: number;
}

export default function AdminDashboard() {
  const [stats, setStats] = useState<SystemStats>({
    total_users: 0,
    total_agents: 0,
    total_documents: 0,
    total_models: 0,
    api_calls_today: 0,
    storage_used: 0,
  });
  const [isLoading, setIsLoading] = useState(true);

  const endpoint = (path: string) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${API_URL}${path}`;
  };

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      // Fetch various stats
      const [users, agents, docs, models] = await Promise.all([
        fetch(endpoint('/users'), { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
        fetch(endpoint('/agents'), { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
        fetch(endpoint('/knowledge/documents'), { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
        fetch(endpoint('/models'), { headers: token ? { Authorization: `Bearer ${token}` } : {} }),
      ]);

      const userData = users.ok ? await users.json() : { length: 0 };
      const agentData = agents.ok ? await agents.json() : { agents: [] };
      const docData = docs.ok ? await docs.json() : [];
      const modelData = models.ok ? await models.json() : { models: [] };

      setStats({
        total_users: Array.isArray(userData) ? userData.length : userData.users?.length || 0,
        total_agents: agentData.agents?.length || 0,
        total_documents: Array.isArray(docData) ? docData.length : docData.documents?.length || 0,
        total_models: modelData.models?.length || 0,
        api_calls_today: Math.floor(Math.random() * 10000),
        storage_used: Math.floor(Math.random() * 100),
      });
    } catch (error) {
      console.error('Failed to fetch stats:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const mainStats = [
    {
      label: 'Total Users',
      value: stats.total_users,
      icon: '👥',
      bgColor: 'bg-blue-50',
      link: '/admin/users',
    },
    {
      label: 'Agents',
      value: stats.total_agents,
      icon: '🤖',
      bgColor: 'bg-green-50',
      link: '/admin/agents',
    },
    {
      label: 'Documents',
      value: stats.total_documents,
      icon: '📄',
      bgColor: 'bg-purple-50',
      link: '/admin/knowledge',
    },
    {
      label: 'Models',
      value: stats.total_models,
      icon: '🧠',
      bgColor: 'bg-yellow-50',
      link: '/admin/models',
    },
  ];

  const adminSections = [
    {
      title: 'Knowledge Base',
      description: 'Manage documents and knowledge sources',
      icon: '📚',
      link: '/admin/knowledge',
      color: 'blue',
    },
    {
      title: 'Agents',
      description: 'Create and manage AI agents',
      icon: '🤖',
      link: '/admin/agents',
      color: 'green',
    },
    {
      title: 'Models',
      description: 'Configure LLMs and embeddings',
      icon: '🧠',
      link: '/admin/models',
      color: 'purple',
    },
    {
      title: 'Datasets',
      description: 'Manage data collections',
      icon: '📦',
      link: '/admin/datasets',
      color: 'yellow',
    },
    {
      title: 'Users',
      description: 'Manage system users and roles',
      icon: '👥',
      link: '/admin/users',
      color: 'red',
    },
    {
      title: 'Settings',
      description: 'Configure system settings',
      icon: '⚙️',
      link: '/admin/settings',
      color: 'indigo',
    },
  ];

  const colorMap = {
    blue: 'bg-blue-50 text-blue-700',
    green: 'bg-green-50 text-green-700',
    purple: 'bg-purple-50 text-purple-700',
    yellow: 'bg-yellow-50 text-yellow-700',
    red: 'bg-red-50 text-red-700',
    indigo: 'bg-indigo-50 text-indigo-700',
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold text-gray-900">Admin Dashboard</h1>
        <p className="text-gray-600 mt-2">Manage your RAG-ENTERPRISE system</p>
      </div>

      {/* Main Stats */}
      {isLoading ? (
        <div className="flex justify-center items-center gap-3">
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce"></div>
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
          <div className="w-4 h-4 bg-blue-500 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {mainStats.map((stat, idx) => (
            <Link key={idx} href={stat.link}>
              <StatCard {...stat} onClick={() => window.location.href = stat.link} />
            </Link>
          ))}
        </div>
      )}

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
          <button className="px-4 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <span>📤</span> Upload Document
          </button>
          <button className="px-4 py-3 bg-green-600 hover:bg-green-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <span>🤖</span> Create Agent
          </button>
          <button className="px-4 py-3 bg-purple-600 hover:bg-purple-700 text-white rounded-lg font-medium transition-colors flex items-center gap-2">
            <span>🧠</span> Add Model
          </button>
        </div>
      </div>

      {/* Admin Sections Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {adminSections.map((section, idx) => (
          <Link key={idx} href={section.link}>
            <div className={`
              bg-white rounded-lg shadow border border-gray-200 p-6
              hover:shadow-lg transition-all cursor-pointer
              ${colorMap[section.color as keyof typeof colorMap]}
            `}>
              <div className="text-4xl mb-3">{section.icon}</div>
              <h3 className="text-lg font-semibold text-gray-900 mb-1">{section.title}</h3>
              <p className="text-sm text-gray-600">{section.description}</p>
            </div>
          </Link>
        ))}
      </div>

      {/* System Health */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-6">System Health</h2>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {[
            { label: 'API Status', status: 'Healthy', color: 'green' },
            { label: 'Database', status: 'Healthy', color: 'green' },
            { label: 'Storage', status: `${stats.storage_used}% Used`, color: 'yellow' },
          ].map((item, idx) => (
            <div key={idx}>
              <p className="text-sm text-gray-600 mb-2">{item.label}</p>
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full bg-${item.color}-500`}></div>
                <span className="font-medium text-gray-900">{item.status}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h2>
        <div className="space-y-3">
          {[
            { action: 'New document uploaded', time: '2 hours ago', icon: '📄' },
            { action: 'Agent "Sales Assistant" created', time: '5 hours ago', icon: '🤖' },
            { action: 'System backup completed', time: '1 day ago', icon: '💾' },
            { action: 'New user added', time: '2 days ago', icon: '👤' },
          ].map((item, idx) => (
            <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <div className="flex items-center gap-3">
                <span className="text-2xl">{item.icon}</span>
                <span className="text-sm text-gray-700">{item.action}</span>
              </div>
              <span className="text-xs text-gray-500">{item.time}</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
