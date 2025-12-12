"""
Step-by-step test script for all order types
"""
from binance.client import Client
from bot.basic_bot import BasicBot
from bot.advanced_orders import AdvancedOrderBot
from dotenv import load_dotenv
import os
import time

load_dotenv()

print("="*70)
print("COMPREHENSIVE TRADING BOT TEST")
print("="*70)

# Initialize client
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)
client.API_URL = 'https://testnet.binancefuture.com'

# Get current price
ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
current_price = float(ticker['price'])
print(f"\nCurrent BTC Price: ${current_price:,.2f}\n")

# Test 1: Market Order
print("="*70)
print("TEST 1: MARKET ORDER")
print("="*70)
bot = BasicBot(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)
result = bot.place_market_order('BTCUSDT', 'BUY', 0.001)
print(f"Result: {result}")
if result['success']:
    print("✅ Market Order PASSED")
else:
    print("❌ Market Order FAILED")
print()

# Test 2: Limit Order
print("="*70)
print("TEST 2: LIMIT ORDER")
print("="*70)
limit_price = current_price * 0.95
result = bot.place_limit_order('BTCUSDT', 'BUY', 0.001, limit_price)
print(f"Result: {result}")
if result['success']:
    print("✅ Limit Order PASSED")
    # Cancel it
    try:
        client.futures_cancel_order(symbol='BTCUSDT', orderId=result['order_id'])
        print("  (Order cancelled for cleanup)")
    except:
        pass
else:
    print("❌ Limit Order FAILED")
print()

# Test 3: Stop-Limit Order
print("="*70)
print("TEST 3: STOP-LIMIT ORDER")
print("="*70)
stop_price = current_price * 0.95
limit_price = current_price * 0.94
result = bot.place_stop_limit_order('BTCUSDT', 'SELL', 0.001, stop_price, limit_price)
print(f"Result: {result}")
if result['success']:
    print("✅ Stop-Limit Order PASSED")
    # Cancel it
    try:
        client.futures_cancel_order(symbol='BTCUSDT', orderId=result['order_id'])
        print("  (Order cancelled for cleanup)")
    except:
        pass
else:
    print("❌ Stop-Limit Order FAILED")
print()

# Test 4: OCO Order
print("="*70)
print("TEST 4: OCO (One-Cancels-the-Other) ORDER")
print("="*70)
advanced_bot = AdvancedOrderBot(client)
result = advanced_bot.place_oco_order(
    symbol='BTCUSDT',
    side='SELL',
    quantity=0.001,
    price=current_price * 1.05,
    stop_price=current_price * 0.95,
    stop_limit_price=current_price * 0.94
)
print(f"Result: {result}")
if result['success']:
    print("✅ OCO Order PASSED")
    print(f"  Take Profit Order: {result['take_profit_order']['order_id']}")
    print(f"  Stop Loss Order: {result['stop_loss_order']['order_id']}")
    # Cancel both
    time.sleep(2)
    try:
        client.futures_cancel_order(symbol='BTCUSDT', orderId=result['take_profit_order']['order_id'])
        client.futures_cancel_order(symbol='BTCUSDT', orderId=result['stop_loss_order']['order_id'])
        print("  (Orders cancelled for cleanup)")
    except:
        pass
else:
    print("❌ OCO Order FAILED")
print()

print("="*70)
print("BASIC TESTS COMPLETE")
print("="*70)
print("\n✅ All basic and OCO tests completed!")
print("Check bot.log for detailed execution logs.")
