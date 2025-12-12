# Quick Start Guide

Get your Crypto Trading Bot up and running in 5 minutes!

## Prerequisites Checklist

- [ ] Python 3.8+ installed
- [ ] Node.js 16+ installed
- [ ] Git installed
- [ ] Binance Testnet account created
- [ ] API credentials generated

## Step 1: Get Binance Testnet Credentials (2 minutes)

1. Visit https://testnet.binancefuture.com/
2. Click "Register" and create an account
3. After login, go to "API Management"
4. Create a new API key
5. **Important**: Save both API Key and Secret Key immediately!
6. Get test funds: Click your balance → "Get Test Funds"

## Step 2: Clone and Setup Backend (1 minute)

```bash
# Clone repository
git clone https://github.com/apoorvpandey048/Crypto-Trading-Bot.git
cd Crypto-Trading-Bot/backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
copy .env.example .env  # Windows
# or
cp .env.example .env    # Mac/Linux

# Edit .env file with your Binance credentials
# Use notepad, vim, or any text editor:
notepad .env  # Windows
nano .env     # Mac/Linux
```

In the `.env` file, update:
```env
BINANCE_API_KEY=your_api_key_from_binance
BINANCE_API_SECRET=your_api_secret_from_binance
BINANCE_TESTNET=True
```

## Step 3: Setup Frontend (1 minute)

```bash
# Open a new terminal
cd Crypto-Trading-Bot/frontend

# Install dependencies
npm install
```

## Step 4: Start the Application (30 seconds)

### Terminal 1 - Backend:
```bash
cd backend
python main.py
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
```

You should see:
```
  ➜  Local:   http://localhost:5173/
```

## Step 5: First Login (30 seconds)

1. Open browser: http://localhost:5173
2. Click "Create one now"
3. Fill registration form:
   - Email: your@email.com
   - Username: myusername
   - Password: (min 6 characters)
4. Click "Create account"
5. Login with your credentials

## Step 6: Configure Your Bot (30 seconds)

1. In dashboard, click "Bot Configs"
2. Click "➕ Add New Bot Config"
3. Fill in:
   - Name: "My First Bot"
   - API Key: (paste from Binance)
   - API Secret: (paste from Binance)
   - ✓ Use Testnet
   - ✓ Active
4. Click "Create"

## Step 7: Execute Your First Trade! (30 seconds)

1. Click "Trade" in sidebar
2. Fill trade form:
   - Symbol: BTCUSDT
   - Side: BUY
   - Order Type: MARKET
   - Quantity: 0.001
3. Click "Execute BUY Order"
4. Check "Order History" to see your trade!

## 🎉 Success! You're now trading on testnet!

## Quick Commands Reference

### Check Balance (CLI)
```bash
cd backend/bot
python cli.py balance
```

### Place Trade (CLI)
```bash
# Market order
python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001

# Limit order
python cli.py limit --symbol ETHUSDT --side SELL --quantity 0.01 --price 2000

# Stop-limit order
python cli.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.001 --stop-price 30000 --limit-price 29900
```

### View Orders (CLI)
```bash
python cli.py orders
python cli.py orders --symbol BTCUSDT
```

### Get Price (CLI)
```bash
python cli.py price --symbol BTCUSDT
```

## Troubleshooting

### "Module not found" error
```bash
# Make sure virtual environment is activated
# You should see (venv) in your terminal

# Reinstall dependencies
pip install -r requirements.txt
```

### "Cannot connect to Binance API"
- Verify API key and secret in `.env` file
- Check `BINANCE_TESTNET=True` in `.env`
- Ensure your Binance testnet account has test funds

### Frontend shows "Failed to fetch"
- Make sure backend is running on port 8000
- Check terminal for backend errors
- Try restarting the backend

### "Database locked" error
- Close any other instances of the app
- Delete `crypto_trading.db` and restart (will lose data)

### Port already in use
```bash
# Backend (8000):
# Windows:
netstat -ano | findstr :8000
# Kill the process using the port

# Mac/Linux:
lsof -ti:8000 | xargs kill -9

# Frontend (5173):
# Change port in vite.config.js or:
npm run dev -- --port 3000
```

## Next Steps

### Learn More
- 📖 Read full [README.md](README.md)
- 🔌 Check [API_DOCUMENTATION.md](API_DOCUMENTATION.md)
- 📈 Review [SCALING_NOTES.md](SCALING_NOTES.md)

### Explore Features
- ✅ Try different order types (Market, Limit, Stop-Limit)
- ✅ Create multiple bot configurations
- ✅ Use Notes feature for trading strategies
- ✅ Monitor your dashboard statistics
- ✅ Filter and search order history

### Practice Safe Trading
- ⚠️ Always use TESTNET first
- ⚠️ Start with small quantities
- ⚠️ Understand order types before using
- ⚠️ Never share your API credentials
- ⚠️ Keep your `.env` file secure

## Support

Having issues? Check:
1. All terminals show no errors
2. Virtual environment is activated
3. All dependencies are installed
4. `.env` file is configured correctly
5. Binance testnet account has funds

Still stuck? Open an issue on GitHub with:
- Error messages
- Steps to reproduce
- Screenshots (hide sensitive data!)

## Security Reminder

🔒 **NEVER commit `.env` file to Git!**
🔒 **Keep API credentials secret**
🔒 **Use TESTNET for learning**

---

Happy Trading! 🚀📈💰
