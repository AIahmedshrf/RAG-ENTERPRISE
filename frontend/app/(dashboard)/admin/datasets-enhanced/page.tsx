'use client';

import React, { useEffect, useState } from 'react';
import StatCard from '@/app/components/admin/stat-card';
import DataTable from '@/app/components/admin/data-table';
import Modal from '@/app/components/admin/modal';

interface Dataset {
  id: string;
  name: string;
  description: string;
  size: number;
  documents: number;
  is_active: boolean;
  created_at: string;
}

export default function DatasetsPage() {
  const [datasets, setDatasets] = useState<Dataset[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedDataset, setSelectedDataset] = useState<Dataset | null>(null);
  const [formData, setFormData] = useState({ name: '', description: '' });

  const endpoint = (path: string) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${API_URL}${path}`;
  };

  useEffect(() => {
    fetchDatasets();
  }, []);

  const fetchDatasets = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint('/datasets'), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setDatasets(Array.isArray(data) ? data : data.datasets || []);
      }
    } catch (error) {
      console.error('Failed to fetch datasets:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddDataset = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint('/datasets'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        setShowAddModal(false);
        setFormData({ name: '', description: '' });
        fetchDatasets();
      }
    } catch (error) {
      console.error('Failed to add dataset:', error);
    }
  };

  const handleDeleteDataset = async () => {
    if (!selectedDataset) return;
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint(`/datasets/${selectedDataset.id}`), {
        method: 'DELETE',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        setDatasets(datasets.filter(d => d.id !== selectedDataset.id));
        setShowDeleteModal(false);
        setSelectedDataset(null);
      }
    } catch (error) {
      console.error('Failed to delete dataset:', error);
    }
  };

  const stats = [
    {
      label: 'Total Datasets',
      value: datasets.length,
      icon: '📦',
      bgColor: 'bg-blue-50',
    },
    {
      label: 'Total Documents',
      value: datasets.reduce((sum, d) => sum + d.documents, 0),
      icon: '📄',
      bgColor: 'bg-green-50',
    },
    {
      label: 'Total Size',
      value: `${(datasets.reduce((sum, d) => sum + d.size, 0) / 1024 / 1024).toFixed(2)} MB`,
      icon: '💾',
      bgColor: 'bg-purple-50',
    },
    {
      label: 'Active',
      value: datasets.filter(d => d.is_active).length,
      icon: '✅',
      bgColor: 'bg-yellow-50',
    },
  ];

  const tableColumns: Array<any> = [
    { header: 'Dataset Name', accessor: 'name' as const, width: 'w-1/3' },
    { header: 'Documents', accessor: 'documents' as const },
    { header: 'Size', accessor: (d: Dataset) => `${(d.size / 1024 / 1024).toFixed(2)} MB` },
    { header: 'Status', accessor: (d: Dataset) => (
      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
        d.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-700'
      }`}>
        {d.is_active ? 'Active' : 'Inactive'}
      </span>
    ) },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Datasets Management</h1>
          <p className="text-gray-600 mt-1">Manage data collections and resources</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          ➕ Create Dataset
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatCard key={idx} {...stat} />
        ))}
      </div>

      {/* Table */}
      <DataTable<Dataset>
        columns={tableColumns}
        data={datasets}
        isLoading={isLoading}
        emptyMessage="No datasets yet. Create your first dataset!"
        onRowClick={(dataset) => setSelectedDataset(dataset)}
        actions={(dataset) => (
          <div className="flex gap-2">
            <button className="text-blue-600 hover:text-blue-700 text-sm font-medium">
              View
            </button>
            <button
              onClick={() => {
                setSelectedDataset(dataset);
                setShowDeleteModal(true);
              }}
              className="text-red-600 hover:text-red-700 text-sm font-medium"
            >
              Delete
            </button>
          </div>
        )}
      />

      {/* Add Dataset Modal */}
      <Modal
        isOpen={showAddModal}
        title="Create New Dataset"
        onClose={() => setShowAddModal(false)}
        onConfirm={handleAddDataset}
        confirmText="Create"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Dataset Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., Customer Data"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              placeholder="Dataset description..."
              rows={4}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </Modal>

      {/* Delete Modal */}
      <Modal
        isOpen={showDeleteModal}
        title="Delete Dataset?"
        onClose={() => setShowDeleteModal(false)}
        onConfirm={handleDeleteDataset}
        confirmText="Delete"
        isDangerous={true}
      >
        <p>Are you sure you want to delete <strong>{selectedDataset?.name}</strong>? This action cannot be undone.</p>
      </Modal>
    </div>
  );
}
