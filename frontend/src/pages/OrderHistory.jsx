import React, { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { tradingService } from '../services/services';

const OrderHistory = () => {
  const [trades, setTrades] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({
    symbol: '',
    status: '',
  });

  useEffect(() => {
    fetchTrades();
  }, [filters]);

  const fetchTrades = async () => {
    try {
      setLoading(true);
      const params = {};
      if (filters.symbol) params.symbol = filters.symbol;
      if (filters.status) params.status = filters.status;

      const data = await tradingService.getTrades(params);
      setTrades(data);
    } catch (err) {
      console.error('Error fetching trades:', err);
      setError('Failed to load trade history');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      FILLED: 'badge-success',
      PENDING: 'badge-warning',
      FAILED: 'badge-danger',
      CANCELLED: 'badge-info',
      PARTIALLY_FILLED: 'badge-warning',
    };
    return styles[status] || 'badge-info';
  };

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleString();
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Order History</h1>
          <button onClick={fetchTrades} className="btn-secondary">
            🔄 Refresh
          </button>
        </div>

        {/* Filters */}
        <div className="card">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Symbol
              </label>
              <input
                type="text"
                placeholder="e.g., BTCUSDT"
                className="input-field"
                value={filters.symbol}
                onChange={(e) => setFilters({ ...filters, symbol: e.target.value })}
              />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Status
              </label>
              <select
                className="input-field"
                value={filters.status}
                onChange={(e) => setFilters({ ...filters, status: e.target.value })}
              >
                <option value="">All Statuses</option>
                <option value="FILLED">Filled</option>
                <option value="PENDING">Pending</option>
                <option value="FAILED">Failed</option>
                <option value="CANCELLED">Cancelled</option>
                <option value="PARTIALLY_FILLED">Partially Filled</option>
              </select>
            </div>
            <div className="flex items-end">
              <button
                onClick={() => setFilters({ symbol: '', status: '' })}
                className="btn-secondary w-full"
              >
                Clear Filters
              </button>
            </div>
          </div>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {/* Trades Table */}
        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : trades.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg">No trades found</p>
            <p className="text-gray-400 text-sm mt-2">
              Start trading to see your order history here
            </p>
            <a href="/dashboard/trade" className="btn-primary mt-4 inline-block">
              Create New Trade
            </a>
          </div>
        ) : (
          <div className="card overflow-hidden">
            <div className="overflow-x-auto">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      ID
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Symbol
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Side
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Type
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Quantity
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Price
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Status
                    </th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                      Date
                    </th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {trades.map((trade) => (
                    <tr key={trade.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                        #{trade.id}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {trade.symbol}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">
                        <span
                          className={`font-medium ${
                            trade.side === 'BUY' ? 'text-green-600' : 'text-red-600'
                          }`}
                        >
                          {trade.side}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {trade.order_type}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {trade.quantity}
                        {trade.executed_quantity > 0 && (
                          <span className="text-gray-500 text-xs block">
                            Exec: {trade.executed_quantity}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                        {trade.price ? `$${parseFloat(trade.price).toFixed(2)}` : 'Market'}
                        {trade.stop_price && (
                          <span className="text-gray-500 text-xs block">
                            Stop: ${parseFloat(trade.stop_price).toFixed(2)}
                          </span>
                        )}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`${getStatusBadge(trade.status)}`}>
                          {trade.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {formatDate(trade.created_at)}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Summary Stats */}
        {trades.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="card bg-blue-50">
              <p className="text-sm text-gray-600">Total Orders</p>
              <p className="text-2xl font-bold text-blue-700">{trades.length}</p>
            </div>
            <div className="card bg-green-50">
              <p className="text-sm text-gray-600">Filled Orders</p>
              <p className="text-2xl font-bold text-green-700">
                {trades.filter((t) => t.status === 'FILLED').length}
              </p>
            </div>
            <div className="card bg-yellow-50">
              <p className="text-sm text-gray-600">Pending Orders</p>
              <p className="text-2xl font-bold text-yellow-700">
                {trades.filter((t) => t.status === 'PENDING').length}
              </p>
            </div>
            <div className="card bg-red-50">
              <p className="text-sm text-gray-600">Failed Orders</p>
              <p className="text-2xl font-bold text-red-700">
                {trades.filter((t) => t.status === 'FAILED').length}
              </p>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default OrderHistory;
