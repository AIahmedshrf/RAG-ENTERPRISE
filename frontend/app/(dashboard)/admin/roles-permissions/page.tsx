'use client';

import { useState, useEffect } from 'react';
import Modal from '@/app/components/admin/modal';
import StatCard from '@/app/components/admin/stat-card';

interface Permission {
  id: string;
  name: string;
  resource: string;
  action: string;
}

interface Role {
  id: string;
  name: string;
  description?: string;
  is_system: boolean;
  user_count: number;
  permissions: Permission[];
}

export default function RolesPermissionsPage() {
  const [roles, setRoles] = useState<Role[]>([]);
  const [allPermissions, setAllPermissions] = useState<Permission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  
  const [showRoleModal, setShowRoleModal] = useState(false);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);
  const [selectedPermissions, setSelectedPermissions] = useState<Set<string>>(new Set());
  
  const [showMatrixView, setShowMatrixView] = useState(false);
  const [searchRole, setSearchRole] = useState('');
  const [expandedRole, setExpandedRole] = useState<string | null>(null);

  const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null;

  useEffect(() => {
    fetchRoles();
    fetchPermissions();
  }, []);

  const fetchRoles = async () => {
    try {
      setLoading(true);
      const response = await fetch(`${API_URL}/admin/roles?limit=100`, {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) throw new Error('Failed to fetch roles');
      const data = await response.json();
      setRoles(data.data || []);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const fetchPermissions = async () => {
    try {
      const response = await fetch(
        `${API_URL}/admin/roles/permissions/list`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        }
      );

      if (!response.ok) throw new Error('Failed to fetch permissions');
      const data = await response.json();
      
      // Flatten permissions from grouped structure
      const flattened = Object.values(data.data || {})
        .flat() as Permission[];
      setAllPermissions(flattened);
    } catch (err: any) {
      console.error('Error fetching permissions:', err);
    }
  };

  const handleSelectPermission = (permissionId: string) => {
    const newSet = new Set(selectedPermissions);
    if (newSet.has(permissionId)) {
      newSet.delete(permissionId);
    } else {
      newSet.add(permissionId);
    }
    setSelectedPermissions(newSet);
  };

  const handleEditRole = (role: Role) => {
    setSelectedRole(role);
    setSelectedPermissions(new Set(role.permissions.map(p => p.id)));
    setShowRoleModal(true);
  };

  const handleSaveRolePermissions = async () => {
    if (!selectedRole) return;

    try {
      // Get current permissions
      const currentPermIds = new Set(selectedRole.permissions.map(p => p.id));
      const newPermIds = selectedPermissions;

      // Find permissions to add and remove
      const toAdd = Array.from(newPermIds).filter(id => !currentPermIds.has(id));
      const toRemove = Array.from(currentPermIds).filter(id => !newPermIds.has(id));

      // Add new permissions
      for (const permId of toAdd) {
        const response = await fetch(
          `${API_URL}/admin/roles/${selectedRole.id}/permissions`,
          {
            method: 'POST',
            headers: {
              'Authorization': `Bearer ${token}`,
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({
              permission_id: permId,
            }),
          }
        );
        if (!response.ok) throw new Error('Failed to add permission');
      }

      // Remove permissions
      for (const permId of toRemove) {
        const response = await fetch(
          `${API_URL}/admin/roles/${selectedRole.id}/permissions/${permId}`,
          {
            method: 'DELETE',
            headers: {
              'Authorization': `Bearer ${token}`,
            },
          }
        );
        if (!response.ok) throw new Error('Failed to remove permission');
      }

      alert('Role permissions updated successfully');
      setShowRoleModal(false);
      setSelectedRole(null);
      setSelectedPermissions(new Set());
      fetchRoles();
    } catch (err: any) {
      alert(`Error: ${err.message}`);
    }
  };

  const filteredRoles = roles.filter(role =>
    role.name.toLowerCase().includes(searchRole.toLowerCase())
  );

  // Group permissions by resource
  const permissionsByResource = allPermissions.reduce((acc, perm) => {
    if (!acc[perm.resource]) acc[perm.resource] = [];
    acc[perm.resource].push(perm);
    return acc;
  }, {} as Record<string, Permission[]>);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6">
      {/* Header */}
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">🎖️ Roles & Permissions</h1>
          <p className="text-gray-600 mt-1">Manage roles and their permissions</p>
        </div>
        <button
          onClick={() => setShowMatrixView(!showMatrixView)}
          className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 transition-colors"
        >
          {showMatrixView ? '📊 Switch to List' : '📈 Permission Matrix'}
        </button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
        <StatCard
          label="Total Roles"
          value={roles.length}
          icon="🎖️"
          bgColor="bg-blue-50"
        />
        <StatCard
          label="Total Permissions"
          value={allPermissions.length}
          icon="✅"
          bgColor="bg-green-50"
        />
        <StatCard
          label="Resources"
          value={Object.keys(permissionsByResource).length}
          icon="📦"
          bgColor="bg-yellow-50"
        />
      </div>

      {showMatrixView ? (
        // Permission Matrix View
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50 border-b sticky top-0">
                <tr>
                  <th className="px-6 py-3 text-left font-semibold text-gray-700 min-w-40">Role</th>
                  {Object.keys(permissionsByResource).map(resource => (
                    <th key={resource} className="px-3 py-3 text-center font-semibold text-gray-700 min-w-32">
                      <div className="text-xs uppercase">{resource}</div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y">
                {roles.map(role => (
                  <tr key={role.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4">
                      <div className="font-medium text-gray-900">{role.name}</div>
                      <div className="text-xs text-gray-500">{role.user_count} users</div>
                    </td>
                    {Object.keys(permissionsByResource).map(resource => {
                      const rolePermsForResource = role.permissions.filter(
                        p => p.resource === resource
                      );
                      return (
                        <td key={resource} className="px-3 py-4 text-center">
                          {rolePermsForResource.length > 0 ? (
                            <details className="cursor-pointer">
                              <summary className="inline-flex items-center justify-center px-2 py-1 bg-green-100 text-green-800 rounded text-xs font-medium hover:bg-green-200">
                                {rolePermsForResource.length}
                              </summary>
                              <div className="absolute bg-gray-50 border border-gray-200 rounded shadow p-2 min-w-32 z-10">
                                {rolePermsForResource.map(p => (
                                  <div key={p.id} className="text-xs text-gray-600 py-1">
                                    • {p.action}
                                  </div>
                                ))}
                              </div>
                            </details>
                          ) : (
                            <span className="text-gray-400">-</span>
                          )}
                        </td>
                      );
                    })}
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      ) : (
        // List View
        <>
          <div className="mb-4">
            <input
              type="text"
              placeholder="Search roles..."
              value={searchRole}
              onChange={(e) => setSearchRole(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>

          <div className="space-y-4">
            {filteredRoles.map(role => (
              <div
                key={role.id}
                className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <h3 className="text-lg font-semibold text-gray-900">
                        {role.name.toUpperCase()}
                      </h3>
                      {role.is_system && (
                        <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                          SYSTEM
                        </span>
                      )}
                    </div>
                    {role.description && (
                      <p className="text-gray-600 mt-1">{role.description}</p>
                    )}
                    <p className="text-sm text-gray-500 mt-2">
                      👥 {role.user_count} user{role.user_count !== 1 ? 's' : ''} • 
                      ✅ {role.permissions.length} permission{role.permissions.length !== 1 ? 's' : ''}
                    </p>
                  </div>
                  <button
                    onClick={() => handleEditRole(role)}
                    className="px-4 py-2 bg-blue-50 text-blue-600 rounded-lg hover:bg-blue-100 transition-colors"
                  >
                    Edit Permissions
                  </button>
                </div>

                {/* Permissions by Resource */}
                <div className="mt-4 pt-4 border-t">
                  <button
                    onClick={() => setExpandedRole(expandedRole === role.id ? null : role.id)}
                    className="text-sm font-medium text-blue-600 hover:text-blue-800"
                  >
                    {expandedRole === role.id ? '▼' : '▶'} View Permissions
                  </button>

                  {expandedRole === role.id && (
                    <div className="mt-4 grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {Object.entries(permissionsByResource).map(([resource, perms]) => {
                        const rolePerms = role.permissions.filter(p => p.resource === resource);
                        return (
                          <div key={resource} className="bg-gray-50 p-3 rounded">
                            <h4 className="font-medium text-gray-900 text-sm capitalize mb-2">
                              {resource}
                            </h4>
                            <div className="space-y-1">
                              {perms.map(perm => (
                                <div
                                  key={perm.id}
                                  className={`text-xs py-1 px-2 rounded ${
                                    rolePerms.some(rp => rp.id === perm.id)
                                      ? 'bg-green-100 text-green-800'
                                      : 'text-gray-500'
                                  }`}
                                >
                                  {rolePerms.some(rp => rp.id === perm.id) ? '✓' : '○'} {perm.action}
                                </div>
                              ))}
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        </>
      )}

      {/* Edit Permissions Modal */}
      <Modal
        isOpen={showRoleModal}
        onClose={() => setShowRoleModal(false)}
        title={`Edit Permissions - ${selectedRole?.name}`}
      >
        <div className="space-y-4 max-h-96 overflow-y-auto">
          {Object.entries(permissionsByResource).map(([resource, perms]) => (
            <div key={resource}>
              <h4 className="font-semibold text-gray-900 capitalize mb-2 text-sm">
                {resource}
              </h4>
              <div className="space-y-2 pl-4">
                {perms.map(perm => (
                  <label key={perm.id} className="flex items-center gap-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedPermissions.has(perm.id)}
                      onChange={() => handleSelectPermission(perm.id)}
                      className="w-4 h-4 text-blue-600 rounded focus:ring-blue-500"
                    />
                    <span className="text-sm text-gray-700 capitalize">{perm.action}</span>
                  </label>
                ))}
              </div>
            </div>
          ))}
        </div>

        <div className="flex gap-3 pt-6 border-t">
          <button
            onClick={handleSaveRolePermissions}
            className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            Save Changes
          </button>
          <button
            onClick={() => setShowRoleModal(false)}
            className="flex-1 px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
          >
            Cancel
          </button>
        </div>
      </Modal>
    </div>
  );
}
