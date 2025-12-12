# Quick Test Guide for Advanced Orders

This guide provides simple commands to quickly test all advanced order types.

## ⚡ Quick Setup

```bash
# 1. Navigate to backend directory
cd backend

# 2. Ensure .env is configured
# BINANCE_API_KEY=your_key
# BINANCE_API_SECRET=your_secret
# BINANCE_TESTNET=True

# 3. Activate virtual environment (if using one)
# venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

## 🧪 Test Commands

### Test 1: OCO Order (2 minutes)
```bash
# Place OCO with current market price adjustments
python src/advanced/oco.py BTCUSDT SELL 0.001 95000 90000 89900
```

**What to expect**:
- Two orders placed (take-profit + stop-loss)
- Order IDs displayed
- Background monitoring starts
- Both orders visible in Binance testnet

**Success criteria**: ✅ Both orders appear in testnet, no errors

---

### Test 2: TWAP Order (5 minutes)
```bash
# Buy 0.003 BTC over 2 minutes in 3 chunks
python src/advanced/twap.py BTCUSDT BUY 0.003 2 3
```

**What to expect**:
- Strategy starts immediately
- First order executes right away
- Progress updates every 40 seconds
- Three total orders placed

**Success criteria**: ✅ All 3 orders execute at intervals, status shows "completed"

---

### Test 3: Grid Trading (2 minutes setup, runs indefinitely)
```bash
# Create 5-level grid with narrow range
python src/advanced/grid.py BTCUSDT 92000 93000 5 0.0005
```

**What to expect**:
- 5 orders placed instantly
- Mix of buy orders (below price) and sell orders (above price)
- Shows all order IDs and prices
- Runs in background monitoring mode
- Press Ctrl+C to stop monitoring

**Success criteria**: ✅ All 5 orders appear in testnet at different price levels

---

### Test 4: Automated Test Suite (3 minutes)
```bash
# Run all tests automatically
python test_advanced_orders.py
```

**What to expect**:
- Tests all three order types sequentially
- Small quantities to minimize risk
- Detailed output for each test
- Final summary with pass/fail

**Success criteria**: ✅ "ALL TESTS PASSED!" message

---

## 📋 Verification Steps

After running tests, verify in Binance Futures Testnet:

1. **Check Open Orders**:
   - Log into https://testnet.binancefuture.com
   - Go to "Orders" section
   - Should see placed orders

2. **Check bot.log**:
   ```bash
   # View last 50 lines of log
   Get-Content bot.log -Tail 50
   ```

3. **Check Order History**:
   - Orders may fill quickly on testnet
   - Check "Order History" for filled orders

---

## 🔍 Troubleshooting

### Error: "API credentials not found"
```bash
# Check .env file exists
ls .env

# Verify contents
Get-Content .env
```

### Error: "Insufficient balance"
- Visit Binance Futures Testnet
- Check USDT balance
- Request test funds if needed

### Error: "Invalid symbol"
```bash
# Use exact symbol format (no spaces, slash, or dash)
# Correct: BTCUSDT
# Wrong: BTC/USDT, BTC-USDT, BTC USDT
```

### Orders not appearing
- Refresh Binance testnet page
- Check if orders filled immediately (check Order History)
- Verify correct API keys are being used

---

## 📊 Expected bot.log Output

```
2025-01-15 10:23:45 - INFO - Placing OCO order for BTCUSDT
2025-01-15 10:23:46 - INFO - Take profit order placed: 12345678
2025-01-15 10:23:47 - INFO - Stop loss order placed: 12345679
2025-01-15 10:23:48 - INFO - OCO order placed successfully: OCO_1736934225
2025-01-15 10:25:30 - INFO - Placing TWAP order for BTCUSDT
2025-01-15 10:25:31 - INFO - TWAP order initiated: TWAP_1736934331
2025-01-15 10:25:32 - INFO - TWAP TWAP_1736934331: Order 1/3 placed - 87654321
2025-01-15 10:26:12 - INFO - TWAP TWAP_1736934331: Order 2/3 placed - 87654322
2025-01-15 10:26:52 - INFO - TWAP TWAP_1736934331: Order 3/3 placed - 87654323
2025-01-15 10:26:53 - INFO - TWAP TWAP_1736934331 completed: 3/3 orders placed
```

---

## 🎯 Success Indicators

For each test, you should see:
1. ✅ No error messages in console
2. ✅ Order IDs displayed
3. ✅ Success confirmation messages
4. ✅ Log entries in bot.log
5. ✅ Orders visible in Binance testnet

---

## 🚀 Next Steps

After successful testing:
1. Review bot.log for detailed execution traces
2. Check TRADING_TEST_RESULTS.md for more examples
3. Read backend/src/advanced/README.md for full documentation
4. Try different parameters (quantities, price ranges, durations)
5. Monitor orders in Binance testnet interface

---

## ⚠️ Important Notes

- **Always use testnet** for testing (BINANCE_TESTNET=True)
- **Small quantities** recommended for initial tests
- **Monitor orders** in Binance testnet interface
- **Check logs** if unexpected behavior occurs
- **Stop strategies** with Ctrl+C when testing

---

## 💡 Tips

1. **Start with smallest quantities** to understand behavior
2. **Watch the logs** in real-time: `Get-Content bot.log -Wait`
3. **Keep Binance testnet open** in browser to see orders
4. **Test one at a time** initially, then try automated suite
5. **Read error messages carefully** - they're designed to be helpful

---

## 📞 Need Help?

- Check ASSIGNMENT_SUMMARY.md for complete documentation
- Review backend/src/advanced/README.md for detailed usage
- Check TRADING_TEST_RESULTS.md for examples
- Examine bot.log for execution traces
