import React, { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { tradingService } from '../services/services';

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [balance, setBalance] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const [statsData, balanceData] = await Promise.allSettled([
        tradingService.getStats(),
        tradingService.getBalance(),
      ]);

      if (statsData.status === 'fulfilled') {
        setStats(statsData.value);
      }

      if (balanceData.status === 'fulfilled') {
        setBalance(balanceData.value);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
        </div>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <button
            onClick={fetchDashboardData}
            className="btn-secondary"
          >
            🔄 Refresh
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Stats Grid */}
        {stats && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <div className="card bg-gradient-to-br from-blue-50 to-blue-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Total Trades</p>
                  <p className="text-3xl font-bold text-gray-900">{stats.total_trades}</p>
                </div>
                <div className="text-4xl">📊</div>
              </div>
            </div>

            <div className="card bg-gradient-to-br from-green-50 to-green-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Successful Trades</p>
                  <p className="text-3xl font-bold text-green-700">{stats.successful_trades}</p>
                </div>
                <div className="text-4xl">✅</div>
              </div>
            </div>

            <div className="card bg-gradient-to-br from-red-50 to-red-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Failed Trades</p>
                  <p className="text-3xl font-bold text-red-700">{stats.failed_trades}</p>
                </div>
                <div className="text-4xl">❌</div>
              </div>
            </div>

            <div className="card bg-gradient-to-br from-yellow-50 to-yellow-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Pending Orders</p>
                  <p className="text-3xl font-bold text-yellow-700">{stats.pending_trades}</p>
                </div>
                <div className="text-4xl">⏳</div>
              </div>
            </div>

            <div className="card bg-gradient-to-br from-purple-50 to-purple-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Active Bots</p>
                  <p className="text-3xl font-bold text-purple-700">{stats.active_bot_configs}</p>
                </div>
                <div className="text-4xl">🤖</div>
              </div>
            </div>

            <div className="card bg-gradient-to-br from-indigo-50 to-indigo-100">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600 mb-1">Success Rate</p>
                  <p className="text-3xl font-bold text-indigo-700">
                    {stats.total_trades > 0
                      ? `${((stats.successful_trades / stats.total_trades) * 100).toFixed(1)}%`
                      : '0%'}
                  </p>
                </div>
                <div className="text-4xl">📈</div>
              </div>
            </div>
          </div>
        )}

        {/* Account Balance */}
        {balance && (
          <div className="card">
            <h2 className="text-xl font-bold mb-4">Account Balance</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Wallet Balance</p>
                <p className="text-2xl font-bold text-gray-900">
                  ${parseFloat(balance.total_wallet_balance).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Available Balance</p>
                <p className="text-2xl font-bold text-green-600">
                  ${parseFloat(balance.available_balance).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Margin Balance</p>
                <p className="text-2xl font-bold text-blue-600">
                  ${parseFloat(balance.total_margin_balance).toFixed(2)}
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Unrealized P&L</p>
                <p
                  className={`text-2xl font-bold ${
                    parseFloat(balance.total_unrealized_profit) >= 0
                      ? 'text-green-600'
                      : 'text-red-600'
                  }`}
                >
                  ${parseFloat(balance.total_unrealized_profit).toFixed(2)}
                </p>
              </div>
            </div>

            {balance.assets && balance.assets.length > 0 && (
              <div className="mt-6">
                <h3 className="text-lg font-semibold mb-3">Assets</h3>
                <div className="overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Asset
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Wallet Balance
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Available
                        </th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">
                          Unrealized P&L
                        </th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {balance.assets.map((asset, index) => (
                        <tr key={index}>
                          <td className="px-6 py-4 whitespace-nowrap font-medium">
                            {asset.asset}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {parseFloat(asset.wallet_balance).toFixed(8)}
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            {parseFloat(asset.available_balance).toFixed(8)}
                          </td>
                          <td
                            className={`px-6 py-4 whitespace-nowrap ${
                              parseFloat(asset.unrealized_profit) >= 0
                                ? 'text-green-600'
                                : 'text-red-600'
                            }`}
                          >
                            {parseFloat(asset.unrealized_profit).toFixed(8)}
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            )}
          </div>
        )}

        {/* Quick Actions */}
        <div className="card">
          <h2 className="text-xl font-bold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <a href="/dashboard/trade" className="btn-primary text-center">
              📈 New Trade
            </a>
            <a href="/dashboard/orders" className="btn-secondary text-center">
              📋 View Orders
            </a>
            <a href="/dashboard/bot-configs" className="btn-secondary text-center">
              ⚙️ Bot Settings
            </a>
            <a href="/dashboard/notes" className="btn-secondary text-center">
              📝 Notes
            </a>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Dashboard;
