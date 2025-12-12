import api from './api';

// Authentication endpoints
export const authService = {
  register: async (userData) => {
    const response = await api.post('/api/auth/register', userData);
    return response.data;
  },

  login: async (credentials) => {
    const formData = new FormData();
    formData.append('username', credentials.username);
    formData.append('password', credentials.password);
    
    const response = await api.post('/api/auth/login', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    
    if (response.data.access_token) {
      localStorage.setItem('token', response.data.access_token);
    }
    
    return response.data;
  },

  logout: async () => {
    try {
      await api.post('/api/auth/logout');
    } finally {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
    }
  },

  getCurrentUser: async () => {
    const response = await api.get('/api/auth/me');
    return response.data;
  },
};

// User endpoints
export const userService = {
  getProfile: async () => {
    const response = await api.get('/api/users/profile');
    return response.data;
  },

  updateProfile: async (userData) => {
    const response = await api.put('/api/users/profile', userData);
    return response.data;
  },

  deleteProfile: async () => {
    const response = await api.delete('/api/users/profile');
    return response.data;
  },
};

// Trading endpoints
export const tradingService = {
  executeOrder: async (orderData) => {
    const response = await api.post('/api/trading/execute', orderData);
    return response.data;
  },

  getTrades: async (params = {}) => {
    const response = await api.get('/api/trading/trades', { params });
    return response.data;
  },

  getTrade: async (tradeId) => {
    const response = await api.get(`/api/trading/trades/${tradeId}`);
    return response.data;
  },

  getBalance: async (botConfigId = null) => {
    const params = botConfigId ? { bot_config_id: botConfigId } : {};
    const response = await api.get('/api/trading/balance', { params });
    return response.data;
  },

  getPrice: async (symbol, botConfigId = null) => {
    const params = botConfigId ? { bot_config_id: botConfigId } : {};
    const response = await api.get(`/api/trading/price/${symbol}`, { params });
    return response.data;
  },

  getStats: async () => {
    const response = await api.get('/api/trading/stats');
    return response.data;
  },
};

// Bot config endpoints
export const botConfigService = {
  getConfigs: async () => {
    const response = await api.get('/api/bot-configs/');
    return response.data;
  },

  getConfig: async (configId) => {
    const response = await api.get(`/api/bot-configs/${configId}`);
    return response.data;
  },

  createConfig: async (configData) => {
    const response = await api.post('/api/bot-configs/', configData);
    return response.data;
  },

  updateConfig: async (configId, configData) => {
    const response = await api.put(`/api/bot-configs/${configId}`, configData);
    return response.data;
  },

  deleteConfig: async (configId) => {
    const response = await api.delete(`/api/bot-configs/${configId}`);
    return response.data;
  },
};

// Notes endpoints
export const noteService = {
  getNotes: async (params = {}) => {
    const response = await api.get('/api/notes/', { params });
    return response.data;
  },

  getNote: async (noteId) => {
    const response = await api.get(`/api/notes/${noteId}`);
    return response.data;
  },

  createNote: async (noteData) => {
    const response = await api.post('/api/notes/', noteData);
    return response.data;
  },

  updateNote: async (noteId, noteData) => {
    const response = await api.put(`/api/notes/${noteId}`, noteData);
    return response.data;
  },

  deleteNote: async (noteId) => {
    const response = await api.delete(`/api/notes/${noteId}`);
    return response.data;
  },
};
