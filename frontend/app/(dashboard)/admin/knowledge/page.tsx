'use client';

import React, { useEffect, useState } from 'react';
import { endpoint } from '@/app/lib/api-constants';

interface KnowledgeStats {
  total_documents: number;
  total_segments: number;
  recent_uploads: number;
  processing_jobs: number;
}

interface RecentDocument {
  id: string;
  name: string;
  status: string;
  uploaded_at: string;
  segment_count: number;
}

export default function KnowledgeBaseAdminPage() {
  const [stats, setStats] = useState<KnowledgeStats>({
    total_documents: 0,
    total_segments: 0,
    recent_uploads: 0,
    processing_jobs: 0,
  });
  const [documents, setDocuments] = useState<RecentDocument[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem('access_token');
        
        // Fetch documents
        const docsRes = await fetch(endpoint('/knowledge/documents'), {
          headers: token ? { Authorization: `Bearer ${token}` } : undefined,
        });
        
        if (docsRes.ok) {
          const docsData = await docsRes.json();
          const docs = docsData.documents || [];
          setDocuments(docs.slice(0, 10)); // Recent 10
          
          // Calculate stats
          setStats({
            total_documents: docs.length,
            total_segments: docs.reduce((sum: number, d: any) => sum + (d.segment_count || 0), 0),
            recent_uploads: docs.filter((d: any) => {
              const uploaded = new Date(d.uploaded_at || d.created_at);
              const dayAgo = new Date(Date.now() - 24 * 60 * 60 * 1000);
              return uploaded > dayAgo;
            }).length,
            processing_jobs: docs.filter((d: any) => d.status === 'processing').length,
          });
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div className="text-center py-8">Loading Knowledge Base...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">📄 Knowledge Base Management</h1>
        <p className="text-gray-600 mt-1">Manage documents, search, and knowledge indexing</p>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
          {error}
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <StatCard
          title="Total Documents"
          value={stats.total_documents}
          icon="📋"
          color="blue"
        />
        <StatCard
          title="Total Segments"
          value={stats.total_segments}
          icon="🔗"
          color="green"
        />
        <StatCard
          title="Uploaded (24h)"
          value={stats.recent_uploads}
          icon="⬆️"
          color="orange"
        />
        <StatCard
          title="Processing"
          value={stats.processing_jobs}
          icon="⚙️"
          color="purple"
        />
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <ActionCard
          title="Upload Document"
          description="Add new document to knowledge base"
          icon="⬆️"
          href="/admin/knowledge/upload"
        />
        <ActionCard
          title="Search Knowledge"
          description="Search across all documents"
          icon="🔍"
          href="/admin/knowledge/search"
        />
        <ActionCard
          title="View All Documents"
          description="Browse and manage documents"
          icon="📋"
          href="/admin/knowledge/documents"
        />
      </div>

      {/* Recent Documents */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Recent Documents</h2>
        </div>
        
        {documents.length === 0 ? (
          <div className="px-6 py-8 text-center text-gray-500">
            No documents yet. <a href="/admin/knowledge/upload" className="text-blue-600 hover:underline">Upload one now</a>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 border-b border-gray-200">
                <tr>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Name</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Status</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Segments</th>
                  <th className="px-6 py-3 text-left text-sm font-medium text-gray-700">Uploaded</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {documents.map((doc) => (
                  <tr key={doc.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{doc.name}</td>
                    <td className="px-6 py-4 text-sm">
                      <StatusBadge status={doc.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">{doc.segment_count || 0}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {new Date(doc.uploaded_at).toLocaleDateString()}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}

function StatCard({ title, value, icon, color }: any) {
  const colorClass = {
    blue: 'bg-blue-50 border-blue-200',
    green: 'bg-green-50 border-green-200',
    orange: 'bg-orange-50 border-orange-200',
    purple: 'bg-purple-50 border-purple-200',
  }[color] || 'bg-gray-50 border-gray-200';

  return (
    <div className={`${colorClass} border rounded-lg p-4`}>
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
        </div>
        <div className="text-3xl">{icon}</div>
      </div>
    </div>
  );
}

function ActionCard({ title, description, icon, href }: any) {
  return (
    <a
      href={href}
      className="block bg-white border border-gray-200 rounded-lg p-4 hover:shadow-lg hover:border-blue-400 transition-all"
    >
      <div className="text-3xl mb-2">{icon}</div>
      <h3 className="font-semibold text-gray-900">{title}</h3>
      <p className="text-sm text-gray-600 mt-1">{description}</p>
    </a>
  );
}

function StatusBadge({ status }: any) {
  const statusConfig: any = {
    completed: { bg: 'bg-green-100', text: 'text-green-800' },
    processing: { bg: 'bg-yellow-100', text: 'text-yellow-800' },
    uploading: { bg: 'bg-blue-100', text: 'text-blue-800' },
    error: { bg: 'bg-red-100', text: 'text-red-800' },
  };

  const config = statusConfig[status] || { bg: 'bg-gray-100', text: 'text-gray-800' };

  return (
    <span className={`px-3 py-1 rounded-full text-xs font-medium ${config.bg} ${config.text}`}>
      {status}
    </span>
  );
}
