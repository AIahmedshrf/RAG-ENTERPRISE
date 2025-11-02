// Adapted from Dify - Apps Management
'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/app/components/ui/button';
import { Modal } from '@/app/components/ui/modal';
import { Input } from '@/app/components/ui/input';
import { appsAPI } from '@/app/lib/api/apps';

interface App {
  id: string;
  name: string;
  mode: string;
  description?: string;
  created_at: string;
}

export const AppsList: React.FC = () => {
  const [apps, setApps] = useState<App[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    mode: 'chat',
    description: '',
  });

  useEffect(() => {
    loadApps();
  }, []);

  const loadApps = async () => {
    try {
      setLoading(true);
      const data = await appsAPI.list();
      setApps(data);
    } catch (error) {
      console.error('Failed to load apps:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateApp = async () => {
    try {
      await appsAPI.create(formData);
      setShowCreateModal(false);
      setFormData({ name: '', mode: 'chat', description: '' });
      loadApps();
    } catch (error) {
      console.error('Failed to create app:', error);
    }
  };

  const handleDeleteApp = async (id: string) => {
    if (!confirm('Are you sure you want to delete this app?')) return;
    
    try {
      await appsAPI.delete(id);
      loadApps();
    } catch (error) {
      console.error('Failed to delete app:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Applications</h2>
        <Button onClick={() => setShowCreateModal(true)}>
          Create App
        </Button>
      </div>

      {/* Apps Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {apps.map((app) => (
          <div
            key={app.id}
            className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            <div className="flex justify-between items-start mb-2">
              <h3 className="font-semibold text-lg">{app.name}</h3>
              <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                {app.mode}
              </span>
            </div>
            {app.description && (
              <p className="text-sm text-gray-600 mb-3">{app.description}</p>
            )}
            <div className="flex justify-between items-center text-xs text-gray-500">
              <span>{new Date(app.created_at).toLocaleDateString()}</span>
              <button
                onClick={() => handleDeleteApp(app.id)}
                className="text-red-600 hover:text-red-800"
              >
                Delete
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* Create Modal */}
      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Application"
      >
        <div className="space-y-4">
          <Input
            label="App Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Enter app name"
          />
          
          <div>
            <label className="block text-sm font-medium mb-1">Mode</label>
            <select
              value={formData.mode}
              onChange={(e) => setFormData({ ...formData, mode: e.target.value })}
              className="w-full border rounded-md px-3 py-2"
            >
              <option value="chat">Chat</option>
              <option value="agent">Agent</option>
              <option value="workflow">Workflow</option>
            </select>
          </div>
          
          <Input
            label="Description (optional)"
            value={formData.description}
            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
            placeholder="Enter description"
          />
          
          <div className="flex justify-end gap-2">
            <Button variant="secondary" onClick={() => setShowCreateModal(false)}>
              Cancel
            </Button>
            <Button onClick={handleCreateApp}>
              Create
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
