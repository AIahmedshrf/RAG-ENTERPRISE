// Admin Dashboard Overview
'use client';

import React, { useEffect, useState } from 'react';

interface Stats {
  apps: number;
  datasets: number;
  users: number;
  messages: number;
}

export default function AdminOverview() {
  const [stats, setStats] = useState<Stats>({
    apps: 0,
    datasets: 0,
    users: 0,
    messages: 0,
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadStats();
  }, []);

  const loadStats = async () => {
    try {
      // TODO: Replace with actual API calls
      setStats({
        apps: 12,
        datasets: 8,
        users: 45,
        messages: 1234,
      });
    } catch (error) {
      console.error('Failed to load stats:', error);
    } finally {
      setLoading(false);
    }
  };

  const statCards = [
    { name: 'Applications', value: stats.apps, icon: '🚀', color: 'blue' },
    { name: 'Knowledge Base', value: stats.datasets, icon: '📚', color: 'green' },
    { name: 'Users', value: stats.users, icon: '👥', color: 'purple' },
    { name: 'Total Messages', value: stats.messages, icon: '💬', color: 'orange' },
  ];

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Dashboard Overview</h1>
        <p className="mt-2 text-gray-600">Welcome to RAG-ENTERPRISE Admin Panel</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <div
            key={stat.name}
            className="bg-white rounded-lg border border-gray-200 p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-gray-600">{stat.name}</p>
                <p className="mt-2 text-3xl font-bold text-gray-900">{stat.value}</p>
              </div>
              <div className={`text-4xl bg-${stat.color}-50 p-3 rounded-lg`}>
                {stat.icon}
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Quick Actions</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-blue-500 hover:bg-blue-50 transition-colors">
            <div className="text-2xl mb-2">➕</div>
            <div className="font-medium">Create Application</div>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-green-500 hover:bg-green-50 transition-colors">
            <div className="text-2xl mb-2">📄</div>
            <div className="font-medium">Upload Document</div>
          </button>
          <button className="p-4 border-2 border-dashed border-gray-300 rounded-lg hover:border-purple-500 hover:bg-purple-50 transition-colors">
            <div className="text-2xl mb-2">👤</div>
            <div className="font-medium">Invite User</div>
          </button>
        </div>
      </div>

      {/* Recent Activity */}
      <div className="bg-white rounded-lg border border-gray-200 p-6">
        <h3 className="text-lg font-semibold mb-4">Recent Activity</h3>
        <div className="space-y-3">
          {[1, 2, 3, 4, 5].map((i) => (
            <div key={i} className="flex items-center gap-4 p-3 hover:bg-gray-50 rounded-lg">
              <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
                📝
              </div>
              <div className="flex-1">
                <p className="text-sm font-medium">Activity {i}</p>
                <p className="text-xs text-gray-500">5 minutes ago</p>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
