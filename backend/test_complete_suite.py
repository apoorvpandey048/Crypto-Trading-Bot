"""
Complete test suite with all order types including TWAP and Grid
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
print("COMPLETE TEST SUITE - ALL ORDER TYPES")
print("="*70)

# Initialize
client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)
client.API_URL = 'https://testnet.binancefuture.com'

# Get current price
ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
current_price = float(ticker['price'])
print(f"\nCurrent BTC Price: ${current_price:,.2f}\n")

# Get symbol info for precision
exchange_info = client.futures_exchange_info()
symbol_info = next(s for s in exchange_info['symbols'] if s['symbol'] == 'BTCUSDT')
price_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'PRICE_FILTER')
tick_size = float(price_filter['tickSize'])
lot_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'LOT_SIZE')
step_size = float(lot_filter['stepSize'])
min_notional_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'MIN_NOTIONAL')
min_notional = float(min_notional_filter['notional'])

quantity = math.ceil((min_notional * 1.5 / current_price) / step_size) * step_size

def round_price(price, tick_size):
    return math.floor(price / tick_size) * tick_size

# Test Results Tracker
results = []

# Test 1: OCO with proper position
print("="*70)
print("TEST 1: OCO (One-Cancels-the-Other) ORDER")
print("="*70)
print("First, opening a position...")

bot = BasicBot(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)
# Buy position first
position_result = bot.place_market_order('BTCUSDT', 'BUY', quantity)
if position_result['success']:
    print(f"✅ Position opened: Order ID {position_result['order_id']}")
    time.sleep(2)
    
    # Now place OCO to close the position
    advanced_bot = AdvancedOrderBot(client)
    tp_price = round_price(current_price * 1.05, tick_size)
    stop_price = round_price(current_price * 0.95, tick_size)
    stop_limit_price = round_price(current_price * 0.94, tick_size)
    
    print(f"Placing OCO: TP=${tp_price:,.2f}, Stop=${stop_price:,.2f}, SL=${stop_limit_price:,.2f}")
    
    result = advanced_bot.place_oco_order(
        symbol='BTCUSDT',
        side='SELL',
        quantity=quantity,
        price=tp_price,
        stop_price=stop_price,
        stop_limit_price=stop_limit_price
    )
    
    if result['success']:
        print(f"✅ OCO Order PASSED")
        print(f"  Take Profit: {result['take_profit_order']['order_id']}")
        print(f"  Stop Loss: {result['stop_loss_order']['order_id']}")
        results.append(("OCO Order", "PASSED", result['oco_id']))
        
        # Cancel for cleanup
        time.sleep(2)
        try:
            client.futures_cancel_order(symbol='BTCUSDT', orderId=result['take_profit_order']['order_id'])
            client.futures_cancel_order(symbol='BTCUSDT', orderId=result['stop_loss_order']['order_id'])
            print("  (OCO orders cancelled)")
        except:
            pass
    else:
        print(f"❌ OCO Failed: {result.get('error')}")
        results.append(("OCO Order", "FAILED", result.get('error')))
else:
    print(f"❌ Could not open position for OCO test")
    results.append(("OCO Order", "SKIPPED", "No position"))

print()
time.sleep(2)

# Test 2: TWAP
print("="*70)
print("TEST 2: TWAP (Time-Weighted Average Price)")
print("="*70)
print("Executing TWAP: 0.003 BTC over 1 minute in 3 orders")

advanced_bot = AdvancedOrderBot(client)
result = advanced_bot.place_twap_order(
    symbol='BTCUSDT',
    side='BUY',
    total_quantity=0.003,
    duration_minutes=1,
    num_orders=3
)

if result['success']:
    print(f"✅ TWAP Started - ID: {result['twap_id']}")
    print(f"  Will place 3 orders, ~20 seconds apart")
    results.append(("TWAP Order", "STARTED", result['twap_id']))
    
    # Monitor for 70 seconds
    for i in range(7):
        time.sleep(10)
        status = advanced_bot.get_strategy_status(result['twap_id'])
        if status['success']:
            orders_placed = status['strategy'].get('orders_placed', 0)
            print(f"  Progress: {orders_placed}/3 orders placed")
            if status['strategy'].get('status') == 'completed':
                print("✅ TWAP Completed!")
                results.append(("TWAP Execution", "PASSED", f"{orders_placed}/3 orders"))
                break
else:
    print(f"❌ TWAP Failed: {result.get('error')}")
    results.append(("TWAP Order", "FAILED", result.get('error')))

print()
time.sleep(2)

# Test 3: Grid Trading
print("="*70)
print("TEST 3: GRID TRADING")
print("="*70)

lower_price = round_price(current_price * 0.98, tick_size)
upper_price = round_price(current_price * 1.02, tick_size)
print(f"Creating 5-level grid: ${lower_price:,.2f} - ${upper_price:,.2f}")

result = advanced_bot.start_grid_trading(
    symbol='BTCUSDT',
    lower_price=lower_price,
    upper_price=upper_price,
    num_grids=5,
    quantity_per_grid=0.001
)

if result['success']:
    print(f"✅ Grid Trading Started - ID: {result['grid_id']}")
    print(f"  {len(result['orders'])} orders placed:")
    for order in result['orders']:
        print(f"    {order['side']:4} @ ${order['price']:>10.2f} | ID: {order['order_id']}")
    results.append(("Grid Trading", "PASSED", f"{len(result['orders'])} orders"))
    
    # Monitor briefly
    print("\n  Monitoring for 10 seconds...")
    time.sleep(10)
    
    # Stop grid
    stop_result = advanced_bot.stop_grid_trading(result['grid_id'])
    if stop_result['success']:
        print(f"  Grid stopped - {stop_result['orders_cancelled']} orders cancelled")
else:
    print(f"❌ Grid Failed: {result.get('error')}")
    results.append(("Grid Trading", "FAILED", result.get('error')))

print()

# Final Summary
print("="*70)
print("TEST RESULTS SUMMARY")
print("="*70)
for test_name, status, details in results:
    status_icon = "✅" if status == "PASSED" or status == "STARTED" else "❌"
    print(f"{status_icon} {test_name:25} {status:10} {details}")

print("\n" + "="*70)
passed = sum(1 for _, status, _ in results if status in ["PASSED", "STARTED"])
total = len(results)
print(f"TOTAL: {passed}/{total} tests passed")
print("="*70)
print("\n✅ Check bot.log for detailed execution logs")
