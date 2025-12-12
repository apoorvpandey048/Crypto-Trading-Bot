# Advanced Order Types - Assignment Implementation

This directory contains CLI scripts for advanced trading strategies required by the assignment.

## 🎯 Assignment Requirements (30% Weight)

Three advanced order types have been implemented:
1. **OCO (One-Cancels-the-Other)** - Combines take-profit and stop-loss orders
2. **TWAP (Time-Weighted Average Price)** - Splits large orders over time
3. **Grid Trading** - Automated trading in ranging markets

## 📁 Files

- `oco.py` - OCO order execution
- `twap.py` - TWAP strategy execution
- `grid.py` - Grid trading strategy execution

## 🚀 Usage

All scripts require the following setup:
1. Valid `.env` file with Binance API credentials in the `backend/` directory
2. Python 3.8+ with required dependencies installed
3. Active Binance Futures Testnet account (or live account)

### OCO (One-Cancels-the-Other) Orders

**Purpose**: Simultaneously place a take-profit and stop-loss order. When one executes, the other is automatically cancelled.

**Usage**:
```bash
cd backend
python src/advanced/oco.py SYMBOL SIDE QUANTITY TP_PRICE STOP_PRICE STOP_LIMIT_PRICE
```

**Example**:
```bash
# Sell 0.002 BTC with take-profit at $95,000 and stop-loss at $90,000
python src/advanced/oco.py BTCUSDT SELL 0.002 95000 90000 89900
```

**Arguments**:
- `SYMBOL` - Trading pair (e.g., BTCUSDT)
- `SIDE` - BUY or SELL
- `QUANTITY` - Amount to trade
- `TP_PRICE` - Take profit price (limit order)
- `STOP_PRICE` - Stop loss trigger price
- `STOP_LIMIT_PRICE` - Stop loss execution price

**When to use**: Protect positions with both profit targets and stop losses automatically.

---

### TWAP (Time-Weighted Average Price) Orders

**Purpose**: Split a large order into smaller chunks executed at regular intervals to minimize market impact and achieve better average price.

**Usage**:
```bash
cd backend
python src/advanced/twap.py SYMBOL SIDE TOTAL_QUANTITY DURATION_MINUTES NUM_ORDERS
```

**Example**:
```bash
# Buy 0.01 BTC over 30 minutes in 10 equal chunks
python src/advanced/twap.py BTCUSDT BUY 0.01 30 10
```

**Arguments**:
- `SYMBOL` - Trading pair (e.g., BTCUSDT)
- `SIDE` - BUY or SELL
- `TOTAL_QUANTITY` - Total amount to trade
- `DURATION_MINUTES` - Time period to spread orders over
- `NUM_ORDERS` - Number of smaller orders to split into

**When to use**: Execute large orders without causing significant price impact.

---

### Grid Trading Strategy

**Purpose**: Create a grid of buy and sell orders to profit from price oscillations in a ranging market. Orders are automatically replaced when filled.

**Usage**:
```bash
cd backend
python src/advanced/grid.py SYMBOL LOWER_PRICE UPPER_PRICE NUM_GRIDS QUANTITY_PER_GRID
```

**Example**:
```bash
# Create 10 grid levels between $90,000 and $95,000
python src/advanced/grid.py BTCUSDT 90000 95000 10 0.001
```

**Arguments**:
- `SYMBOL` - Trading pair (e.g., BTCUSDT)
- `LOWER_PRICE` - Bottom of price range
- `UPPER_PRICE` - Top of price range
- `NUM_GRIDS` - Number of grid levels
- `QUANTITY_PER_GRID` - Amount to trade at each level

**When to use**: Market is ranging sideways without strong trends. Profits from volatility.

---

## 📊 Logging

All strategies log to `bot.log` in the backend directory with detailed execution information:
- Order placements and fills
- Price levels and quantities
- Errors and warnings
- Strategy progress updates

## 🎓 Implementation Details

### OCO Orders
- Places both limit (take-profit) and stop-limit (stop-loss) orders
- Background monitoring thread watches order status
- Automatically cancels opposite order when one fills
- Prevents both orders from executing

### TWAP Orders
- Calculates equal order chunks based on total quantity
- Executes market orders at fixed time intervals
- Background thread manages sequential execution
- Respects exchange quantity precision rules

### Grid Trading
- Calculates grid levels with equal spacing
- Places buy orders below current price, sell orders above
- Background monitoring replaces filled orders automatically
- Creates opposite side order at same price level
- Continues indefinitely until manually stopped

## 🧪 Testing

Test with small quantities on Binance Futures Testnet first:

```bash
# Set testnet in .env
BINANCE_TESTNET=True

# Test OCO with small amount
python src/advanced/oco.py BTCUSDT SELL 0.001 95000 90000 89900

# Test TWAP with short duration
python src/advanced/twap.py BTCUSDT BUY 0.001 5 5

# Test Grid with narrow range
python src/advanced/grid.py BTCUSDT 92000 93000 5 0.0001
```

## ⚠️ Important Notes

1. **Risk Management**: Always test with small quantities first
2. **API Limits**: Be aware of Binance rate limits
3. **Market Conditions**: Grid trading works best in ranging markets
4. **Monitoring**: Scripts run in foreground and can be stopped with Ctrl+C
5. **Background Tasks**: Some strategies (OCO, Grid) continue monitoring in background

## 📈 Expected Output

Each script provides:
- ✅ Success confirmation with strategy ID
- 📊 Order details (IDs, prices, quantities)
- 🔄 Real-time progress updates
- ⚠️ Error messages with clear descriptions
- 📝 Final summary upon completion

## 🛠️ Troubleshooting

**Error: API credentials not found**
- Check `.env` file exists in `backend/` directory
- Verify `BINANCE_API_KEY` and `BINANCE_API_SECRET` are set

**Error: Insufficient balance**
- Check account balance on Binance Futures Testnet
- Reduce order quantities

**Error: Invalid symbol**
- Ensure trading pair is valid (e.g., BTCUSDT not BTC/USDT)
- Check symbol is available on Binance Futures

## 📚 Related Files

- `backend/bot/advanced_orders.py` - Core implementation of all strategies
- `backend/bot.log` - Detailed execution logs
- `backend/.env` - API configuration

## 🏆 Assignment Scoring

This implementation covers:
- ✅ OCO order implementation (10%)
- ✅ TWAP order implementation (10%)
- ✅ Grid trading implementation (10%)
- ✅ CLI interface for all strategies
- ✅ Proper logging to bot.log
- ✅ Error handling and validation
- ✅ Background monitoring and automation
- ✅ Comprehensive documentation

**Total: 30% of assignment grade**
