"""
Fixed test with proper quantities and price precision
"""
from binance.client import Client
from bot.basic_bot import BasicBot
from bot.advanced_orders import AdvancedOrderBot
from dotenv import load_dotenv
import os
import time
import math

load_dotenv()

print("="*70)
print("COMPREHENSIVE TRADING BOT TEST - FIXED")
print("="*70)

# Initialize client
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)
client.API_URL = 'https://testnet.binancefuture.com'

# Get current price and symbol info
ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
current_price = float(ticker['price'])
print(f"\nCurrent BTC Price: ${current_price:,.2f}")

# Get symbol precision
exchange_info = client.futures_exchange_info()
symbol_info = next(s for s in exchange_info['symbols'] if s['symbol'] == 'BTCUSDT')

# Get price filter
price_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'PRICE_FILTER')
tick_size = float(price_filter['tickSize'])

# Get lot size filter
lot_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
min_qty = float(lot_filter['minQty'])
step_size = float(lot_filter['stepSize'])

# Get min notional
min_notional_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'MIN_NOTIONAL')
min_notional = float(min_notional_filter['notional'])

print(f"Min Notional: ${min_notional}")
print(f"Tick Size: {tick_size}")
print(f"Min Quantity: {min_qty}")
print(f"Step Size: {step_size}\n")

# Calculate proper quantity (above min notional)
quantity = math.ceil((min_notional * 1.5 / current_price) / step_size) * step_size
print(f"Using Quantity: {quantity} BTC")
print(f"Notional Value: ${quantity * current_price:,.2f}\n")

def round_price(price, tick_size):
    """Round price to tick size"""
    return math.floor(price / tick_size) * tick_size

# Initialize bot
bot = BasicBot(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)

# Test 1: Market Order
print("="*70)
print("TEST 1: MARKET ORDER")
print("="*70)
result = bot.place_market_order('BTCUSDT', 'BUY', quantity)
print(f"Result: {result}")
if result['success']:
    print(f"✅ Market Order PASSED - Order ID: {result['order_id']}")
else:
    print(f"❌ Market Order FAILED - {result.get('error')}")
print()

time.sleep(1)

# Test 2: Limit Order
print("="*70)
print("TEST 2: LIMIT ORDER")
print("="*70)
limit_price = round_price(current_price * 0.95, tick_size)
print(f"Limit Price: ${limit_price:,.2f}")
result = bot.place_limit_order('BTCUSDT', 'BUY', quantity, limit_price)
print(f"Result: {result}")
if result['success']:
    print(f"✅ Limit Order PASSED - Order ID: {result['order_id']}")
    # Cancel it
    try:
        client.futures_cancel_order(symbol='BTCUSDT', orderId=result['order_id'])
        print("  (Order cancelled for cleanup)")
    except:
        pass
else:
    print(f"❌ Limit Order FAILED - {result.get('error')}")
print()

time.sleep(1)

# Test 3: Stop-Limit Order
print("="*70)
print("TEST 3: STOP-LIMIT ORDER")
print("="*70)
stop_price = round_price(current_price * 0.95, tick_size)
limit_price = round_price(current_price * 0.94, tick_size)
print(f"Stop Price: ${stop_price:,.2f}, Limit Price: ${limit_price:,.2f}")
result = bot.place_stop_limit_order('BTCUSDT', 'SELL', quantity, stop_price, limit_price)
print(f"Result: {result}")
if result['success']:
    print(f"✅ Stop-Limit Order PASSED - Order ID: {result['order_id']}")
    # Cancel it
    try:
        client.futures_cancel_order(symbol='BTCUSDT', orderId=result['order_id'])
        print("  (Order cancelled for cleanup)")
    except:
        pass
else:
    print(f"❌ Stop-Limit Order FAILED - {result.get('error')}")
print()

time.sleep(1)

# Test 4: OCO Order
print("="*70)
print("TEST 4: OCO (One-Cancels-the-Other) ORDER")
print("="*70)
advanced_bot = AdvancedOrderBot(client)
tp_price = round_price(current_price * 1.05, tick_size)
stop_price = round_price(current_price * 0.95, tick_size)
stop_limit_price = round_price(current_price * 0.94, tick_size)
print(f"TP: ${tp_price:,.2f}, Stop: ${stop_price:,.2f}, Stop Limit: ${stop_limit_price:,.2f}")

result = advanced_bot.place_oco_order(
    symbol='BTCUSDT',
    side='SELL',
    quantity=quantity,
    price=tp_price,
    stop_price=stop_price,
    stop_limit_price=stop_limit_price
)
print(f"Result: {result}")
if result['success']:
    print(f"✅ OCO Order PASSED")
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
    print(f"❌ OCO Order FAILED - {result.get('error')}")
print()

print("="*70)
print("ALL BASIC TESTS COMPLETE!")
print("="*70)
print("\n✅ Check bot.log and trading_bot.log for detailed execution logs.")
