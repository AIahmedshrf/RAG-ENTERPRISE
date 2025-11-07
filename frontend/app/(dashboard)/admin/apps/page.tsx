'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/contexts/auth-context';

interface App {
  id: string;
  name: string;
  mode: string;
  icon: string;
  description: string;
  created_at: string;
  updated_at: string;
}

const APP_MODES = [
  { value: 'chat', label: 'Chat', icon: '💬', description: 'Conversational interface' },
  { value: 'agent', label: 'Agent', icon: '🤖', description: 'Autonomous AI agent' },
  { value: 'workflow', label: 'Workflow', icon: '⚡', description: 'Multi-step automation' },
  { value: 'completion', label: 'Completion', icon: '✨', description: 'Text completion' },
];

const ICON_OPTIONS = ['🤖', '💬', '🎧', '💰', '🔬', '📊', '🚀', '⚡', '✨', '🎯', '📚', '🔮'];

export default function AppsPage() {
  const { user } = useAuth();
  const [apps, setApps] = useState<App[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [editingApp, setEditingApp] = useState<App | null>(null);

  useEffect(() => {
    fetchApps();
  }, []);

  const fetchApps = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:8000/api/v1/admin/apps', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const data = await response.json();
      setApps(data.data || []);
    } catch (err: any) {
      setError(err.message);
      console.error('Error fetching apps:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApp = async (name: string, mode: string, icon: string, description: string) => {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:8000/api/v1/admin/apps', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, mode, icon, description }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to create app');
      }

      const result = await response.json();
      alert(`✅ ${result.message || 'App created successfully!'}`);
      await fetchApps();
      setShowCreateModal(false);
    } catch (err: any) {
      alert(`❌ Error: ${err.message}`);
      console.error('Create error:', err);
    }
  };

  const handleUpdateApp = async (appId: string, name: string, icon: string, description: string) => {
    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/apps/${appId}`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ name, icon, description }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update app');
      }

      alert('✅ App updated successfully!');
      await fetchApps();
      setEditingApp(null);
    } catch (err: any) {
      alert(`❌ Error: ${err.message}`);
    }
  };

  const handleDeleteApp = async (appId: string, appName: string) => {
    if (!confirm(`Are you sure you want to delete "${appName}"?`)) return;

    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/apps/${appId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        throw new Error('Failed to delete app');
      }

      alert('✅ App deleted successfully!');
      await fetchApps();
    } catch (err: any) {
      alert(`❌ Error: ${err.message}`);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading applications...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🚀 Applications</h1>
          <p className="text-sm text-gray-500 mt-1">Create and manage AI-powered applications</p>
        </div>
        <button
          onClick={() => setShowCreateModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <span>+</span>
          <span>Create App</span>
        </button>
      </div>

      {/* Error */}
      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg">
          <p className="text-red-600">⚠️ {error}</p>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Total Apps</p>
          <p className="text-2xl font-bold text-gray-900">{apps.length}</p>
        </div>
        {APP_MODES.map(mode => (
          <div key={mode.value} className="bg-white p-4 rounded-lg shadow">
            <p className="text-sm text-gray-600">{mode.label}</p>
            <p className="text-2xl font-bold text-blue-600">
              {apps.filter(a => a.mode === mode.value).length}
            </p>
          </div>
        ))}
      </div>

      {/* Apps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {apps.length === 0 ? (
          <div className="col-span-full bg-white rounded-lg shadow p-8 text-center">
            <p className="text-gray-500">No applications found. Create your first one!</p>
          </div>
        ) : (
          apps.map((app) => (
            <div key={app.id} className="bg-white rounded-lg shadow p-6 hover:shadow-lg transition-shadow">
              <div className="flex items-start justify-between mb-3">
                <div className="flex items-center gap-3">
                  <span className="text-3xl">{app.icon}</span>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{app.name}</h3>
                    <span className="text-xs text-gray-500 uppercase">{app.mode}</span>
                  </div>
                </div>
              </div>
              <p className="text-sm text-gray-600 mb-4">
                {app.description || 'No description'}
              </p>
              <div className="flex items-center justify-between text-xs text-gray-500 mb-4">
                <span>Created: {new Date(app.created_at).toLocaleDateString()}</span>
              </div>
              <div className="flex gap-2">
                <button
                  onClick={() => setEditingApp(app)}
                  className="flex-1 px-3 py-2 bg-blue-50 text-blue-600 rounded hover:bg-blue-100 text-sm"
                >
                  Edit
                </button>
                <button
                  onClick={() => handleDeleteApp(app.id, app.name)}
                  className="px-3 py-2 bg-red-50 text-red-600 rounded hover:bg-red-100 text-sm"
                >
                  Delete
                </button>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Create Modal */}
      {showCreateModal && (
        <CreateAppModal
          onClose={() => setShowCreateModal(false)}
          onCreate={handleCreateApp}
        />
      )}

      {/* Edit Modal */}
      {editingApp && (
        <EditAppModal
          app={editingApp}
          onClose={() => setEditingApp(null)}
          onUpdate={handleUpdateApp}
        />
      )}
    </div>
  );
}

function CreateAppModal({
  onClose,
  onCreate,
}: {
  onClose: () => void;
  onCreate: (name: string, mode: string, icon: string, description: string) => void;
}) {
  const [name, setName] = useState('');
  const [mode, setMode] = useState('chat');
  const [icon, setIcon] = useState('🤖');
  const [description, setDescription] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name) {
      alert('Please enter an app name');
      return;
    }

    setLoading(true);
    try {
      await onCreate(name, mode, icon, description);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <h2 className="text-xl font-bold mb-4">Create New Application</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              App Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="My AI App"
              required
            />
          </div>
          
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              App Type *
            </label>
            <select
              value={mode}
              onChange={(e) => setMode(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {APP_MODES.map(m => (
                <option key={m.value} value={m.value}>
                  {m.icon} {m.label} - {m.description}
                </option>
              ))}
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Icon
            </label>
            <div className="grid grid-cols-6 gap-2">
              {ICON_OPTIONS.map(i => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setIcon(i)}
                  className={`text-2xl p-2 rounded border-2 hover:bg-gray-50 ${
                    icon === i ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  {i}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="App description..."
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? 'Creating...' : 'Create App'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

function EditAppModal({
  app,
  onClose,
  onUpdate,
}: {
  app: App;
  onClose: () => void;
  onUpdate: (appId: string, name: string, icon: string, description: string) => void;
}) {
  const [name, setName] = useState(app.name);
  const [icon, setIcon] = useState(app.icon);
  const [description, setDescription] = useState(app.description);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    setLoading(true);
    try {
      await onUpdate(app.id, name, icon, description);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Edit Application</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              App Name
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Icon
            </label>
            <div className="grid grid-cols-6 gap-2">
              {ICON_OPTIONS.map(i => (
                <button
                  key={i}
                  type="button"
                  onClick={() => setIcon(i)}
                  className={`text-2xl p-2 rounded border-2 hover:bg-gray-50 ${
                    icon === i ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
                  }`}
                >
                  {i}
                </button>
              ))}
            </div>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Description
            </label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
              rows={3}
            />
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? 'Saving...' : 'Save Changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
