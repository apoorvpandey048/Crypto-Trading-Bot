# Crypto Trading Bot - Full Stack Application

A comprehensive cryptocurrency trading bot with a modern web interface, built with Python FastAPI backend and React frontend. Features include automated trading on Binance Futures Testnet, JWT authentication, and a complete dashboard for managing trades, bot configurations, and notes.

## ✅ **FULLY FUNCTIONAL & TESTED**
All core features have been tested and verified on Binance Futures Testnet. See [TRADING_TEST_RESULTS.md](./TRADING_TEST_RESULTS.md) for detailed test results.

## 🚀 Features

### Trading Bot Core
- ✅ Market, Limit, and Stop-Limit orders
- ✅ Binance Futures Testnet integration
- ✅ Real-time price tracking
- ✅ Order execution history
- ✅ Multiple bot configurations
- ✅ Comprehensive logging and error handling
- ✅ CLI interface for direct trading

### Backend (FastAPI)
- ✅ JWT-based authentication
- ✅ RESTful API design
- ✅ SQLAlchemy ORM with SQLite/PostgreSQL support
- ✅ Password hashing with bcrypt
- ✅ CORS middleware
- ✅ Comprehensive error handling
- ✅ API documentation (Swagger/OpenAPI)

### Frontend (React + Vite)
- ✅ Modern, responsive UI with TailwindCSS
- ✅ Protected routes and authentication flow
- ✅ Real-time dashboard with statistics
- ✅ Trade execution interface
- ✅ Order history with filtering
- ✅ Bot configuration management
- ✅ Notes CRUD functionality
- ✅ User profile management

## 📋 Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn
- Binance Testnet account with API credentials

## 🔧 Installation

### 1. Clone the Repository

```bash
git clone https://github.com/apoorvpandey048/Crypto-Trading-Bot.git
cd Crypto-Trading-Bot
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac

# Edit .env file and add your Binance API credentials
# BINANCE_API_KEY=your_api_key_here
# BINANCE_API_SECRET=your_api_secret_here
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Create .env file (optional)
echo "VITE_API_URL=http://localhost:8000" > .env
```

## 🎯 Getting Started

### 1. Register for Binance Testnet

1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com/)
2. Sign up for a testnet account
3. Generate API credentials:
   - Go to API Management
   - Create new API key
   - Save your API Key and Secret Key
4. Add test funds to your testnet account (usually available in account settings)

### 2. Configure Backend

Edit `backend/.env`:

```env
BINANCE_API_KEY=your_testnet_api_key_here
BINANCE_API_SECRET=your_testnet_api_secret_here
BINANCE_TESTNET=True
DATABASE_URL=sqlite:///./crypto_trading.db
SECRET_KEY=your-secret-key-here-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Start the Backend Server

```bash
cd backend
python main.py
```

The API will be available at `http://localhost:8000`
- API Documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### 4. Start the Frontend Development Server

```bash
cd frontend
npm run dev
```

The application will be available at `http://localhost:5173`

## 📖 Usage

### Web Interface

1. **Register an Account**
   - Navigate to `http://localhost:5173/register`
   - Create your account with email, username, and password

2. **Login**
   - Go to `http://localhost:5173/login`
   - Enter your credentials

3. **Configure Bot**
   - Navigate to "Bot Configs" in the dashboard
   - Add your Binance API credentials
   - Enable testnet mode

4. **Execute Trades**
   - Go to "Trade" section
   - Select symbol, side, order type, and quantity
   - Submit order

5. **Monitor Orders**
   - View order history in "Order History"
   - Filter by symbol or status
   - Track execution status

### CLI Interface

```bash
cd backend/bot

# Place a market order
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001

# Place a limit order
python cli.py limit --symbol ETHUSDT --side SELL --quantity 0.01 --price 2000

# Place a stop-limit order
python cli.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.001 --stop-price 30000 --limit-price 29900

# Check account balance
python cli.py balance

# View open orders
python cli.py orders --symbol BTCUSDT

# Cancel an order
python cli.py cancel --symbol BTCUSDT --order-id 12345

# Get current price
python cli.py price --symbol BTCUSDT
```

## 🏗️ Project Structure

```
Crypto-Trading-Bot/
├── backend/
│   ├── bot/
│   │   ├── basic_bot.py        # Trading bot implementation
│   │   ├── cli.py              # Command-line interface
│   │   └── __init__.py
│   ├── routes/
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── users.py            # User management
│   │   ├── trading.py          # Trading endpoints
│   │   ├── bot_configs.py      # Bot configuration
│   │   ├── notes.py            # Notes CRUD
│   │   └── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration management
│   ├── database.py             # Database setup
│   ├── models.py               # SQLAlchemy models
│   ├── schemas.py              # Pydantic schemas
│   ├── auth.py                 # Authentication logic
│   ├── requirements.txt        # Python dependencies
│   └── .env.example           # Environment variables template
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── DashboardLayout.jsx
│   │   │   └── ProtectedRoute.jsx
│   │   ├── context/
│   │   │   └── AuthContext.jsx
│   │   ├── pages/
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── Trade.jsx
│   │   │   ├── OrderHistory.jsx
│   │   │   ├── BotConfigs.jsx
│   │   │   ├── Notes.jsx
│   │   │   └── Profile.jsx
│   │   ├── services/
│   │   │   ├── api.js
│   │   │   └── services.js
│   │   ├── App.jsx
│   │   ├── main.jsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.js
│   ├── tailwind.config.js
│   └── index.html
└── README.md
```

## 🔐 Security Features

- ✅ **Password Hashing**: Bcrypt for secure password storage
- ✅ **JWT Authentication**: Secure token-based authentication
- ✅ **Protected Routes**: Client-side route protection
- ✅ **API Key Security**: API credentials stored securely (encrypt in production)
- ✅ **CORS Protection**: Configured allowed origins
- ✅ **Input Validation**: Server and client-side validation
- ✅ **Error Handling**: Comprehensive error handling throughout

## 📊 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout user

### Users
- `GET /api/users/profile` - Get user profile
- `PUT /api/users/profile` - Update profile
- `DELETE /api/users/profile` - Delete account

### Trading
- `POST /api/trading/execute` - Execute trade order
- `GET /api/trading/trades` - Get trade history
- `GET /api/trading/trades/{id}` - Get specific trade
- `GET /api/trading/balance` - Get account balance
- `GET /api/trading/price/{symbol}` - Get current price
- `GET /api/trading/stats` - Get dashboard statistics

### Bot Configurations
- `GET /api/bot-configs/` - List bot configurations
- `POST /api/bot-configs/` - Create bot configuration
- `GET /api/bot-configs/{id}` - Get specific configuration
- `PUT /api/bot-configs/{id}` - Update configuration
- `DELETE /api/bot-configs/{id}` - Delete configuration

### Notes
- `GET /api/notes/` - List notes (with search)
- `POST /api/notes/` - Create note
- `GET /api/notes/{id}` - Get specific note
- `PUT /api/notes/{id}` - Update note
- `DELETE /api/notes/{id}` - Delete note

## 🚀 Scaling for Production

### Backend Scaling

1. **Database**
   - Switch from SQLite to PostgreSQL
   - Implement connection pooling
   - Add database replicas for read operations
   - Use Redis for caching

2. **API Security**
   - Encrypt API keys at rest
   - Implement rate limiting
   - Add request validation middleware
   - Use HTTPS only

3. **Infrastructure**
   - Deploy with Gunicorn/Uvicorn workers
   - Use Nginx as reverse proxy
   - Implement load balancing
   - Add monitoring (Prometheus, Grafana)

4. **Performance**
   - Implement async database operations
   - Add background task queue (Celery)
   - Cache frequent queries
   - Optimize database indexes

### Frontend Scaling

1. **Build Optimization**
   - Enable production build optimizations
   - Implement code splitting
   - Use CDN for static assets
   - Enable gzip compression

2. **State Management**
   - Implement Redux or Zustand for complex state
   - Add query caching (React Query)
   - Optimize re-renders

3. **Performance**
   - Lazy load routes and components
   - Implement virtual scrolling for large lists
   - Add service workers for offline support
   - Optimize images and assets

4. **Deployment**
   - Deploy to Vercel, Netlify, or AWS S3
   - Enable CDN distribution
   - Implement CI/CD pipeline
   - Add error tracking (Sentry)

### Architecture Recommendations

```
Production Architecture:

                    ┌─────────────┐
                    │   CDN       │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  Frontend   │
                    │  (Vercel)   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  API Gateway│
                    │  (Nginx)    │
                    └──────┬──────┘
                           │
                ┌──────────┴──────────┐
                │                     │
         ┌──────▼──────┐      ┌─────▼─────┐
         │  Load       │      │  Redis    │
         │  Balancer   │      │  Cache    │
         └──────┬──────┘      └───────────┘
                │
    ┌───────────┼───────────┐
    │           │           │
┌───▼───┐   ┌───▼───┐   ┌───▼───┐
│FastAPI│   │FastAPI│   │FastAPI│
│ API 1 │   │ API 2 │   │ API 3 │
└───┬───┘   └───┬───┘   └───┬───┘
    │           │           │
    └───────────┼───────────┘
                │
         ┌──────▼──────┐
         │ PostgreSQL  │
         │  (Primary)  │
         └──────┬──────┘
                │
         ┌──────▼──────┐
         │ PostgreSQL  │
         │  (Replica)  │
         └─────────────┘
```

## 🧪 Testing

```bash
# Backend tests (to be implemented)
cd backend
pytest

# Frontend tests (to be implemented)
cd frontend
npm test
```

## 📝 Environment Variables

### Backend (.env)
```env
BINANCE_API_KEY=your_api_key
BINANCE_API_SECRET=your_api_secret
BINANCE_TESTNET=True
DATABASE_URL=sqlite:///./crypto_trading.db
SECRET_KEY=your-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
HOST=0.0.0.0
PORT=8000
```

### Frontend (.env)
```env
VITE_API_URL=http://localhost:8000
```

## 🐛 Troubleshooting

### Common Issues

1. **Backend fails to start**
   - Check if Python virtual environment is activated
   - Ensure all dependencies are installed
   - Verify .env file exists with correct values

2. **Cannot connect to Binance API**
   - Verify API credentials are correct
   - Check if testnet mode is enabled
   - Ensure API key has necessary permissions

3. **Frontend cannot reach backend**
   - Check if backend is running on port 8000
   - Verify CORS settings in backend
   - Check browser console for errors

4. **Authentication issues**
   - Clear browser localStorage
   - Check if JWT secret is configured
   - Verify token expiration time

## 📄 License

This project is licensed under the MIT License.

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Contact

- GitHub: [@apoorvpandey048](https://github.com/apoorvpandey048)
- Repository: [Crypto-Trading-Bot](https://github.com/apoorvpandey048/Crypto-Trading-Bot)

## 🙏 Acknowledgments

- Binance API documentation
- FastAPI framework
- React and Vite teams
- TailwindCSS
- python-binance library

---

**⚠️ Disclaimer**: This bot is for educational and testing purposes only. Use at your own risk. Always test thoroughly on testnet before considering any live trading. Cryptocurrency trading carries significant risks.
