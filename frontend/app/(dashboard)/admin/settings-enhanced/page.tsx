'use client';

import React, { useEffect, useState } from 'react';
import Modal from '@/app/components/admin/modal';

export default function SettingsPage() {
  const [settings, setSettings] = useState({
    system_name: 'RAG-ENTERPRISE',
    organization_name: 'My Organization',
    admin_email: 'admin@example.com',
    api_key: '',
    max_file_size: 100,
    max_documents: 1000,
    enable_embeddings: true,
    enable_search: true,
    enable_analytics: true,
    enable_api: true,
    backup_enabled: true,
    backup_frequency: 'daily',
    session_timeout: 30,
    password_policy: 'strong',
  });

  const [isSaving, setIsSaving] = useState(false);
  const [showApiKeyModal, setShowApiKeyModal] = useState(false);
  const [showBackupModal, setShowBackupModal] = useState(false);
  const [showCacheModal, setShowCacheModal] = useState(false);

  const handleChange = (key: string, value: any) => {
    setSettings({ ...settings, [key]: value });
  };

  const handleSave = async () => {
    setIsSaving(true);
    // Simulate saving
    setTimeout(() => {
      setIsSaving(false);
      alert('Settings saved successfully!');
    }, 1000);
  };

  const handleGenerateApiKey = () => {
    const newKey = `sk_${Math.random().toString(36).substr(2, 20)}`;
    setSettings({ ...settings, api_key: newKey });
  };

  const handleBackup = async () => {
    alert('Backup started! This may take a few minutes.');
    setShowBackupModal(false);
  };

  const handleClearCache = async () => {
    alert('Cache cleared successfully!');
    setShowCacheModal(false);
  };

  const SettingSection = ({ title, description, children }: { title: string; description: string; children: React.ReactNode }) => (
    <div className="bg-white rounded-lg shadow border border-gray-200 p-6 mb-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-1">{title}</h3>
      <p className="text-sm text-gray-600 mb-4">{description}</p>
      {children}
    </div>
  );

  return (
    <div className="max-w-4xl space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">System Settings</h1>
        <p className="text-gray-600 mt-1">Configure system behavior and features</p>
      </div>

      {/* General Settings */}
      <SettingSection
        title="General"
        description="Basic system configuration"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">System Name</label>
            <input
              type="text"
              value={settings.system_name}
              onChange={(e) => handleChange('system_name', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Organization</label>
            <input
              type="text"
              value={settings.organization_name}
              onChange={(e) => handleChange('organization_name', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div className="md:col-span-2">
            <label className="block text-sm font-medium text-gray-700 mb-2">Admin Email</label>
            <input
              type="email"
              value={settings.admin_email}
              onChange={(e) => handleChange('admin_email', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </SettingSection>

      {/* API Configuration */}
      <SettingSection
        title="API Configuration"
        description="Manage API access and authentication"
      >
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">API Key</label>
            <div className="flex gap-2">
              <input
                type="password"
                value={settings.api_key}
                readOnly
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg bg-gray-50"
              />
              <button
                onClick={handleGenerateApiKey}
                className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
              >
                Generate New
              </button>
            </div>
          </div>
          <label className="flex items-center gap-3">
            <input
              type="checkbox"
              checked={settings.enable_api}
              onChange={(e) => handleChange('enable_api', e.target.checked)}
              className="w-4 h-4 rounded border-gray-300"
            />
            <span className="text-sm text-gray-700">Enable API Access</span>
          </label>
        </div>
      </SettingSection>

      {/* Feature Settings */}
      <SettingSection
        title="Features"
        description="Enable or disable system features"
      >
        <div className="space-y-3">
          {[
            { key: 'enable_embeddings', label: 'Enable Embeddings' },
            { key: 'enable_search', label: 'Enable Search' },
            { key: 'enable_analytics', label: 'Enable Analytics' },
          ].map((feature) => (
            <label key={feature.key} className="flex items-center gap-3">
              <input
                type="checkbox"
                checked={settings[feature.key as keyof typeof settings] as boolean}
                onChange={(e) => handleChange(feature.key, e.target.checked)}
                className="w-4 h-4 rounded border-gray-300"
              />
              <span className="text-sm text-gray-700">{feature.label}</span>
            </label>
          ))}
        </div>
      </SettingSection>

      {/* Storage & Limits */}
      <SettingSection
        title="Storage & Limits"
        description="Configure storage quotas and limits"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max File Size (MB)</label>
            <input
              type="number"
              value={settings.max_file_size}
              onChange={(e) => handleChange('max_file_size', parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Max Documents</label>
            <input
              type="number"
              value={settings.max_documents}
              onChange={(e) => handleChange('max_documents', parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        </div>
      </SettingSection>

      {/* Security Settings */}
      <SettingSection
        title="Security"
        description="Manage security and access policies"
      >
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Session Timeout (minutes)</label>
            <input
              type="number"
              value={settings.session_timeout}
              onChange={(e) => handleChange('session_timeout', parseInt(e.target.value))}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password Policy</label>
            <select
              value={settings.password_policy}
              onChange={(e) => handleChange('password_policy', e.target.value)}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="weak">Weak</option>
              <option value="medium">Medium</option>
              <option value="strong">Strong</option>
            </select>
          </div>
        </div>
      </SettingSection>

      {/* Backup & Maintenance */}
      <SettingSection
        title="Backup & Maintenance"
        description="Manage backups and system maintenance"
      >
        <div className="space-y-4">
          <div className="flex items-center justify-between p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div>
              <p className="font-medium text-blue-900">Automatic Backups</p>
              <p className="text-sm text-blue-700">Frequency: {settings.backup_frequency}</p>
            </div>
            <button
              onClick={() => setShowBackupModal(true)}
              className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors"
            >
              Backup Now
            </button>
          </div>
          <button
            onClick={() => setShowCacheModal(true)}
            className="w-full px-4 py-2 border border-gray-300 hover:bg-gray-50 rounded-lg font-medium transition-colors text-left"
          >
            🗑️ Clear Cache
          </button>
        </div>
      </SettingSection>

      {/* Save Button */}
      <div className="flex gap-3">
        <button
          onClick={handleSave}
          disabled={isSaving}
          className="flex-1 px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white rounded-lg font-medium transition-colors disabled:opacity-50"
        >
          {isSaving ? 'Saving...' : 'Save Settings'}
        </button>
        <button className="px-6 py-3 border border-gray-300 hover:bg-gray-50 rounded-lg font-medium transition-colors">
          Cancel
        </button>
      </div>

      {/* Modals */}
      <Modal
        isOpen={showBackupModal}
        title="Create Backup?"
        onClose={() => setShowBackupModal(false)}
        onConfirm={handleBackup}
        confirmText="Backup Now"
      >
        <p>This will create a complete backup of your system data. The process may take several minutes.</p>
      </Modal>

      <Modal
        isOpen={showCacheModal}
        title="Clear Cache?"
        onClose={() => setShowCacheModal(false)}
        onConfirm={handleClearCache}
        confirmText="Clear"
      >
        <p>This will clear all cached data. Your application performance may be temporarily affected.</p>
      </Modal>
    </div>
  );
}
