'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/auth-context';
import { useEffect } from 'react';

const navigation = [
  { name: 'Overview', href: '/admin', icon: '📊' },
  { name: 'Applications', href: '/admin/apps', icon: '🚀' },
  { name: 'Knowledge Base', href: '/admin/datasets', icon: '📚' },
  { name: 'AI Models', href: '/admin/models', icon: '🤖' },
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
  const router = useRouter();
  const { user, logout } = useAuth();

  useEffect(() => {
    if (user && !user.role_id?.includes('admin')) {
      router.push('/home');
    }
  }, [user, router]);

  if (!user || !user.role_id?.includes('admin')) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white shadow-lg">
        <div className="flex flex-col h-full">
          {/* Logo */}
          <div className="p-4 border-b">
            <h1 className="text-xl font-bold text-blue-600">RAG-ENTERPRISE</h1>
            <p className="text-xs text-gray-500 mt-1">Admin Panel</p>
          </div>

          {/* Navigation */}
          <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
            {navigation.map((item) => {
              const isActive = pathname === item.href || 
                (item.href !== '/admin' && pathname.startsWith(item.href));
              
              return (
                <button
                  key={item.name}
                  onClick={() => router.push(item.href)}
                  className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isActive
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-lg">{item.icon}</span>
                  <span>{item.name}</span>
                </button>
              );
            })}
          </nav>

          {/* User Info */}
          <div className="p-4 border-t">
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-900">{user.name}</p>
              <p className="text-xs text-gray-500">{user.email}</p>
            </div>
            <button
              onClick={logout}
              className="w-full px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 text-sm font-medium"
            >
              Logout
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {children}
      </div>
    </div>
  );
}
