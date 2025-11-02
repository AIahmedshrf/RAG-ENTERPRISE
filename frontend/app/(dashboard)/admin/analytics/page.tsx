// Analytics Page
'use client';

import React from 'react';

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">Analytics</h1>
        <p className="mt-2 text-gray-600">Track usage and performance metrics</p>
      </div>

      {/* Charts Placeholder */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-white rounded-lg border border-gray-200 p-6 h-80">
          <h3 className="text-lg font-semibold mb-4">Messages Over Time</h3>
          <div className="flex items-center justify-center h-full text-gray-400">
            📊 Chart placeholder
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 h-80">
          <h3 className="text-lg font-semibold mb-4">User Activity</h3>
          <div className="flex items-center justify-center h-full text-gray-400">
            📈 Chart placeholder
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 h-80">
          <h3 className="text-lg font-semibold mb-4">Popular Applications</h3>
          <div className="flex items-center justify-center h-full text-gray-400">
            🎯 Chart placeholder
          </div>
        </div>
        
        <div className="bg-white rounded-lg border border-gray-200 p-6 h-80">
          <h3 className="text-lg font-semibold mb-4">Knowledge Base Usage</h3>
          <div className="flex items-center justify-center h-full text-gray-400">
            📚 Chart placeholder
          </div>
        </div>
      </div>
    </div>
  );
}
