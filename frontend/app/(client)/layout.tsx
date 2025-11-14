'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LanguageSwitcher } from '@/app/components/ui/language-switcher';
import { useAuth } from '@/app/contexts/auth-context';
import { ProtectedRoute } from '@/app/components/auth/protected-route';

const navigation = [
  { name: 'Home', href: '/home', icon: '🏠' },
  { name: 'Chat', href: '/chat', icon: '💬' },
  { name: 'Documents', href: '/documents', icon: '📄' },
  { name: 'Quotes', href: '/quotes', icon: '💭' },
  { name: 'Financial', href: '/financial', icon: '💰' },
];

const adminNavigation = [
  { name: 'Dashboard', href: '/admin', icon: '📊' },
  { name: 'Knowledge Base', href: '/admin/knowledge', icon: '📚' },
  { name: 'Agents', href: '/admin/agents', icon: '🤖' },
  { name: 'Models', href: '/admin/models', icon: '🧠' },
  { name: 'Datasets', href: '/admin/datasets', icon: '📦' },
  { name: 'Users', href: '/admin/users', icon: '👥' },
  { name: 'Settings', href: '/admin/settings', icon: '⚙️' },
];

const adminMenuItems = [
  { name: 'Dashboard', href: '/admin', icon: '📊' },
  { name: 'Knowledge Base', href: '/admin/knowledge', icon: '📄' },
  { name: 'Agents', href: '/admin/agents', icon: '🤖' },
  { name: 'Models', href: '/admin/models', icon: '🧠' },
  { name: 'Datasets', href: '/admin/datasets', icon: '📦' },
  { name: 'Users', href: '/admin/users', icon: '👥' },
  { name: 'Settings', href: '/admin/settings', icon: '⚙️' },
];

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();
  const { user, logout, isAdmin } = useAuth();
  const [showAdminMenu, setShowAdminMenu] = useState(false);

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
        <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              <div className="flex items-center gap-8">
                <Link href="/home" className="flex items-center gap-2">
                  <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                    <span className="text-white text-xl font-bold">R</span>
                  </div>
                  <span className="text-xl font-bold text-gray-900">RAG-ENTERPRISE</span>
                </Link>

                <nav className="hidden md:flex items-center gap-1">
                  {navigation.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                      <Link
                        key={item.name}
                        href={item.href}
                        className={`
                          flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors
                          ${isActive 
                            ? 'bg-blue-50 text-blue-700' 
                            : 'text-gray-700 hover:bg-gray-50'
                          }
                        `}
                      >
                        <span>{item.icon}</span>
                        {item.name}
                      </Link>
                    );
                  })}
                  
                  {isAdmin && (
                    <div className="relative">
                      <button 
                        onClick={() => setShowAdminMenu(!showAdminMenu)}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-orange-700 hover:bg-orange-50 transition-colors"
                      >
                        <span>🔧</span>
                        Admin
                        <span className={`transition-transform text-xs ${showAdminMenu ? 'rotate-180' : ''}`}>▼</span>
                      </button>
                      
                      {showAdminMenu && (
                        <div className="absolute left-0 mt-2 w-56 bg-white rounded-lg shadow-xl border border-gray-200 z-50">
                          <div className="py-2">
                            {adminMenuItems.map((item) => (
                              <Link
                                key={item.name}
                                href={item.href}
                                onClick={() => setShowAdminMenu(false)}
                                className={`flex items-center gap-3 px-4 py-3 text-sm transition-colors block w-full text-left ${
                                  pathname.startsWith(item.href) && item.href !== '/admin'
                                    ? 'bg-orange-50 text-orange-700'
                                    : pathname === item.href
                                    ? 'bg-orange-50 text-orange-700'
                                    : 'text-gray-700 hover:bg-gray-50'
                                }`}
                              >
                                <span className="text-lg">{item.icon}</span>
                                <span className="flex-1">{item.name}</span>
                              </Link>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </nav>
              </div>

              <div className="flex items-center gap-4">
                <LanguageSwitcher />
                
                <div className="relative group">
                  <button className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-50">
                    <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                      {user?.name?.charAt(0).toUpperCase()}
                    </div>
                    <span className="text-sm font-medium hidden md:block">{user?.name}</span>
                  </button>
                  
                  <div className="absolute right-0 mt-2 w-48 bg-white rounded-lg shadow-lg border border-gray-200 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all">
                    <div className="p-2">
                      <div className="px-4 py-2 text-sm text-gray-700 border-b">
                        {user?.email}
                      </div>
                      <button 
                        onClick={logout}
                        className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded"
                      >
                        Logout
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </header>

        <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {children}
        </main>
      </div>
    </ProtectedRoute>
  );
}
