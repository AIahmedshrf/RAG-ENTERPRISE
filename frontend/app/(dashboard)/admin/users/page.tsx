'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/app/contexts/auth-context';
import Modal from '@/app/components/admin/modal';
import StatCard from '@/app/components/admin/stat-card';

interface User {
  id: string;
  email: string;
  name: string;
  role: string;
  status: string;
  last_login: string | null;
  created_at: string;
}

export default function UsersPage() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [filterRole, setFilterRole] = useState('');

  useEffect(() => {
    fetchUsers();
  }, []);

  const fetchUsers = async () => {
    try {
      setLoading(true);
      setError(null);
      const token = localStorage.getItem('access_token');
      
      const response = await fetch('http://localhost:8000/api/v1/admin/workspace/members', {
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(JSON.stringify(errorData.detail || errorData));
      }

      const data = await response.json();
      setUsers(data.data || []);
    } catch (err: any) {
      const errorMessage = typeof err.message === 'string' 
        ? err.message 
        : JSON.stringify(err.message);
      setError(errorMessage);
      console.error('Error fetching users:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInviteUser = async (email: string, role: string, name: string) => {
    try {
      const token = localStorage.getItem('access_token');
      
      console.log('Sending invite request:', { email, role, name });
      
      const response = await fetch('http://localhost:8000/api/v1/admin/workspace/members/invite', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ email, role, name }),
      });

      const responseData = await response.json();
      console.log('Response:', responseData);

      if (!response.ok) {
        const errorMsg = responseData.detail 
          ? (typeof responseData.detail === 'string' 
              ? responseData.detail 
              : JSON.stringify(responseData.detail))
          : `Server error: ${response.status}`;
        throw new Error(errorMsg);
      }

      alert(`✅ ${responseData.message || 'User invited successfully!'}\n\nTemporary password: temporary123`);
      await fetchUsers();
      setShowInviteModal(false);
    } catch (err: any) {
      const errorMsg = err.message || 'Unknown error occurred';
      console.error('Invite error:', err);
      alert(`❌ Failed to invite user:\n${errorMsg}`);
    }
  };

  const handleDeleteUser = async (userId: string, userName: string) => {
    if (!confirm(`Are you sure you want to remove "${userName}"?`)) return;

    try {
      const token = localStorage.getItem('access_token');
      
      const response = await fetch(`http://localhost:8000/api/v1/admin/workspace/members/${userId}`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to delete user');
      }

      alert('✅ User removed successfully!');
      await fetchUsers();
    } catch (err: any) {
      alert(`❌ Error: ${err.message}`);
      console.error('Delete error:', err);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading users...</p>
        </div>
      </div>
    );
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch =
      user.email.toLowerCase().includes(searchTerm.toLowerCase()) ||
      user.name.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesRole = !filterRole || user.role === filterRole;
    return matchesSearch && matchesRole;
  });

  const stats = [
    { label: 'Total Users', value: users.length, icon: '👥', bgColor: 'bg-blue-50' },
    { label: 'Active Users', value: users.filter(u => u.status === 'active').length, icon: '✅', bgColor: 'bg-green-50' },
    { label: 'Admins', value: users.filter(u => u.role === 'admin').length, icon: '🛡️', bgColor: 'bg-purple-50' },
    { label: 'Viewers', value: users.filter(u => u.role === 'viewer').length, icon: '👁️', bgColor: 'bg-orange-50' },
  ];

  const roleColors: Record<string, string> = {
    admin: 'bg-purple-50 text-purple-700',
    user: 'bg-blue-50 text-blue-700',
    viewer: 'bg-gray-50 text-gray-700',
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">👥 User Management</h1>
          <p className="text-gray-600 mt-1">Manage workspace members and permissions</p>
        </div>
        <button
          onClick={() => setShowInviteModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
        >
          ➕ Invite User
        </button>
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-50 border border-red-200 rounded-lg flex items-start gap-3">
          <span className="text-red-600">⚠️</span>
          <div className="flex-1">
            <p className="text-red-800 font-medium">Error</p>
            <p className="text-red-600 text-sm mt-1">{error}</p>
          </div>
        </div>
      )}

      {/* Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <StatCard key={idx} {...stat} />
        ))}
      </div>

      {/* Filters */}
      <div className="bg-white rounded-lg shadow border border-gray-200 p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search</label>
            <input
              type="text"
              placeholder="Search by email or name..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Filter by Role</label>
            <select
              value={filterRole}
              onChange={(e) => setFilterRole(e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="">All Roles</option>
              <option value="admin">Admin</option>
              <option value="user">User</option>
              <option value="viewer">Viewer</option>
            </select>
          </div>
          <div className="flex items-end">
            <button
              onClick={() => {
                setSearchTerm('');
                setFilterRole('');
              }}
              className="w-full px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50 font-medium transition-colors"
            >
              Reset Filters
            </button>
          </div>
        </div>
      </div>

      {/* Users Table */}
      <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50 border-b border-gray-200">
              <tr>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">User</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Email</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Role</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Status</th>
                <th className="px-6 py-3 text-left text-sm font-semibold text-gray-700">Last Login</th>
                <th className="px-6 py-3 text-center text-sm font-semibold text-gray-700">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {filteredUsers.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-gray-500">
                    No users found
                  </td>
                </tr>
              ) : (
                filteredUsers.map((user) => (
                  <tr key={user.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div>
                        <p className="font-medium text-gray-900">{user.name}</p>
                        <p className="text-sm text-gray-500">ID: {user.id}</p>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <code className="text-sm text-gray-700">{user.email}</code>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold ${roleColors[user.role] || roleColors.user}`}>
                        {user.role}
                      </span>
                    </td>
                    <td className="px-6 py-4">
                      <span className={`px-3 py-1 rounded-full text-xs font-semibold transition-colors ${
                        user.status === 'active'
                          ? 'bg-green-50 text-green-700'
                          : 'bg-red-50 text-red-700'
                      }`}>
                        {user.status === 'active' ? '✓ Active' : '✗ Inactive'}
                      </span>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
                    </td>
                    <td className="px-6 py-4 text-center">
                      <div className="flex items-center justify-center gap-2">
                        {user.id !== currentUser?.id && (
                          <button
                            onClick={() => handleDeleteUser(user.id, user.name)}
                            className="text-red-600 hover:text-red-700 font-medium text-sm"
                          >
                            Remove
                          </button>
                        )}
                        {user.id === currentUser?.id && (
                          <span className="text-gray-400 text-sm">You</span>
                        )}
                      </div>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {showInviteModal && (
        <InviteUserModal
          onClose={() => setShowInviteModal(false)}
          onInvite={handleInviteUser}
        />
      )}
    </div>
  );
}

function InviteUserModal({
  onClose,
  onInvite,
}: {
  onClose: () => void;
  onInvite: (email: string, role: string, name: string) => void;
}) {
  const [email, setEmail] = useState('');
  const [role, setRole] = useState('user');
  const [name, setName] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !name) {
      alert('Please fill in all required fields');
      return;
    }

    if (!email.includes('@')) {
      alert('Please enter a valid email address');
      return;
    }

    setLoading(true);
    try {
      await onInvite(email, role, name);
    } catch (error) {
      console.error('Submit error:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md">
        <h2 className="text-xl font-bold mb-4">Invite New User</h2>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email Address *
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="user@example.com"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Full Name *
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              placeholder="John Doe"
              required
            />
          </div>
          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Role
            </label>
            <select
              value={role}
              onChange={(e) => setRole(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="user">User - Regular access</option>
              <option value="admin">Admin - Full access</option>
              <option value="viewer">Viewer - Read-only access</option>
            </select>
          </div>
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3 mb-4">
            <p className="text-sm text-yellow-800">
              ℹ️ The user will receive a temporary password: <code className="font-mono bg-yellow-100 px-1 py-0.5 rounded">temporary123</code>
            </p>
            <p className="text-xs text-yellow-700 mt-1">
              They should change it after first login.
            </p>
          </div>
          <div className="flex justify-end gap-2">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
              disabled={loading}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? 'Inviting...' : 'Invite User'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
