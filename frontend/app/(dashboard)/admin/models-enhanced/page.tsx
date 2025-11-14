'use client';

import React, { useEffect, useState } from 'react';
import StatCard from '@/app/components/admin/stat-card';
import Modal from '@/app/components/admin/modal';

interface Model {
  id: string;
  name: string;
  type: 'llm' | 'embedding' | 'reranker';
  provider: string;
  is_active: boolean;
  config?: Record<string, unknown>;
}

export default function ModelsPage() {
  const [models, setModels] = useState<Model[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showAddModal, setShowAddModal] = useState(false);
  const [formData, setFormData] = useState({ name: '', type: 'llm', provider: '' });

  const endpoint = (path: string) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${API_URL}${path}`;
  };

  useEffect(() => {
    fetchModels();
  }, []);

  const fetchModels = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint('/models'), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (res.ok) {
        const data = await res.json();
        setModels(Array.isArray(data) ? data : data.models || []);
      }
    } catch (error) {
      console.error('Failed to fetch models:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddModel = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const res = await fetch(endpoint('/models'), {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          ...(token && { Authorization: `Bearer ${token}` }),
        },
        body: JSON.stringify(formData),
      });
      if (res.ok) {
        setShowAddModal(false);
        setFormData({ name: '', type: 'llm', provider: '' });
        fetchModels();
      }
    } catch (error) {
      console.error('Failed to add model:', error);
    }
  };

  const llmModels = models.filter(m => m.type === 'llm');
  const embeddingModels = models.filter(m => m.type === 'embedding');
  const rerankerModels = models.filter(m => m.type === 'reranker');

  const stats = [
    { label: 'Total Models', value: models.length, icon: '🧠', bgColor: 'bg-blue-50' },
    { label: 'LLM Models', value: llmModels.length, icon: '💬', bgColor: 'bg-green-50' },
    { label: 'Embeddings', value: embeddingModels.length, icon: '📊', bgColor: 'bg-purple-50' },
    { label: 'Active Models', value: models.filter(m => m.is_active).length, icon: '✅', bgColor: 'bg-yellow-50' },
  ];

  const ModelSection = ({ title, models }: { title: string; models: Model[] }) => (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">{title}</h3>
      {models.length === 0 ? (
        <p className="text-gray-500 text-sm">No models configured yet</p>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {models.map((model) => (
            <div key={model.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
              <div className="flex items-start justify-between mb-2">
                <h4 className="font-semibold text-gray-900">{model.name}</h4>
                <span className={`px-2 py-1 rounded text-xs font-semibold ${
                  model.is_active ? 'bg-green-50 text-green-700' : 'bg-gray-50 text-gray-700'
                }`}>
                  {model.is_active ? 'Active' : 'Inactive'}
                </span>
              </div>
              <p className="text-sm text-gray-600 mb-3">{model.provider}</p>
              <div className="flex gap-2">
                <button className="flex-1 text-sm text-blue-600 hover:text-blue-700 font-medium">Configure</button>
                <button className="flex-1 text-sm text-green-600 hover:text-green-700 font-medium">Test</button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Models Management</h1>
          <p className="text-gray-600 mt-1">Configure LLMs, embeddings, and rerankers</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          ➕ Add Model
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatCard key={idx} {...stat} />
        ))}
      </div>

      {/* Model Sections */}
      <div className="space-y-6">
        <ModelSection title="Large Language Models (LLM)" models={llmModels} />
        <ModelSection title="Embedding Models" models={embeddingModels} />
        <ModelSection title="Reranker Models" models={rerankerModels} />
      </div>

      {/* Add Model Modal */}
      <Modal
        isOpen={showAddModal}
        title="Add New Model"
        onClose={() => setShowAddModal(false)}
        onConfirm={handleAddModel}
        confirmText="Add"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Model Name</label>
            <input
              type="text"
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              placeholder="e.g., GPT-4"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Type</label>
            <select
              value={formData.type}
              onChange={(e) => setFormData({ ...formData, type: e.target.value as 'llm' | 'embedding' | 'reranker' })}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="llm">LLM</option>
              <option value="embedding">Embedding</option>
              <option value="reranker">Reranker</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Provider</label>
            <input
              type="text"
              value={formData.provider}
              onChange={(e) => setFormData({ ...formData, provider: e.target.value })}
              placeholder="e.g., OpenAI"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </Modal>
    </div>
  );
}
