// Admin Dashboard Layout
'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const navigation = [
  { name: 'Overview', href: '/admin', icon: '📊' },
  { name: 'Applications', href: '/admin/apps', icon: '🚀' },
  { name: 'Knowledge Base', href: '/admin/datasets', icon: '📚' },
  { name: 'Users', href: '/admin/users', icon: '👥' },
  { name: 'Workspace', href: '/admin/workspace', icon: '⚙️' },
  { name: 'Analytics', href: '/admin/analytics', icon: '📈' },
];

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-gray-50" dir="ltr">
      {/* Sidebar */}
      <div className="w-64 bg-white border-r border-gray-200">
        {/* Logo */}
        <div className="h-16 flex items-center px-6 border-b border-gray-200">
          <h1 className="text-xl font-bold text-gray-900">RAG Admin</h1>
        </div>

        {/* Navigation */}
        <nav className="p-4 space-y-1">
          {navigation.map((item) => {
            const isActive = pathname === item.href;
            return (
              <Link
                key={item.name}
                href={item.href}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-lg text-sm font-medium transition-colors
                  ${isActive 
                    ? 'bg-blue-50 text-blue-700' 
                    : 'text-gray-700 hover:bg-gray-50'
                  }
                `}
              >
                <span className="text-xl">{item.icon}</span>
                {item.name}
              </Link>
            );
          })}
        </nav>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-auto">
        {/* Header */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-8">
          <div className="flex items-center gap-4">
            <h2 className="text-lg font-semibold text-gray-900">Admin Dashboard</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <button className="text-gray-600 hover:text-gray-900">
              🔔
            </button>
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                A
              </div>
              <span className="text-sm font-medium">Admin</span>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="p-8">
          {children}
        </main>
      </div>
    </div>
  );
}
