import React, { useEffect, useState } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { botConfigService } from '../services/services';

const BotConfigs = () => {
  const [configs, setConfigs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showModal, setShowModal] = useState(false);
  const [editingConfig, setEditingConfig] = useState(null);
  const [formData, setFormData] = useState({
    name: '',
    api_key: '',
    api_secret: '',
    is_testnet: true,
    is_active: true,
  });

  useEffect(() => {
    fetchConfigs();
  }, []);

  const fetchConfigs = async () => {
    try {
      setLoading(true);
      const data = await botConfigService.getConfigs();
      setConfigs(data);
    } catch (err) {
      console.error('Error fetching configs:', err);
      setError('Failed to load bot configurations');
    } finally {
      setLoading(false);
    }
  };

  const handleOpenModal = (config = null) => {
    if (config) {
      setEditingConfig(config);
      setFormData({
        name: config.name,
        api_key: config.api_key,
        api_secret: config.api_secret,
        is_testnet: config.is_testnet,
        is_active: config.is_active,
      });
    } else {
      setEditingConfig(null);
      setFormData({
        name: '',
        api_key: '',
        api_secret: '',
        is_testnet: true,
        is_active: true,
      });
    }
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingConfig(null);
    setFormData({
      name: '',
      api_key: '',
      api_secret: '',
      is_testnet: true,
      is_active: true,
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    try {
      if (editingConfig) {
        await botConfigService.updateConfig(editingConfig.id, formData);
      } else {
        await botConfigService.createConfig(formData);
      }
      await fetchConfigs();
      handleCloseModal();
    } catch (err) {
      console.error('Error saving config:', err);
      setError(err.response?.data?.detail || 'Failed to save configuration');
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Are you sure you want to delete this configuration?')) {
      return;
    }

    try {
      await botConfigService.deleteConfig(id);
      await fetchConfigs();
    } catch (err) {
      console.error('Error deleting config:', err);
      setError('Failed to delete configuration');
    }
  };

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <h1 className="text-3xl font-bold text-gray-900">Bot Configurations</h1>
          <button onClick={() => handleOpenModal()} className="btn-primary">
            ➕ Add New Bot Config
          </button>
        </div>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {loading ? (
          <div className="flex items-center justify-center h-64">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          </div>
        ) : configs.length === 0 ? (
          <div className="card text-center py-12">
            <p className="text-gray-500 text-lg">No bot configurations found</p>
            <p className="text-gray-400 text-sm mt-2">
              Create your first bot configuration to start trading
            </p>
            <button onClick={() => handleOpenModal()} className="btn-primary mt-4">
              Create Bot Config
            </button>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {configs.map((config) => (
              <div key={config.id} className="card hover:shadow-lg transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">{config.name}</h3>
                    <div className="flex gap-2 mt-2">
                      <span
                        className={`badge ${
                          config.is_testnet ? 'badge-warning' : 'badge-info'
                        }`}
                      >
                        {config.is_testnet ? 'Testnet' : 'Live'}
                      </span>
                      <span
                        className={`badge ${
                          config.is_active ? 'badge-success' : 'badge-danger'
                        }`}
                      >
                        {config.is_active ? 'Active' : 'Inactive'}
                      </span>
                    </div>
                  </div>
                </div>

                <div className="space-y-2 text-sm">
                  <div>
                    <p className="text-gray-600">API Key</p>
                    <p className="font-mono text-xs bg-gray-100 p-2 rounded">
                      {config.api_key.substring(0, 20)}...
                    </p>
                  </div>
                  <div>
                    <p className="text-gray-600">Created</p>
                    <p className="text-gray-900">
                      {new Date(config.created_at).toLocaleDateString()}
                    </p>
                  </div>
                </div>

                <div className="flex gap-2 mt-4">
                  <button
                    onClick={() => handleOpenModal(config)}
                    className="flex-1 btn-secondary text-sm"
                  >
                    ✏️ Edit
                  </button>
                  <button
                    onClick={() => handleDelete(config.id)}
                    className="flex-1 btn-danger text-sm"
                  >
                    🗑️ Delete
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Modal */}
        {showModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-8 max-w-md w-full mx-4">
              <h2 className="text-2xl font-bold mb-4">
                {editingConfig ? 'Edit Bot Configuration' : 'New Bot Configuration'}
              </h2>

              <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Configuration Name
                  </label>
                  <input
                    type="text"
                    className="input-field"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    placeholder="My Trading Bot"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Binance API Key
                  </label>
                  <input
                    type="text"
                    className="input-field font-mono text-sm"
                    value={formData.api_key}
                    onChange={(e) => setFormData({ ...formData, api_key: e.target.value })}
                    placeholder="Your API Key"
                    required
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Binance API Secret
                  </label>
                  <input
                    type="password"
                    className="input-field font-mono text-sm"
                    value={formData.api_secret}
                    onChange={(e) =>
                      setFormData({ ...formData, api_secret: e.target.value })
                    }
                    placeholder="Your API Secret"
                    required
                  />
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_testnet"
                    checked={formData.is_testnet}
                    onChange={(e) =>
                      setFormData({ ...formData, is_testnet: e.target.checked })
                    }
                    className="rounded"
                  />
                  <label htmlFor="is_testnet" className="text-sm text-gray-700">
                    Use Testnet (Recommended for testing)
                  </label>
                </div>

                <div className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    id="is_active"
                    checked={formData.is_active}
                    onChange={(e) =>
                      setFormData({ ...formData, is_active: e.target.checked })
                    }
                    className="rounded"
                  />
                  <label htmlFor="is_active" className="text-sm text-gray-700">
                    Active
                  </label>
                </div>

                <div className="flex gap-3 mt-6">
                  <button type="submit" className="flex-1 btn-primary">
                    {editingConfig ? 'Update' : 'Create'}
                  </button>
                  <button
                    type="button"
                    onClick={handleCloseModal}
                    className="flex-1 btn-secondary"
                  >
                    Cancel
                  </button>
                </div>
              </form>
            </div>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
};

export default BotConfigs;
