// frontend/src/components/Dashboard.jsx
import React, { useEffect, useState } from 'react';
import { apiService } from '../services/apiService';

export default function Dashboard({ user, onLogout }) {
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState('overview');

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const h = await apiService.checkHealth();
        setHealth(h);
      } catch (err) {
        console.error('Failed to load health:', err);
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const navigation = [
    { id: 'overview', name: 'Overview' },
    { id: 'users', name: 'Users' },
    { id: 'activities', name: 'Activities' },
    { id: 'reports', name: 'Reports' },
  ];

  return (
    <div className="min-h-screen bg-gray-100">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            <div className="text-xl font-bold">SPMS</div>
            <nav className="hidden md:flex space-x-2">
              {navigation.map((n) => (
                <button
                  key={n.id}
                  onClick={() => setActiveTab(n.id)}
                  className={`px-3 py-2 rounded ${activeTab === n.id ? 'bg-blue-600 text-white' : 'text-gray-600'}`}
                >
                  {n.name}
                </button>
              ))}
            </nav>
          </div>
          <div className="flex items-center space-x-4">
            <div className="text-sm text-gray-700">Welcome, {user?.full_name || user?.username}</div>
            <button
              onClick={onLogout}
              className="px-3 py-2 bg-red-500 text-white rounded"
            >
              Logout
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto p-4">
        {loading ? (
          <div className="text-gray-600">Loading dashboard…</div>
        ) : (
          <>
            {activeTab === 'overview' && (
              <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div className="col-span-2 bg-white p-4 rounded shadow">
                  <h3 className="text-lg font-semibold mb-2">Overview</h3>
                  <p className="text-sm text-gray-600">Quick stats and recent activity will appear here.</p>
                </div>

                <aside className="bg-white p-4 rounded shadow">
                  <h4 className="font-semibold mb-2">System Health</h4>
                  {health ? (
                    <div className="text-sm">
                      <div>Status: <strong className={health.status === 'healthy' ? 'text-green-600' : 'text-red-600'}>{health.status}</strong></div>
                      <div>Version: {health.version || 'n/a'}</div>
                      <div>Environment: {health.environment || 'n/a'}</div>
                      {health.checks?.database && <div>Database: {health.checks.database.status}</div>}
                    </div>
                  ) : (
                    <div className="text-sm text-gray-500">Health info unavailable</div>
                  )}
                </aside>
              </section>
            )}

            {activeTab !== 'overview' && (
              <div className="bg-white p-6 rounded shadow">
                <h3 className="text-lg font-semibold mb-2">{navigation.find(n => n.id === activeTab)?.name}</h3>
                <p className="text-sm text-gray-600">This module is under development. Coming soon.</p>
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}
