// Adapted from Dify - Datasets Management
'use client';

import React, { useState, useEffect } from 'react';
import { Button } from '@/app/components/ui/button';
import { Modal } from '@/app/components/ui/modal';
import { Input } from '@/app/components/ui/input';
import { datasetsAPI } from '@/app/lib/api/datasets';

interface Dataset {
  id: string;
  name: string;
  description?: string;
  indexing_technique: string;
  document_count: number;
  created_at: string;
}

export const DatasetsList: React.FC = () => {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    indexing_technique: 'high_quality',
  });

  useEffect(() => {
    loadDatasets();
  }, []);

  const loadDatasets = async () => {
    try {
      setLoading(true);
      const data = await datasetsAPI.list();
      setDatasets(data);
    } catch (error) {
      console.error('Failed to load datasets:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateDataset = async () => {
    try {
      await datasetsAPI.create(formData);
      setShowCreateModal(false);
      setFormData({ name: '', description: '', indexing_technique: 'high_quality' });
      loadDatasets();
    } catch (error) {
      console.error('Failed to create dataset:', error);
    }
  };

  if (loading) {
    return <div className="flex justify-center p-8">Loading...</div>;
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">Knowledge Base</h2>
        <Button onClick={() => setShowCreateModal(true)}>
          Create Dataset
        </Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {datasets.map((dataset) => (
          <div
            key={dataset.id}
            className="border rounded-lg p-4 hover:shadow-lg transition-shadow"
          >
            <h3 className="font-semibold text-lg mb-2">{dataset.name}</h3>
            {dataset.description && (
              <p className="text-sm text-gray-600 mb-3">{dataset.description}</p>
            )}
            <div className="flex justify-between text-sm text-gray-500">
              <span>{dataset.document_count} documents</span>
              <span className="text-xs">{dataset.indexing_technique}</span>
            </div>
          </div>
        ))}
      </div>

      <Modal
        isOpen={showCreateModal}
        onClose={() => setShowCreateModal(false)}
        title="Create New Dataset"
      >
        <div className="space-y-4">
          <Input
            label="Dataset Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            placeholder="Enter dataset name"
          />
          
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
            <Button onClick={handleCreateDataset}>
              Create
            </Button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
