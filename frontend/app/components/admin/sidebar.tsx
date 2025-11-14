'use client';

import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/app/contexts/auth-context';
import { useState } from 'react';

interface NavSection {
  title: string;
  icon: string;
  items: NavItem[];
}

interface NavItem {
  name: string;
  href: string;
  icon: string;
}

const navigationSections: NavSection[] = [
  {
    title: 'Dashboard',
    icon: '📊',
    items: [
      { name: 'Overview', href: '/admin', icon: '📊' },
      { name: 'Analytics', href: '/admin/analytics', icon: '📈' },
    ],
  },
  {
    title: 'Knowledge Base',
    icon: '📄',
    items: [
      { name: 'Documents', href: '/admin/knowledge/documents', icon: '📋' },
      { name: 'Upload', href: '/admin/knowledge/upload', icon: '⬆️' },
      { name: 'Search', href: '/admin/knowledge/search', icon: '🔍' },
      { name: 'Jobs', href: '/admin/knowledge/jobs', icon: '⚙️' },
    ],
  },
  {
    title: 'Agents',
    icon: '🤖',
    items: [
      { name: 'All Agents', href: '/admin/agents', icon: '🤖' },
      { name: 'Create Agent', href: '/admin/agents/create', icon: '➕' },
      { name: 'Templates', href: '/admin/agents/templates', icon: '📋' },
    ],
  },
  {
    title: 'Data Management',
    icon: '📦',
    items: [
      { name: 'Datasets', href: '/admin/datasets', icon: '📦' },
      { name: 'Create Dataset', href: '/admin/datasets/create', icon: '➕' },
    ],
  },
  {
    title: 'AI Configuration',
    icon: '🧠',
    items: [
      { name: 'LLM Models', href: '/admin/models/llm', icon: '🧠' },
      { name: 'Embeddings', href: '/admin/models/embeddings', icon: '🔢' },
      { name: 'Reranker', href: '/admin/models/reranker', icon: '🎯' },
    ],
  },
  {
    title: 'System',
    icon: '⚙️',
    items: [
      { name: 'Users', href: '/admin/users', icon: '👥' },
      { name: 'Workspace', href: '/admin/workspace', icon: '🏢' },
      { name: 'Settings', href: '/admin/settings', icon: '⚙️' },
    ],
  },
];

interface SidebarProps {
  collapsed?: boolean;
}

export default function Sidebar({ collapsed = false }: SidebarProps) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, logout } = useAuth();
  const [expandedSection, setExpandedSection] = useState<string | null>('Dashboard');
  const [isCollapsed, setIsCollapsed] = useState(collapsed);

  const isItemActive = (href: string): boolean => {
    if (href === '/admin') {
      return pathname === '/admin';
    }
    return pathname.startsWith(href);
  };

  const isSectionActive = (items: NavItem[]): boolean => {
    return items.some(item => isItemActive(item.href));
  };

  const handleNavigation = (href: string) => {
    router.push(href);
  };

  const handleSectionToggle = (sectionTitle: string) => {
    setExpandedSection(expandedSection === sectionTitle ? null : sectionTitle);
  };

  return (
    <div className={`fixed inset-y-0 left-0 bg-white shadow-lg transition-all duration-300 ${
      isCollapsed ? 'w-20' : 'w-64'
    }`}>
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="p-4 border-b flex items-center justify-between">
          {!isCollapsed && (
            <div className="flex-1">
              <h1 className="text-xl font-bold text-blue-600">RAG-ENTERPRISE</h1>
              <p className="text-xs text-gray-500 mt-1">Admin Panel</p>
            </div>
          )}
          <button
            onClick={() => setIsCollapsed(!isCollapsed)}
            className="p-1 hover:bg-gray-100 rounded transition-colors"
            title={isCollapsed ? 'Expand' : 'Collapse'}
          >
            {isCollapsed ? '▶️' : '◀️'}
          </button>
        </div>

        {/* Navigation */}
        <nav className="flex-1 overflow-y-auto">
          <div className="space-y-1 p-3">
            {navigationSections.map((section) => (
              <div key={section.title}>
                {/* Section Header */}
                <button
                  onClick={() => handleSectionToggle(section.title)}
                  className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                    isSectionActive(section.items)
                      ? 'bg-blue-50 text-blue-600'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-lg flex-shrink-0">{section.icon}</span>
                  {!isCollapsed && (
                    <>
                      <span className="flex-1 text-left">{section.title}</span>
                      <span className={`transform transition-transform ${
                        expandedSection === section.title ? 'rotate-90' : ''
                      }`}>
                        ›
                      </span>
                    </>
                  )}
                </button>

                {/* Section Items */}
                {!isCollapsed && expandedSection === section.title && (
                  <div className="space-y-1 mt-1 pl-2">
                    {section.items.map((item) => (
                      <button
                        key={item.name}
                        onClick={() => handleNavigation(item.href)}
                        className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-sm transition-colors ${
                          isItemActive(item.href)
                            ? 'bg-blue-100 text-blue-600 font-medium'
                            : 'text-gray-600 hover:bg-gray-50'
                        }`}
                      >
                        <span className="text-base flex-shrink-0">{item.icon}</span>
                        <span>{item.name}</span>
                      </button>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </nav>

        {/* User Profile & Logout */}
        <div className="p-4 border-t">
          {!isCollapsed && user && (
            <div className="mb-3">
              <p className="text-sm font-medium text-gray-900 truncate">{user.name}</p>
              <p className="text-xs text-gray-500 truncate">{user.email}</p>
            </div>
          )}
          <button
            onClick={logout}
            className={`w-full px-3 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 text-sm font-medium transition-colors ${
              isCollapsed ? 'text-center' : 'text-left'
            }`}
          >
            {isCollapsed ? '🚪' : 'Logout'}
          </button>
        </div>
      </div>
    </div>
  );
}
