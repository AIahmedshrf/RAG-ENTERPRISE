// Applications Management Page
import React from 'react';
import { AppsList } from '@/app/components/admin/apps-list';

export default function AppsPage() {
  return (
    <div>
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900">Applications</h1>
        <p className="mt-2 text-gray-600">Manage your AI applications and chatbots</p>
      </div>
      <AppsList />
    </div>
  );
}
