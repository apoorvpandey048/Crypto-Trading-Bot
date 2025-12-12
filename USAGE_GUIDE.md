# 🚀 Complete Setup and Usage Guide

## 📋 Table of Contents
1. [Prerequisites](#prerequisites)
2. [Installation](#installation)
3. [Getting Binance Test API Keys](#getting-binance-test-api-keys)
4. [First-Time Setup](#first-time-setup)
5. [Using the Trading Bot](#using-the-trading-bot)
6. [Testing](#testing)
7. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

- **Python 3.11+** (Tested with Python 3.13.1)
- **Node.js 18+** and npm
- **Git** (for cloning the repository)
- A **Binance Testnet account** (free, no real money required)

---

## 📥 Installation

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
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
.\venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
cp .env.example .env
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install
```

---

## 🔑 Getting Binance Test API Keys

### Step 1: Register on Binance Testnet
1. Go to https://testnet.binancefuture.com/
2. Click "Sign in" and register using your GitHub or Google account
3. **This is a TEST environment** - no real money is involved

### Step 2: Generate API Keys
1. After logging in, click on your **profile icon** (top right)
2. Select **"API Key"**
3. Click **"Generate HMAC_SHA256 Key"**
4. **Copy** both:
   - **API Key** (starts with letters/numbers, ~64 characters)
   - **Secret Key** (longer string, ~64 characters)

### Step 3: Enable Trading Permissions
⚠️ **Important**: By default, API keys are read-only

1. Click **"Edit restrictions"** on your API key
2. Check one or more of these options:
   - ✅ **Enable Spot & Margin Trading**
   - ✅ **Permits Universal Transfer**
3. Click **Save**

**Security Note**: Keep your API keys secure and never commit them to Git!

---

## 🎯 First-Time Setup

### 1. Start the Backend Server

```bash
cd backend
.\venv\Scripts\Activate.ps1  # Activate virtual environment
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Application startup complete.
```

### 2. Start the Frontend Server

In a **new terminal**:

```bash
cd frontend
npm run dev
```

You should see:
```
VITE v5.4.21  ready in 278 ms
➜  Local:   http://localhost:5173/
```

### 3. Access the Application

Open your browser and go to: **http://localhost:5173**

---

## 🎮 Using the Trading Bot

### Step 1: Register Your Account

1. Click **"Register"** on the homepage
2. Fill in:
   - **Email**: your@email.com
   - **Username**: your_username
   - **Password**: minimum 6 characters
   - **Full Name**: (optional)
3. Click **"Register"**
4. You'll be redirected to the login page

### Step 2: Login

1. Enter your **username** and **password**
2. Click **"Login"**
3. You'll be redirected to the **Dashboard**

### Step 3: Add Bot Configuration

1. Click **"Bot Configs"** in the sidebar
2. Click **"Add New Configuration"**
3. Fill in the form:
   - **Name**: e.g., "My Trading Bot"
   - **API Key**: paste your Binance API key
   - **API Secret**: paste your Binance API secret
   - **Testnet**: ✅ Check this box (we're using testnet)
   - **Active**: ✅ Check this box
4. Click **"Create Configuration"**

### Step 4: Execute Your First Trade

1. Click **"Trade"** in the sidebar
2. Select your **bot configuration** from the dropdown
3. Fill in the trade details:
   - **Symbol**: BTCUSDT (or ETHUSDT, BNBUSDT, etc.)
   - **Side**: BUY or SELL
   - **Order Type**: 
     - **MARKET**: Execute immediately at current price
     - **LIMIT**: Set your desired price
     - **STOP_LIMIT**: Set stop price and limit price
   - **Quantity**: Amount to trade (e.g., 0.001 for BTC)
   - **Price**: (only for LIMIT and STOP_LIMIT orders)
4. Click **"Execute Trade"**

### Step 5: View Your Results

#### Dashboard
- Shows your **account balance**
- Displays **trading statistics**:
  - Total trades
  - Successful trades
  - Failed trades
  - Pending trades
- Lists all **assets** in your account

#### Order History
- View all your **past trades**
- Filter by:
  - Symbol
  - Order type
  - Status
- See detailed information about each trade

#### Bot Configs
- Manage multiple bot configurations
- Edit or delete configurations
- Activate/deactivate bots

#### Notes
- Create notes about your trading strategies
- Organize notes by category
- Search through your notes

---

## 🧪 Testing

### Automated Testing

We've included a comprehensive test suite:

```bash
cd backend
.\venv\Scripts\Activate.ps1
python test_complete_system.py
```

This will test:
- ✅ Health check endpoint
- ✅ User registration & authentication
- ✅ Bot configuration management
- ✅ Account balance retrieval
- ✅ Price fetching
- ✅ CRUD operations (Notes)
- ✅ Trading stats

Test results are saved to `test_results.log`

### Manual Testing via CLI

The bot includes a CLI for direct trading:

```bash
cd backend
.\venv\Scripts\Activate.ps1
python -m bot.cli --help
```

**Examples**:

```bash
# Get account balance
python -m bot.cli balance --api-key YOUR_KEY --api-secret YOUR_SECRET

# Get current price
python -m bot.cli price BTCUSDT --api-key YOUR_KEY --api-secret YOUR_SECRET

# Execute market order
python -m bot.cli market BTCUSDT BUY 0.001 --api-key YOUR_KEY --api-secret YOUR_SECRET

# Execute limit order
python -m bot.cli limit BTCUSDT BUY 0.001 --price 50000 --api-key YOUR_KEY --api-secret YOUR_SECRET
```

---

## 🐛 Troubleshooting

### Issue: Backend won't start - Port 8001 already in use

**Solution**:
```powershell
# Find and kill the process
$port = Get-NetTCPConnection -LocalPort 8001 | Select-Object -ExpandProperty OwningProcess
Stop-Process -Id $port -Force
```

Or use a different port:
```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8002 --reload
```
(Update `frontend/vite.config.js` and `frontend/src/services/api.js` to use port 8002)

### Issue: "Registration failed" error

**Cause**: bcrypt version incompatibility

**Solution**: Ensure bcrypt 4.1.3 is installed:
```bash
pip install bcrypt==4.1.3
```

### Issue: "Invalid API-key" error

**Possible causes**:
1. API key/secret incorrect - double-check your credentials
2. API key permissions not enabled - enable trading permissions in Binance Testnet
3. IP restrictions - use "Unrestricted" or add your IP to whitelist

### Issue: Frontend can't connect to backend

**Solution**: Check CORS settings in `backend/.env`:
```
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000
```

### Issue: Database errors

**Solution**: Delete and recreate the database:
```bash
cd backend
Remove-Item crypto_trading.db  # Windows
# rm crypto_trading.db  # Linux/Mac
python -m uvicorn main:app  # Will recreate tables
```

---

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

---

## 🔒 Security Best Practices

1. **Never commit `.env` files** to Git
2. **Never share your API keys** publicly
3. **Use testnet** for development and testing
4. **Enable IP restrictions** on Binance for production
5. **Use environment variables** for sensitive data
6. **Regularly rotate** your API keys
7. **Monitor your API usage** to detect unusual activity

---

## 📚 Additional Resources

- [Binance Testnet Documentation](https://testnet.binancefuture.com/en/futures/BTCUSDT)
- [Python-Binance Library](https://python-binance.readthedocs.io/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [React Documentation](https://react.dev/)

---

## 🤝 Support

For issues or questions:
1. Check the [Troubleshooting](#troubleshooting) section
2. Review the [API Documentation](#api-documentation)
3. Check the test results in `backend/test_results.log`
4. Open an issue on GitHub

---

## ⚠️ Disclaimer

This trading bot is for **educational purposes** only. Always use the **Binance Testnet** for testing. Never use real funds until you fully understand the risks involved in cryptocurrency trading.

**Cryptocurrency trading involves substantial risk of loss and is not suitable for everyone.**

---

**Happy Trading! 🚀**
