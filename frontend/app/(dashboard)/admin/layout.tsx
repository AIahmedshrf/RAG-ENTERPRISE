'use client';

import { useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/auth-context';
import { useEffect, useState } from 'react';
import Sidebar from '@/app/components/admin/sidebar';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const router = useRouter();
  const { user, isAdmin } = useAuth();
  const [isCollapsed, setIsCollapsed] = useState(false);

  useEffect(() => {
    if (user && !isAdmin) {
      router.push('/home');
    }
  }, [user, isAdmin, router]);

  if (!user || !isAdmin) {
    return <div className="flex items-center justify-center min-h-screen text-gray-500">Redirecting...</div>;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <Sidebar collapsed={isCollapsed} />

      {/* Main Content */}
      <div className={`transition-all duration-300 ${
        isCollapsed ? 'ml-20' : 'ml-64'
      }`}>
        {/* Top Bar */}
        <div className="bg-white border-b px-6 py-4 sticky top-0 z-10">
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-2 hover:bg-gray-100 rounded transition-colors"
            title={isCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
          >
            {isCollapsed ? '▶️' : '◀️'}
          </button>
        </div>

        {/* Content */}
        <div className="p-6">
          {children}
        </div>
      </div>
    </div>
  );
}
