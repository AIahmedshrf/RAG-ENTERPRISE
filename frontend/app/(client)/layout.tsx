// Client Layout - User-Facing Interface
'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { LanguageSwitcher } from '@/app/components/ui/language-switcher';

const navigation = [
  { name: 'Home', href: '/', icon: '🏠' },
  { name: 'Chat', href: '/chat', icon: '💬' },
  { name: 'Documents', href: '/documents', icon: '📄' },
  { name: 'Financial', href: '/financial', icon: '💰' },
  { name: 'History', href: '/history', icon: '📜' },
];

export default function ClientLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const pathname = usePathname();

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      {/* Header */}
      <header className="bg-white border-b border-gray-200 sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center gap-8">
              <Link href="/" className="flex items-center gap-2">
                <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-lg flex items-center justify-center">
                  <span className="text-white text-xl font-bold">R</span>
                </div>
                <span className="text-xl font-bold text-gray-900">RAG-ENTERPRISE</span>
              </Link>

              {/* Navigation */}
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
              </nav>
            </div>

            {/* Right Side */}
            <div className="flex items-center gap-4">
              <LanguageSwitcher />
              
              <button className="p-2 text-gray-600 hover:text-gray-900 rounded-lg hover:bg-gray-50">
                🔔
              </button>

              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-gradient-to-br from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white text-sm font-semibold">
                  U
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {children}
      </main>

      {/* Footer */}
      <footer className="bg-white border-t border-gray-200 mt-auto">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <p className="text-center text-sm text-gray-500">
            © 2025 RAG-ENTERPRISE. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
