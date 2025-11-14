'use client';

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-gray-900">⚙️ System Settings</h1>
        <p className="text-gray-600 mt-1">Configure system preferences and settings</p>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">General Settings</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                System Name
              </label>
              <input
                type="text"
                defaultValue="RAG-ENTERPRISE"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
            
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Organization
              </label>
              <input
                type="text"
                placeholder="Your Organization"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Support Email
              </label>
              <input
                type="email"
                placeholder="support@example.com"
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>

            <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
              Save Settings
            </button>
          </div>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b border-gray-200">
          <h2 className="text-lg font-semibold text-gray-900">Feature Flags</h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            {[
              { name: 'Advanced Search', enabled: true },
              { name: 'Custom Agents', enabled: true },
              { name: 'Multi-language Support', enabled: true },
              { name: 'Vector Store Integration', enabled: false },
            ].map((feature) => (
              <div key={feature.name} className="flex items-center justify-between p-4 border border-gray-200 rounded-lg">
                <div>
                  <p className="font-medium text-gray-900">{feature.name}</p>
                </div>
                <div className={`w-12 h-6 rounded-full flex items-center ${
                  feature.enabled ? 'bg-green-500' : 'bg-gray-300'
                } cursor-pointer`}>
                  <div className={`w-5 h-5 rounded-full bg-white transition-transform ${
                    feature.enabled ? 'transform translate-x-6' : ''
                  }`} />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
