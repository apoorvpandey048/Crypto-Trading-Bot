# Setup Guide for New Users

This guide will help you set up and run the Crypto Trading Bot from scratch.

## Prerequisites

Before you begin, ensure you have:
- Python 3.8+ installed
- Node.js 16+ installed
- Git installed
- A Binance Futures Testnet account

## Step 1: Clone the Repository

```bash
git clone https://github.com/apoorvpandey048/Crypto-Trading-Bot.git
cd Crypto-Trading-Bot
```

## Step 2: Get Binance Futures Testnet API Keys

1. Visit [Binance Futures Testnet](https://testnet.binancefuture.com)
2. Register/Login with your email
3. Go to **API Key** section
4. Click **Generate HMAC_SHA256 Key**
5. Save your:
   - API Key
   - Secret Key
6. Configure API Permissions:
   - ✅ Enable Reading
   - ✅ Enable Spot & Margin Trading
   - ✅ Enable Futures
7. (Optional) Add your IP to whitelist for security

## Step 3: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\Activate.ps1
# Windows CMD:
venv\Scripts\activate.bat
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file from template
# Windows:
copy .env.example .env
# Linux/Mac:
cp .env.example .env
```

### Configure Backend Environment

Edit the `.env` file and add your API credentials:

```env
# Binance Futures Testnet API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_TESTNET=True

# Database Configuration
DATABASE_URL=sqlite:///./crypto_trading.db

# JWT Configuration
SECRET_KEY=your-secret-key-here-change-this-to-something-random
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:5173,http://localhost:3000

# Server Configuration
HOST=0.0.0.0
PORT=8001
```

**Important**: 
- Replace `your_api_key_here` with your actual Binance API key
- Replace `your_api_secret_here` with your actual Binance API secret
- Replace `your-secret-key-here-change-this-to-something-random` with a secure random string

### Start the Backend Server

```bash
# Make sure you're in the backend directory with venv activated
python -m uvicorn main:app --host 0.0.0.0 --port 8001 --reload
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8001 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
```

✅ Backend is now running at http://localhost:8001
✅ API documentation available at http://localhost:8001/docs

## Step 4: Frontend Setup

Open a **new terminal** window:

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

You should see:
```
  VITE v5.4.21  ready in XXX ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
  ➜  press h + enter to show help
```

✅ Frontend is now running at http://localhost:5173

## Step 5: Test the Application

### Access the Web Interface

1. Open your browser and go to http://localhost:5173
2. You should see the login page
3. Click "Register" to create a new account
4. After registration, login with your credentials

### Verify Backend API

Open http://localhost:8001/docs in your browser to see the interactive API documentation.

### Run Automated Tests (Optional)

To verify everything is working:

```bash
cd backend
# Make sure venv is activated
python test_complete_system.py
```

**Note**: You need to add your API keys to the test files before running tests:
- Edit `test_complete_system.py`
- Replace `your_futures_testnet_api_key_here` with your actual API key
- Replace `your_futures_testnet_api_secret_here` with your actual API secret

## Step 6: Start Trading

1. **Create a Bot Configuration**:
   - Go to "Bot Configs" page
   - Click "New Bot Config"
   - Enter your Binance API credentials
   - Save the configuration

2. **Execute Your First Trade**:
   - Go to "Trade" page
   - Select your bot configuration
   - Choose a trading pair (e.g., BTCUSDT)
   - Select order type (Market/Limit/Stop-Limit)
   - Enter quantity
   - Click "Execute Trade"

3. **View Trade History**:
   - Go to "Order History" page
   - See all your executed trades
   - Filter by status, symbol, etc.

4. **Check Dashboard**:
   - View trading statistics
   - See account balance
   - Monitor performance

## Troubleshooting

### Backend Issues

**Port 8001 already in use**:
```bash
# Windows PowerShell:
Get-Process -Id (Get-NetTCPConnection -LocalPort 8001).OwningProcess | Stop-Process -Force

# Linux/Mac:
lsof -ti:8001 | xargs kill -9
```

**Import errors**:
```bash
pip install --upgrade -r requirements.txt
```

**Database errors**:
```bash
# Delete and recreate the database
rm crypto_trading.db
python main.py  # Will create new database
```

### Frontend Issues

**npm install fails**:
```bash
# Clear npm cache
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

**Port 5173 already in use**:
Edit `vite.config.js` and change the port:
```js
export default defineConfig({
  server: {
    port: 3000,  // Change to any available port
  }
})
```

### API Connection Issues

**"Invalid API key" error**:
- Verify your API keys are correct
- Check that you're using **Futures Testnet** keys (not Spot Testnet)
- Ensure API permissions are enabled
- If using IP whitelist, add your current IP

**Get your IP address**:
```bash
# Windows PowerShell:
(Invoke-RestMethod -Uri "https://api.ipify.org?format=json").ip

# Linux/Mac:
curl https://api.ipify.org?format=json
```

## Security Notes

⚠️ **Important Security Reminders**:

1. **Never commit `.env` file** - It's in `.gitignore` for a reason
2. **Never share your API keys** - They provide access to your account
3. **Use testnet for learning** - Don't risk real money until you're confident
4. **Enable IP whitelist** - Restricts API access to specific IPs
5. **Use different keys for prod** - Never use testnet keys in production

## Next Steps

Once everything is running:

1. Read [USAGE_GUIDE.md](./USAGE_GUIDE.md) for detailed feature documentation
2. Check [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) for API reference
3. See [TRADING_TEST_RESULTS.md](./TRADING_TEST_RESULTS.md) for example test results
4. Review [SCALING_NOTES.md](./SCALING_NOTES.md) for production deployment

## Getting Help

If you encounter issues:

1. Check [TEST_LOG.md](./TEST_LOG.md) for common problems and solutions
2. Review error messages in terminal/console
3. Check API documentation at http://localhost:8001/docs
4. Open an issue on GitHub with:
   - Error message
   - Steps to reproduce
   - Your environment (OS, Python version, Node version)

## Success Checklist

Before you start trading, verify:

- ✅ Backend running on http://localhost:8001
- ✅ Frontend running on http://localhost:5173
- ✅ Can register and login
- ✅ Bot configuration created with valid API keys
- ✅ Can fetch real-time prices
- ✅ Test trade executed successfully

**Congratulations! You're ready to start trading! 🎉**

---

*For detailed usage instructions, see USAGE_GUIDE.md*  
*For API reference, see API_DOCUMENTATION.md*  
*For production deployment, see SCALING_NOTES.md*
