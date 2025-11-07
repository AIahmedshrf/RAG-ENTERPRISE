'use client';

import { useState, useEffect } from 'react';
import { useRouter, useParams } from 'next/navigation';

interface Dataset {
  id: string;
  name: string;
  description: string;
  indexing_technique: string;
  document_count?: number;
  created_at: string;
  updated_at: string;
}

interface Document {
  id: string;
  name: string;
  status: string;
  created_at: string;
}

export default function DatasetDetailsPage() {
  const router = useRouter();
  const params = useParams();
  const datasetId = params.id as string;

  const [dataset, setDataset] = useState<Dataset | null>(null);
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (datasetId) {
      fetchDatasetDetails();
    }
  }, [datasetId]);

  const fetchDatasetDetails = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('access_token');

      // Fetch dataset info
      const datasetRes = await fetch(`http://localhost:8000/api/v1/admin/datasets/${datasetId}`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (!datasetRes.ok) {
        throw new Error('Dataset not found');
      }

      const datasetData = await datasetRes.json();
      setDataset(datasetData);

      // Fetch documents
      const docsRes = await fetch(`http://localhost:8000/api/v1/admin/datasets/${datasetId}/documents`, {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (docsRes.ok) {
        const docsData = await docsRes.json();
        setDocuments(docsData.data || []);
      }

    } catch (err: any) {
      setError(err.message);
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

  if (error || !dataset) {
    return (
      <div className="p-6">
        <div className="bg-red-50 border border-red-200 rounded-lg p-4">
          <p className="text-red-600">⚠️ {error || 'Dataset not found'}</p>
        </div>
        <button
          onClick={() => router.push('/admin/datasets')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
        >
          ← Back to Datasets
        </button>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6">
        <button
          onClick={() => router.push('/admin/datasets')}
          className="text-blue-600 hover:text-blue-800 mb-4 flex items-center gap-2"
        >
          ← Back to Datasets
        </button>
        <h1 className="text-3xl font-bold text-gray-900">{dataset.name}</h1>
        <p className="text-gray-600 mt-2">{dataset.description}</p>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Documents</p>
          <p className="text-2xl font-bold text-gray-900">{dataset.document_count || documents.length || 0}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Indexing</p>
          <p className="text-lg font-semibold text-blue-600">{dataset.indexing_technique}</p>
        </div>
        <div className="bg-white p-4 rounded-lg shadow">
          <p className="text-sm text-gray-600">Created</p>
          <p className="text-sm text-gray-900">{new Date(dataset.created_at).toLocaleDateString()}</p>
        </div>
      </div>

      {/* Documents Section */}
      <div className="bg-white rounded-lg shadow">
        <div className="p-6 border-b border-gray-200">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-semibold">Documents</h2>
            <button
              onClick={() => alert('Upload document feature coming soon')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              + Upload Document
            </button>
          </div>
        </div>

        {documents.length === 0 ? (
          <div className="p-12 text-center">
            <p className="text-gray-500">No documents yet</p>
            <p className="text-sm text-gray-400 mt-2">Upload your first document to get started</p>
          </div>
        ) : (
          <div className="divide-y divide-gray-200">
            {documents.map((doc) => (
              <div key={doc.id} className="p-4 hover:bg-gray-50 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{doc.name}</p>
                  <p className="text-sm text-gray-500">
                    Added {new Date(doc.created_at).toLocaleDateString()}
                  </p>
                </div>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  doc.status === 'completed' 
                    ? 'bg-green-100 text-green-800'
                    : doc.status === 'processing'
                    ? 'bg-yellow-100 text-yellow-800'
                    : 'bg-gray-100 text-gray-800'
                }`}>
                  {doc.status}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Settings Section */}
      <div className="mt-6 bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold mb-4">Dataset Settings</h2>
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Dataset ID
            </label>
            <code className="block w-full px-3 py-2 bg-gray-50 rounded border text-sm">
              {dataset.id}
            </code>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Indexing Technique
            </label>
            <p className="text-sm text-gray-600">{dataset.indexing_technique}</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Last Updated
            </label>
            <p className="text-sm text-gray-600">{new Date(dataset.updated_at).toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  );
}
