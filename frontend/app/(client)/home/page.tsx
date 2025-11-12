'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/auth-context';

interface Stats {
  datasets: number;
  apps: number;
  conversations: number;
  documents: number;
}

export default function HomePage() {
  const router = useRouter();
  const { user, loading } = useAuth();
  const [stats, setStats] = useState<Stats>({
    datasets: 0,
    apps: 0,
    conversations: 0,
    documents: 0,
  });
  const [loadingStats, setLoadingStats] = useState(true);

  useEffect(() => {
    if (!loading && !user) {
      router.push('/login');
    }
  }, [user, loading, router]);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const token = localStorage.getItem('access_token');
        if (!token) return;

        // Fetch datasets count
        const datasetsRes = await fetch('http://localhost:8000/admin/datasets', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const datasetsData = datasetsRes.ok ? await datasetsRes.json() : { total: 0 };

        // Fetch apps count
        const appsRes = await fetch('http://localhost:8000/admin/apps', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const appsData = appsRes.ok ? await appsRes.json() : { total: 0 };

        // Fetch conversations count
        const conversationsRes = await fetch('http://localhost:8000/conversations', {
          headers: { Authorization: `Bearer ${token}` },
        });
        const conversationsData = conversationsRes.ok ? await conversationsRes.json() : [];

        setStats({
          datasets: datasetsData?.total || 0,
          apps: appsData?.total || 0,
          conversations: Array.isArray(conversationsData) ? conversationsData.length : 0,
          documents: 0,
        });
      } catch (error) {
        console.error('Error fetching stats:', error);
        // Set default values on error
        setStats({
          datasets: 0,
          apps: 0,
          conversations: 0,
          documents: 0,
        });
      } finally {
        setLoadingStats(false);
      }
    };

    if (user) {
      fetchStats();
    }
  }, [user]);

  if (loading || !user) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">
                Welcome back, {user.name}! 👋
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                {user.role_id?.includes('admin') ? 'Administrator Dashboard' : 'User Dashboard'}
              </p>
            </div>
            <div className="flex items-center gap-4">
              <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium">
                {user.role_id?.includes('admin') ? 'Admin' : 'User'}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Grid */}
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4 mb-8">
          <StatCard
            title="Datasets"
            value={stats.datasets}
            icon="📊"
            color="blue"
            loading={loadingStats}
            onClick={() => router.push('/admin/datasets')}
          />
          <StatCard
            title="Applications"
            value={stats.apps}
            icon="🤖"
            color="purple"
            loading={loadingStats}
            onClick={() => router.push('/admin/apps')}
          />
          <StatCard
            title="Conversations"
            value={stats.conversations}
            icon="💬"
            color="green"
            loading={loadingStats}
            onClick={() => router.push('/chat')}
          />
          <StatCard
            title="Documents"
            value={stats.documents}
            icon="📄"
            color="yellow"
            loading={loadingStats}
            onClick={() => router.push('/documents')}
          />
        </div>

        {/* Quick Actions */}
        <div className="bg-white rounded-lg shadow p-6 mb-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            <QuickAction
              title="New Chat"
              description="Start a conversation with AI"
              icon="💬"
              onClick={() => router.push('/chat')}
            />
            <QuickAction
              title="Upload Document"
              description="Add documents to knowledge base"
              icon="📤"
              onClick={() => router.push('/documents')}
            />
            {user.role_id?.includes('admin') && (
              <QuickAction
                title="Create App"
                description="Build a new AI application"
                icon="🚀"
                onClick={() => router.push('/admin/apps')}
              />
            )}
            <QuickAction
              title="Financial Analysis"
              description="Analyze financial data"
              icon="💰"
              onClick={() => router.push('/financial')}
            />
            {user.role_id?.includes('admin') && (
              <QuickAction
                title="Analytics"
                description="View system analytics"
                icon="📈"
                onClick={() => router.push('/admin/analytics')}
              />
            )}
            {user.role_id?.includes('admin') && (
              <QuickAction
                title="Workspace Settings"
                description="Manage workspace"
                icon="⚙️"
                onClick={() => router.push('/admin/workspace')}
              />
            )}
          </div>
        </div>

        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Recent Activity</h2>
          <div className="space-y-4">
            <ActivityItem
              title="Welcome to RAG-ENTERPRISE"
              description="Your intelligent AI platform is ready to use"
              time="Just now"
              icon="🎉"
            />
            <ActivityItem
              title="System Status"
              description="All systems operational"
              time="2 minutes ago"
              icon="✅"
            />
          </div>
        </div>
      </main>
    </div>
  );
}

// Stat Card Component
function StatCard({
  title,
  value,
  icon,
  color,
  loading,
  onClick,
}: {
  title: string;
  value: number;
  icon: string;
  color: string;
  loading: boolean;
  onClick: () => void;
}) {
  const colorClasses = {
    blue: 'bg-blue-500',
    purple: 'bg-purple-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-500',
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg shadow p-6 cursor-pointer hover:shadow-lg transition-shadow"
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          {loading ? (
            <div className="mt-2 h-8 w-16 bg-gray-200 animate-pulse rounded"></div>
          ) : (
            <p className="mt-2 text-3xl font-bold text-gray-900">{value}</p>
          )}
        </div>
        <div className={`${colorClasses[color as keyof typeof colorClasses]} p-3 rounded-full`}>
          <span className="text-2xl">{icon}</span>
        </div>
      </div>
    </div>
  );
}

// Quick Action Component
function QuickAction({
  title,
  description,
  icon,
  onClick,
}: {
  title: string;
  description: string;
  icon: string;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className="text-left p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
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

// Activity Item Component
function ActivityItem({
  title,
  description,
  time,
  icon,
}: {
  title: string;
  description: string;
  time: string;
  icon: string;
}) {
  return (
    <div className="flex items-start gap-4 p-4 bg-gray-50 rounded-lg">
      <span className="text-2xl">{icon}</span>
      <div className="flex-1">
        <h4 className="font-medium text-gray-900">{title}</h4>
        <p className="text-sm text-gray-600 mt-1">{description}</p>
        <p className="text-xs text-gray-400 mt-2">{time}</p>
      </div>
    </div>
  );
}
