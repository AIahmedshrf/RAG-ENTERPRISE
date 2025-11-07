'use client';

import { useState } from 'react';

interface ModelConfig {
  id: string;
  name: string;
  provider: 'openai' | 'azure' | 'local';
  model: string;
  apiKey?: string;
  endpoint?: string;
  status: 'active' | 'inactive';
}

const PROVIDERS = [
  { value: 'openai', label: 'OpenAI', icon: '🤖' },
  { value: 'azure', label: 'Azure OpenAI', icon: '☁️' },
  { value: 'local', label: 'Local Model', icon: '💻' }
];

const OPENAI_MODELS = [
  'gpt-4',
  'gpt-4-turbo',
  'gpt-3.5-turbo',
  'text-embedding-ada-002'
];

export default function ModelsPage() {
  const [models, setModels] = useState<ModelConfig[]>([
    {
      id: '1',
      name: 'Default GPT-4',
      provider: 'openai',
      model: 'gpt-4',
      status: 'active'
    }
  ]);
  const [showAddModal, setShowAddModal] = useState(false);

  const handleAddModel = (config: Omit<ModelConfig, 'id'>) => {
    const newModel: ModelConfig = {
      ...config,
      id: Date.now().toString()
    };
    setModels([...models, newModel]);
    setShowAddModal(false);
    alert('✅ Model configuration added successfully!');
  };

  const handleDeleteModel = (id: string) => {
    if (confirm('Are you sure you want to delete this model configuration?')) {
      setModels(models.filter(m => m.id !== id));
      alert('✅ Model deleted successfully!');
    }
  };

  const handleToggleStatus = (id: string) => {
    setModels(models.map(m =>
      m.id === id ? { ...m, status: m.status === 'active' ? 'inactive' : 'active' } : m
    ));
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">🤖 AI Models</h1>
          <p className="text-sm text-gray-500 mt-1">Configure AI models and providers</p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 flex items-center gap-2"
        >
          <span>+</span>
          <span>Add Model</span>
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Total Models</p>
          <p className="text-2xl font-bold text-gray-900">{models.length}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Active</p>
          <p className="text-2xl font-bold text-green-600">
            {models.filter(m => m.status === 'active').length}
          </p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Providers</p>
          <p className="text-2xl font-bold text-blue-600">
            {new Set(models.map(m => m.provider)).size}
          </p>
        </div>
      </div>

      {/* Models List */}
      <div className="bg-white rounded-lg shadow">
        <table className="min-w-full divide-y divide-gray-200">
          <thead className="bg-gray-50">
            <tr>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Model
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Provider
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Status
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                Actions
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {models.map(model => (
              <tr key={model.id} className="hover:bg-gray-50">
                <td className="px-6 py-4">
                  <div>
                    <div className="font-medium text-gray-900">{model.name}</div>
                    <div className="text-sm text-gray-500">{model.model}</div>
                  </div>
                </td>
                <td className="px-6 py-4">
                  <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                    {PROVIDERS.find(p => p.value === model.provider)?.icon}{' '}
                    {model.provider}
                  </span>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => handleToggleStatus(model.id)}
                    className={`px-2 py-1 text-xs rounded-full ${
                      model.status === 'active'
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}
                  >
                    {model.status}
                  </button>
                </td>
                <td className="px-6 py-4">
                  <button
                    onClick={() => handleDeleteModel(model.id)}
                    className="text-red-600 hover:text-red-900 text-sm"
                  >
                    Delete
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {showAddModal && (
        <AddModelModal
          onClose={() => setShowAddModal(false)}
          onAdd={handleAddModel}
        />
      )}
    </div>
  );
}

function AddModelModal({
  onClose,
  onAdd
}: {
  onClose: () => void;
  onAdd: (config: Omit<ModelConfig, 'id'>) => void;
}) {
  const [name, setName] = useState('');
  const [provider, setProvider] = useState<'openai' | 'azure' | 'local'>('openai');
  const [model, setModel] = useState('gpt-4');
  const [apiKey, setApiKey] = useState('');
  const [endpoint, setEndpoint] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!name || !model) {
      alert('Please fill in required fields');
      return;
    }

    onAdd({
      name,
      provider,
      model,
      apiKey: apiKey || undefined,
      endpoint: endpoint || undefined,
      status: 'active'
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Add AI Model</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Configuration Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              placeholder="My GPT-4 Config"
              required
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Provider *
            </label>
            <select
              value={provider}
              onChange={(e) => setProvider(e.target.value as any)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
            >
              {PROVIDERS.map(p => (
                <option key={p.value} value={p.value}>
                  {p.icon} {p.label}
                </option>
              ))}
            </select>
          </div>

          {provider === 'openai' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Model *
              </label>
              <select
                value={model}
                onChange={(e) => setModel(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
              >
                {OPENAI_MODELS.map(m => (
                  <option key={m} value={m}>{m}</option>
                ))}
              </select>
            </div>
          )}

          {provider !== 'local' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                API Key
              </label>
              <input
                type="password"
                value={apiKey}
                onChange={(e) => setApiKey(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="sk-..."
              />
            </div>
          )}

          {provider === 'azure' && (
            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Endpoint URL
              </label>
              <input
                type="url"
                value={endpoint}
                onChange={(e) => setEndpoint(e.target.value)}
                className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500"
                placeholder="https://..."
              />
            </div>
          )}

          <div className="bg-yellow-50 border border-yellow-200 rounded p-3 mb-4">
            <p className="text-sm text-yellow-800">
              ℹ️ Model configurations are stored locally. API keys are not sent to the server.
            </p>
          </div>

          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Add Model
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
