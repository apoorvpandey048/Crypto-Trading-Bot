import React, { useState, useEffect } from 'react';
import DashboardLayout from '../components/DashboardLayout';
import { tradingService, botConfigService } from '../services/services';

const Trade = () => {
  const [formData, setFormData] = useState({
    symbol: 'BTCUSDT',
    side: 'BUY',
    order_type: 'MARKET',
    quantity: '',
    price: '',
    stop_price: '',
    bot_config_id: null,
  });
  const [botConfigs, setBotConfigs] = useState([]);
  const [currentPrice, setCurrentPrice] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  useEffect(() => {
    fetchBotConfigs();
  }, []);

  useEffect(() => {
    if (formData.symbol) {
      fetchCurrentPrice();
    }
  }, [formData.symbol]);

  const fetchBotConfigs = async () => {
    try {
      const configs = await botConfigService.getConfigs();
      setBotConfigs(configs);
      if (configs.length > 0 && !formData.bot_config_id) {
        setFormData((prev) => ({ ...prev, bot_config_id: configs[0].id }));
      }
    } catch (err) {
      console.error('Error fetching bot configs:', err);
    }
  };

  const fetchCurrentPrice = async () => {
    try {
      const data = await tradingService.getPrice(formData.symbol);
      setCurrentPrice(data.price);
    } catch (err) {
      console.error('Error fetching price:', err);
      setCurrentPrice(null);
    }
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');

    // Validation
    if (!formData.quantity || parseFloat(formData.quantity) <= 0) {
      setError('Please enter a valid quantity');
      return;
    }

    if (formData.order_type === 'LIMIT' && (!formData.price || parseFloat(formData.price) <= 0)) {
      setError('Please enter a valid price for limit orders');
      return;
    }

    if (
      formData.order_type === 'STOP_LIMIT' &&
      (!formData.stop_price || !formData.price || parseFloat(formData.stop_price) <= 0 || parseFloat(formData.price) <= 0)
    ) {
      setError('Please enter valid stop price and limit price for stop-limit orders');
      return;
    }

    setLoading(true);

    try {
      const orderData = {
        symbol: formData.symbol.toUpperCase(),
        side: formData.side,
        order_type: formData.order_type,
        quantity: parseFloat(formData.quantity),
        bot_config_id: formData.bot_config_id || null,
      };

      if (formData.order_type === 'LIMIT') {
        orderData.price = parseFloat(formData.price);
      }

      if (formData.order_type === 'STOP_LIMIT') {
        orderData.price = parseFloat(formData.price);
        orderData.stop_price = parseFloat(formData.stop_price);
      }

      const result = await tradingService.executeOrder(orderData);

      if (result.success) {
        setSuccess(`Order executed successfully! Order ID: ${result.order_id}`);
        // Reset form
        setFormData((prev) => ({
          ...prev,
          quantity: '',
          price: '',
          stop_price: '',
        }));
      } else {
        setError(result.error || 'Failed to execute order');
      }
    } catch (err) {
      console.error('Error executing order:', err);
      setError(err.response?.data?.detail || 'Failed to execute order');
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardLayout>
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold text-gray-900">Execute Trade</h1>

        {error && (
          <div className="bg-red-50 border border-red-400 text-red-700 px-4 py-3 rounded">
            {error}
          </div>
        )}

        {success && (
          <div className="bg-green-50 border border-green-400 text-green-700 px-4 py-3 rounded">
            {success}
          </div>
        )}

        {/* Current Price Display */}
        {currentPrice && (
          <div className="card bg-gradient-to-r from-primary-50 to-primary-100">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Current Price</p>
                <p className="text-2xl font-bold text-primary-700">
                  {formData.symbol}: ${currentPrice.toFixed(2)}
                </p>
              </div>
              <button
                onClick={fetchCurrentPrice}
                className="btn-secondary"
              >
                🔄 Refresh
              </button>
            </div>
          </div>
        )}

        {/* Trade Form */}
        <form onSubmit={handleSubmit} className="card space-y-6">
          {/* Bot Config Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bot Configuration
            </label>
            <select
              name="bot_config_id"
              value={formData.bot_config_id || ''}
              onChange={handleChange}
              className="input-field"
              required
            >
              {botConfigs.length === 0 ? (
                <option value="">No bot configs available</option>
              ) : (
                botConfigs.map((config) => (
                  <option key={config.id} value={config.id}>
                    {config.name} {config.is_testnet ? '(Testnet)' : '(Live)'}
                  </option>
                ))
              )}
            </select>
            {botConfigs.length === 0 && (
              <p className="mt-1 text-sm text-red-600">
                Please create a bot configuration first in{' '}
                <a href="/dashboard/bot-configs" className="underline">
                  Bot Configs
                </a>
              </p>
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Symbol */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Trading Pair
              </label>
              <input
                type="text"
                name="symbol"
                value={formData.symbol}
                onChange={handleChange}
                className="input-field"
                placeholder="BTCUSDT"
                required
              />
            </div>

            {/* Side */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Side
              </label>
              <select
                name="side"
                value={formData.side}
                onChange={handleChange}
                className="input-field"
                required
              >
                <option value="BUY">Buy</option>
                <option value="SELL">Sell</option>
              </select>
            </div>

            {/* Order Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Order Type
              </label>
              <select
                name="order_type"
                value={formData.order_type}
                onChange={handleChange}
                className="input-field"
                required
              >
                <option value="MARKET">Market</option>
                <option value="LIMIT">Limit</option>
                <option value="STOP_LIMIT">Stop-Limit</option>
              </select>
            </div>

            {/* Quantity */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Quantity
              </label>
              <input
                type="number"
                name="quantity"
                value={formData.quantity}
                onChange={handleChange}
                className="input-field"
                placeholder="0.001"
                step="any"
                min="0"
                required
              />
            </div>

            {/* Price (for LIMIT and STOP_LIMIT) */}
            {(formData.order_type === 'LIMIT' || formData.order_type === 'STOP_LIMIT') && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  {formData.order_type === 'STOP_LIMIT' ? 'Limit Price' : 'Price'}
                </label>
                <input
                  type="number"
                  name="price"
                  value={formData.price}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="30000.00"
                  step="any"
                  min="0"
                  required
                />
              </div>
            )}

            {/* Stop Price (for STOP_LIMIT) */}
            {formData.order_type === 'STOP_LIMIT' && (
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Stop Price
                </label>
                <input
                  type="number"
                  name="stop_price"
                  value={formData.stop_price}
                  onChange={handleChange}
                  className="input-field"
                  placeholder="30500.00"
                  step="any"
                  min="0"
                  required
                />
              </div>
            )}
          </div>

          {/* Order Summary */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-2">Order Summary</h3>
            <div className="space-y-1 text-sm">
              <p>
                <span className="text-gray-600">Action:</span>{' '}
                <span className="font-medium">
                  {formData.side} {formData.quantity || '0'} {formData.symbol}
                </span>
              </p>
              <p>
                <span className="text-gray-600">Order Type:</span>{' '}
                <span className="font-medium">{formData.order_type}</span>
              </p>
              {formData.order_type === 'LIMIT' && formData.price && (
                <p>
                  <span className="text-gray-600">At Price:</span>{' '}
                  <span className="font-medium">${formData.price}</span>
                </p>
              )}
              {formData.order_type === 'STOP_LIMIT' && (
                <>
                  <p>
                    <span className="text-gray-600">Stop Price:</span>{' '}
                    <span className="font-medium">${formData.stop_price || '0'}</span>
                  </p>
                  <p>
                    <span className="text-gray-600">Limit Price:</span>{' '}
                    <span className="font-medium">${formData.price || '0'}</span>
                  </p>
                </>
              )}
              {formData.order_type === 'MARKET' && currentPrice && (
                <p>
                  <span className="text-gray-600">Estimated Value:</span>{' '}
                  <span className="font-medium">
                    ${(parseFloat(formData.quantity || 0) * currentPrice).toFixed(2)}
                  </span>
                </p>
              )}
            </div>
          </div>

          {/* Submit Button */}
          <div className="flex gap-4">
            <button
              type="submit"
              disabled={loading || botConfigs.length === 0}
              className={`flex-1 ${
                formData.side === 'BUY'
                  ? 'bg-green-600 hover:bg-green-700'
                  : 'bg-red-600 hover:bg-red-700'
              } text-white px-6 py-3 rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-offset-2 transition-colors disabled:bg-gray-400 disabled:cursor-not-allowed`}
            >
              {loading ? 'Executing...' : `Execute ${formData.side} Order`}
            </button>
          </div>
        </form>

        {/* Info Box */}
        <div className="card bg-blue-50">
          <h3 className="text-lg font-semibold mb-2 text-blue-900">ℹ️ Trading Tips</h3>
          <ul className="space-y-1 text-sm text-blue-800">
            <li>• <strong>Market Orders:</strong> Execute immediately at current market price</li>
            <li>• <strong>Limit Orders:</strong> Execute only when price reaches your specified limit</li>
            <li>
              • <strong>Stop-Limit Orders:</strong> Trigger at stop price, then execute as limit order
            </li>
            <li>• Always double-check your order details before executing</li>
            <li>• Make sure you have sufficient balance in your account</li>
          </ul>
        </div>
      </div>
    </DashboardLayout>
  );
};

export default Trade;
