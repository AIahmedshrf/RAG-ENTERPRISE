// Workspace Settings Page
'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/app/components/ui/button';
import { Input } from '@/app/components/ui/input';

export default function WorkspacePage() {
  const [workspace, setWorkspace] = useState({
    name: '',
    id: '',
  });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadWorkspace();
  }, []);

  const loadWorkspace = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/v1/admin/workspace');
      const data = await response.json();
      setWorkspace(data);
    } catch (error) {
      console.error('Failed to load workspace:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleSave = async () => {
    try {
      await fetch('/api/v1/admin/workspace', {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name: workspace.name }),
      });
      alert('Workspace updated successfully');
    } catch (error) {
      console.error('Failed to update workspace:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Workspace Settings</h1>
        <p className="mt-2 text-gray-600">Configure your workspace settings</p>
      </div>

      <div className="bg-white rounded-lg border border-gray-200 p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold mb-4">General Settings</h3>
          <div className="space-y-4 max-w-xl">
            <Input
              label="Workspace Name"
              value={workspace.name}
              onChange={(e) => setWorkspace({ ...workspace, name: e.target.value })}
              placeholder="Enter workspace name"
            />
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Workspace ID
              </label>
              <p className="text-sm text-gray-600 font-mono bg-gray-50 p-2 rounded">
                {workspace.id}
              </p>
            </div>
          </div>
        </div>

        <div className="flex justify-end">
          <Button onClick={handleSave}>
            Save Changes
          </Button>
        </div>
      </div>

      {/* Danger Zone */}
      <div className="bg-white rounded-lg border border-red-200 p-6">
        <h3 className="text-lg font-semibold text-red-900 mb-2">Danger Zone</h3>
        <p className="text-sm text-gray-600 mb-4">
          These actions are irreversible. Please be careful.
        </p>
        <Button variant="danger">
          Delete Workspace
        </Button>
      </div>
    </div>
  );
}
