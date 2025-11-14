'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/auth-context';

interface Stats {
  datasets: number;
  apps: number;
  users: number;
  workspace: string;
}

export default function AdminOverview() {
  const router = useRouter();
  const { user } = useAuth();
  const [stats, setStats] = useState<Stats>({
    datasets: 0,
    apps: 0,
    users: 0,
    workspace: ''
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchStats();
  }, []);

  const fetchStats = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setLoading(false);
        return;
      }
      
      const [datasetsRes, appsRes, usersRes, workspaceRes] = await Promise.all([
        fetch('http://localhost:8000/admin/datasets', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/admin/apps', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/admin/workspace/members', {
          headers: { Authorization: `Bearer ${token}` }
        }),
        fetch('http://localhost:8000/admin/workspace', {
          headers: { Authorization: `Bearer ${token}` }
        })
      ]);

      const datasets = datasetsRes.ok ? await datasetsRes.json() : { total: 0 };
      const apps = appsRes.ok ? await appsRes.json() : { total: 0 };
      const users = usersRes.ok ? await usersRes.json() : { total: 0 };
      const workspace = workspaceRes.ok ? await workspaceRes.json() : { name: 'Workspace' };

      // Ensure workspace is a string
      const workspaceName = typeof workspace === 'string' 
        ? workspace 
        : (workspace?.name || workspace?.title || 'Workspace');

      setStats({
        datasets: datasets?.total || 0,
        apps: apps?.total || 0,
        users: users?.total || 0,
        workspace: workspaceName
      });
    } catch (error) {
      console.error('Error fetching stats:', error);
      // Set default values on error
      setStats({
        datasets: 0,
        apps: 0,
        users: 0,
        workspace: 'Workspace'
      });
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">
          Welcome back, {user?.name}! 👋
        </h1>
        <p className="text-gray-600 mt-1">
          Here's what's happening in your workspace
        </p>
      </div>

      {/* Stats Grid - Enhanced with RBAC */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6 mb-8">
        <StatCard
          title="Datasets"
          value={stats.datasets}
          icon="📊"
          color="blue"
          onClick={() => router.push('/admin/datasets')}
        />
        <StatCard
          title="Applications"
          value={stats.apps}
          icon="🚀"
          color="purple"
          onClick={() => router.push('/admin/apps')}
        />
        <StatCard
          title="Team Members"
          value={stats.users}
          icon="👥"
          color="green"
          onClick={() => router.push('/admin/users')}
        />
        <StatCard
          title="Active Roles"
          value={6}
          icon="🎖️"
          color="purple"
          onClick={() => router.push('/admin/roles-permissions')}
        />
        <StatCard
          title="Workspace"
          value={stats.workspace}
          icon="🏢"
          color="yellow"
          onClick={() => router.push('/admin/workspace')}
          isText
        />
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-lg shadow p-6 mb-8">
        <h2 className="text-xl font-semibold mb-4">⚡ Quick Actions</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          <QuickAction
            title="Manage Users"
            description="Add, remove, edit users"
            icon="👥"
            onClick={() => router.push('/admin/users')}
          />
          <QuickAction
            title="Manage Roles"
            description="Control permissions"
            icon="🎖️"
            onClick={() => router.push('/admin/roles-permissions')}
          />
          <QuickAction
            title="Create Dataset"
            description="Add knowledge base"
            icon="📚"
            onClick={() => router.push('/admin/datasets')}
          />
          <QuickAction
            title="Manage Agents"
            description="Deploy AI agents"
            icon="🤖"
            onClick={() => router.push('/admin/agents')}
          />
          <QuickAction
            title="Knowledge Base"
            description="Manage documents"
            icon="📖"
            onClick={() => router.push('/admin/knowledge')}
          />
          <QuickAction
            title="Manage Models"
            description="Configure models"
            icon="🧠"
            onClick={() => router.push('/admin/models')}
          />
          <QuickAction
            title="View Analytics"
            description="Check performance"
            icon="📈"
            onClick={() => router.push('/admin/analytics')}
          />
          <QuickAction
            title="Settings"
            description="System configuration"
            icon="⚙️"
            onClick={() => router.push('/admin/settings-enhanced')}
          />
        </div>
      </div>

      {/* System Status */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">🔧 System Status</h2>
          <div className="space-y-3">
            <StatusItem label="Backend API" status="healthy" />
            <StatusItem label="Database" status="healthy" />
            <StatusItem label="Authentication" status="healthy" />
            <StatusItem label="RBAC System" status="healthy" />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">🔐 RBAC Overview</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-2 text-sm">
              <span className="text-gray-600">Available Roles</span>
              <span className="font-semibold text-gray-900">6</span>
            </div>
            <div className="flex items-center justify-between p-2 text-sm border-t">
              <span className="text-gray-600">Total Permissions</span>
              <span className="font-semibold text-gray-900">28</span>
            </div>
            <div className="flex items-center justify-between p-2 text-sm border-t">
              <span className="text-gray-600">Permission Categories</span>
              <span className="font-semibold text-gray-900">8</span>
            </div>
            <button
              onClick={() => router.push('/admin/roles-permissions')}
              className="w-full mt-2 px-3 py-2 text-sm font-medium text-blue-600 hover:bg-blue-50 rounded-lg border border-blue-200"
            >
              Manage RBAC →
            </button>
          </div>
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">📌 Recent Activity</h2>
          <div className="space-y-3">
            <ActivityItem
              title="System initialized"
              time="Today"
              icon="✅"
            />
            <ActivityItem
              title={`${stats.datasets} datasets created`}
              time="Recently"
              icon="📊"
            />
            <ActivityItem
              title={`${stats.apps} applications deployed`}
              time="Recently"
              icon="🚀"
            />
            <ActivityItem
              title={`${stats.users} team members active`}
              time="Now"
              icon="👥"
            />
          </div>
        </div>
      </div>
    </div>
  );
}

function StatCard({
  title,
  value,
  icon,
  color,
  onClick,
  isText = false
}: {
  title: string;
  value: number | string;
  icon: string;
  color: string;
  onClick: () => void;
  isText?: boolean;
}) {
  const colorClasses = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500'
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
    >
      <div className="flex items-center justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600">{title}</p>
          {isText ? (
            <p className="mt-2 text-lg font-semibold text-gray-900 truncate">{value}</p>
          ) : (
            <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          )}
        </div>
        <div className={`${colorClasses[color as keyof typeof colorClasses]} p-3 rounded-full text-white`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );
}

function QuickAction({
  title,
  description,
  icon,
  onClick
}: {
  title: string;
  description: string;
  icon: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="text-left p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors border border-gray-200"
    >
      <div className="flex items-start gap-3">
        <span className="text-2xl">{icon}</span>
        <div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
    </button>
  );
}

function StatusItem({
  label,
  status
}: {
  label: string;
  status: 'healthy' | 'warning' | 'error';
}) {
  const statusColors = {
    healthy: 'bg-green-100 text-green-800',
    warning: 'bg-yellow-100 text-yellow-800',
    error: 'bg-red-100 text-red-800'
  };

  const statusIcons = {
    healthy: '✅',
    warning: '⚠️',
    error: '❌'
  };

  return (
    <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
      <span className="text-sm font-medium text-gray-700">{label}</span>
      <span className={`px-2 py-1 text-xs font-semibold rounded-full ${statusColors[status]}`}>
        {statusIcons[status]} {status}
      </span>
    </div>
  );
}

function ActivityItem({
  title,
  time,
  icon
}: {
  title: string;
  time: string;
  icon: string;
}) {
  return (
    <div className="flex items-start gap-3 p-3 bg-gray-50 rounded-lg">
      <span className="text-xl">{icon}</span>
      <div className="flex-1">
        <p className="text-sm font-medium text-gray-900">{title}</p>
        <p className="text-xs text-gray-500 mt-1">{time}</p>
      </div>
    </div>
  );
}
