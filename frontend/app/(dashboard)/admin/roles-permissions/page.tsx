'use client';

import React, { useEffect, useState } from 'react';
import Modal from '@/app/components/admin/modal';
import StatCard from '@/app/components/admin/stat-card';

interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
}

interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  is_active: boolean;
  user_count?: number;
}

interface User {
  id: string;
  email: string;
  full_name: string;
  role: string;
  created_at: string;
}

export default function RolesPermissionsPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [users, setUsers] = useState<User[]>([]);
  const [permissions, setPermissions] = useState<Permission[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  const [showRoleModal, setShowRoleModal] = useState(false);
  const [showUserRoleModal, setShowUserRoleModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [selectedUser, setSelectedUser] = useState<User | null>(null);

  const [newRole, setNewRole] = useState({
    name: '',
    description: '',
    permissions: [] as string[],
  });

  const [userRole, setUserRole] = useState('');

  const endpoint = (path: string) => {
    const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    return `${API_URL}${path}`;
  };

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('access_token');

      // Fetch roles (mock data for now)
      const mockRoles: Role[] = [
        {
          id: '1',
          name: 'Super Admin',
          description: 'Full system access',
          permissions: [
            'user:create',
            'user:read',
            'user:update',
            'user:delete',
            'agent:create',
            'agent:read',
            'agent:update',
            'agent:delete',
            'knowledge:create',
            'knowledge:read',
            'knowledge:update',
            'knowledge:delete',
            'model:create',
            'model:read',
            'model:update',
            'model:delete',
            'dataset:create',
            'dataset:read',
            'dataset:update',
            'dataset:delete',
            'settings:read',
            'settings:update',
            'system:admin',
          ],
          is_active: true,
          user_count: 2,
        },
        {
          id: '2',
          name: 'Admin',
          description: 'System administration',
          permissions: [
            'user:read',
            'user:update',
            'agent:create',
            'agent:read',
            'agent:update',
            'knowledge:create',
            'knowledge:read',
            'knowledge:update',
            'knowledge:delete',
            'model:read',
            'dataset:read',
            'settings:read',
            'settings:update',
          ],
          is_active: true,
          user_count: 5,
        },
        {
          id: '3',
          name: 'Manager',
          description: 'Team management',
          permissions: [
            'agent:read',
            'agent:create',
            'knowledge:read',
            'knowledge:create',
            'knowledge:update',
            'dataset:read',
            'settings:read',
          ],
          is_active: true,
          user_count: 12,
        },
        {
          id: '4',
          name: 'Viewer',
          description: 'Read-only access',
          permissions: [
            'agent:read',
            'knowledge:read',
            'dataset:read',
            'settings:read',
          ],
          is_active: true,
          user_count: 25,
        },
      ];

      setRoles(mockRoles);

      // Fetch users
      const usersRes = await fetch(endpoint('/users'), {
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      });
      if (usersRes.ok) {
        const usersData = await usersRes.json();
        setUsers(Array.isArray(usersData) ? usersData : usersData.users || []);
      }
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateRole = async () => {
    // In a real app, this would call the API
    alert(`Creating role: ${newRole.name} with ${newRole.permissions.length} permissions`);
    setShowRoleModal(false);
    setNewRole({ name: '', description: '', permissions: [] });
  };

  const handleAssignRole = async () => {
    if (!selectedUser) return;
    alert(`Assigning role "${userRole}" to ${selectedUser.full_name}`);
    setShowUserRoleModal(false);
    setUserRole('');
  };

  const togglePermission = (permission: string) => {
    setNewRole({
      ...newRole,
      permissions: newRole.permissions.includes(permission)
        ? newRole.permissions.filter(p => p !== permission)
        : [...newRole.permissions, permission],
    });
  };

  const permissionCategories = [
    {
      name: 'User Management',
      icon: '👥',
      items: ['user:create', 'user:read', 'user:update', 'user:delete'],
    },
    {
      name: 'Agent Management',
      icon: '🤖',
      items: ['agent:create', 'agent:read', 'agent:update', 'agent:delete', 'agent:deploy'],
    },
    {
      name: 'Knowledge Management',
      icon: '📚',
      items: ['knowledge:create', 'knowledge:read', 'knowledge:update', 'knowledge:delete', 'knowledge:publish'],
    },
    {
      name: 'Model Management',
      icon: '🧠',
      items: ['model:create', 'model:read', 'model:update', 'model:delete'],
    },
    {
      name: 'Dataset Management',
      icon: '📦',
      items: ['dataset:create', 'dataset:read', 'dataset:update', 'dataset:delete'],
    },
    {
      name: 'System Settings',
      icon: '⚙️',
      items: ['settings:read', 'settings:update', 'system:admin'],
    },
  ];

  const stats = [
    { label: 'Total Roles', value: roles.length, icon: '🎖️', bgColor: 'bg-blue-50' },
    { label: 'Total Users', value: users.length, icon: '👥', bgColor: 'bg-green-50' },
    { label: 'Active Roles', value: roles.filter(r => r.is_active).length, icon: '✅', bgColor: 'bg-purple-50' },
    { label: 'Permissions', value: permissionCategories.reduce((sum, cat) => sum + cat.items.length, 0), icon: '🔐', bgColor: 'bg-orange-50' },
  ];

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Roles & Permissions</h1>
          <p className="text-gray-600 mt-1">Manage user roles and access control</p>
        </div>
        <button
          onClick={() => setShowRoleModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          ➕ Create Role
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatCard key={idx} {...stat} />
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Roles Section */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Roles</h2>
          <div className="space-y-3">
            {roles.map(role => (
              <div key={role.id} className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-2">
                  <div>
                    <h3 className="font-semibold text-gray-900">{role.name}</h3>
                    <p className="text-sm text-gray-600">{role.description}</p>
                  </div>
                  <span className="px-2 py-1 bg-green-50 text-green-700 text-xs rounded font-semibold">
                    {role.user_count} users
                  </span>
                </div>
                <div className="flex gap-2 flex-wrap mb-3">
                  {role.permissions.slice(0, 3).map(perm => (
                    <span key={perm} className="text-xs px-2 py-1 bg-blue-50 text-blue-700 rounded">
                      {perm}
                    </span>
                  ))}
                  {role.permissions.length > 3 && (
                    <span className="text-xs px-2 py-1 bg-gray-100 text-gray-700 rounded">
                      +{role.permissions.length - 3} more
                    </span>
                  )}
                </div>
                <button
                  onClick={() => setSelectedRole(role)}
                  className="text-sm text-blue-600 hover:text-blue-700 font-medium"
                >
                  Edit Permissions →
                </button>
              </div>
            ))}
          </div>
        </div>

        {/* Users Section */}
        <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Users</h2>
          <div className="space-y-2 max-h-96 overflow-y-auto">
            {users.map(user => (
              <div
                key={user.id}
                className="p-3 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors"
                onClick={() => {
                  setSelectedUser(user);
                  setShowUserRoleModal(true);
                }}
              >
                <p className="font-medium text-sm text-gray-900">{user.full_name}</p>
                <p className="text-xs text-gray-500">{user.email}</p>
                <span className="inline-block text-xs px-2 py-1 bg-purple-50 text-purple-700 rounded mt-1">
                  {user.role}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Create Role Modal */}
      <Modal
        isOpen={showRoleModal}
        title="Create New Role"
        onClose={() => setShowRoleModal(false)}
        onConfirm={handleCreateRole}
        confirmText="Create Role"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Role Name</label>
            <input
              type="text"
              value={newRole.name}
              onChange={(e) => setNewRole({ ...newRole, name: e.target.value })}
              placeholder="e.g., Content Creator"
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Description</label>
            <input
              type="text"
              value={newRole.description}
              onChange={(e) => setNewRole({ ...newRole, description: e.target.value })}
              placeholder="Role description..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-3">Permissions</label>
            <div className="space-y-4 max-h-80 overflow-y-auto border border-gray-200 rounded-lg p-4 bg-gray-50">
              {permissionCategories.map((category) => (
                <div key={category.name}>
                  <h4 className="font-semibold text-sm text-gray-900 mb-2">
                    {category.icon} {category.name}
                  </h4>
                  <div className="space-y-2 ml-4">
                    {category.items.map((perm) => (
                      <label key={perm} className="flex items-center gap-2">
                        <input
                          type="checkbox"
                          checked={newRole.permissions.includes(perm)}
                          onChange={() => togglePermission(perm)}
                          className="w-4 h-4 rounded border-gray-300"
                        />
                        <span className="text-sm text-gray-700">{perm}</span>
                      </label>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Modal>

      {/* Assign User Role Modal */}
      <Modal
        isOpen={showUserRoleModal}
        title={`Assign Role - ${selectedUser?.full_name}`}
        onClose={() => setShowUserRoleModal(false)}
        onConfirm={handleAssignRole}
        confirmText="Assign Role"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Select Role</label>
            <select
              value={userRole}
              onChange={(e) => setUserRole(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">Choose a role...</option>
              {roles.map(role => (
                <option key={role.id} value={role.name}>{role.name}</option>
              ))}
            </select>
          </div>
          <p className="text-sm text-gray-600">
            Current role: <strong>{selectedUser?.role}</strong>
          </p>
        </div>
      </Modal>
    </div>
  );
}
