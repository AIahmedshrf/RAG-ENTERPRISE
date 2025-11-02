// Knowledge Base Management Page
import React from 'react';
import { DatasetsList } from '@/app/components/admin/datasets-list';

export default function DatasetsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Knowledge Base</h1>
        <p className="mt-2 text-gray-600">Manage datasets and documents</p>
      </div>
      <DatasetsList />
    </div>
  );
}
