"""Test Futures trading with correct parameters"""
from binance.client import Client
from binance.exceptions import BinanceAPIException
import time

# Replace with your Binance Futures Testnet API credentials
# Get keys from: https://testnet.binancefuture.com
API_KEY = "your_futures_testnet_api_key_here"
API_SECRET = "your_futures_testnet_api_secret_here"

print("=" * 70)
print("FUTURES TRADING TEST - CORRECT PARAMETERS")
print("=" * 70)

client = Client(API_KEY, API_SECRET, testnet=True)
client.API_URL = 'https://testnet.binancefuture.com'

print("\n1. Getting account balance...")
try:
    account = client.futures_account()
    usdt_balance = None
    for asset in account.get('assets', []):
        if asset['asset'] == 'USDT':
            usdt_balance = float(asset['availableBalance'])
            print(f"   ✓ USDT Balance: ${usdt_balance}")
            break
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n2. Getting current BTCUSDT price...")
try:
    ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
    current_price = float(ticker['price'])
    print(f"   ✓ Current Price: ${current_price}")
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n3. Getting symbol info for proper parameters...")
try:
    exchange_info = client.futures_exchange_info()
    btc_symbol = None
    for symbol in exchange_info['symbols']:
        if symbol['symbol'] == 'BTCUSDT':
            btc_symbol = symbol
            break
    
    # Get filters
    min_notional = None
    price_precision = None
    quantity_precision = None
    
    for filter in btc_symbol['filters']:
        if filter['filterType'] == 'MIN_NOTIONAL':
            min_notional = float(filter['notional'])
        elif filter['filterType'] == 'PRICE_FILTER':
            tick_size = float(filter['tickSize'])
        elif filter['filterType'] == 'LOT_SIZE':
            min_qty = float(filter['minQty'])
            step_size = float(filter['stepSize'])
    
    print(f"   ✓ Minimum Notional: ${min_notional}")
    print(f"   ✓ Minimum Quantity: {min_qty}")
    print(f"   ✓ Step Size: {step_size}")
    print(f"   ✓ Tick Size: {tick_size}")
    
    # Calculate proper quantity (minimum $100 notional + buffer)
    target_notional = 150  # $150 to be safe above $100 minimum
    quantity = target_notional / current_price
    # Round UP to step size to ensure we meet minimum
    import math
    quantity = math.ceil(quantity / step_size) * step_size
    quantity = round(quantity, 3)
    
    # Verify notional value
    notional = quantity * current_price
    if notional < min_notional:
        # If still below, increase quantity
        quantity = math.ceil(min_notional / current_price / step_size) * step_size + step_size
        quantity = round(quantity, 3)
        notional = quantity * current_price
    
    print(f"   ✓ Calculated Quantity: {quantity} BTC (notional: ${notional:.2f})")
    
except Exception as e:
    print(f"   ✗ Error: {e}")
    exit(1)

print("\n4. Placing MARKET BUY order...")
try:
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side='BUY',
        type='MARKET',
        quantity=quantity
    )
    print(f"   ✓ Order executed successfully!")
    print(f"   Order ID: {order.get('orderId')}")
    print(f"   Status: {order.get('status')}")
    print(f"   Executed Qty: {order.get('executedQty')} BTC")
    print(f"   Average Price: ${order.get('avgPrice')}")
    print(f"   Total Cost: ${float(order.get('cumQuote', 0)):.2f}")
    
    market_order_id = order.get('orderId')
    
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
    market_order_id = None
except Exception as e:
    print(f"   ✗ Error: {e}")
    market_order_id = None

print("\n5. Checking open positions...")
try:
    account = client.futures_account()
    print(f"   Open Positions:")
    has_positions = False
    for position in account.get('positions', []):
        position_amt = float(position.get('positionAmt', 0))
        if position_amt != 0:
            has_positions = True
            print(f"     - {position['symbol']}: {position_amt} BTC")
            print(f"       Entry Price: ${position.get('entryPrice')}")
            print(f"       Unrealized PnL: ${position.get('unrealizedProfit')}")
    
    if not has_positions:
        print(f"     No open positions")
        
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n6. Placing LIMIT SELL order to close position...")
try:
    # Round price to tick size
    limit_price = current_price * 1.02  # 2% above current (take profit)
    limit_price = round(limit_price / tick_size) * tick_size
    limit_price = round(limit_price, 2)
    
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side='SELL',
        type='LIMIT',
        timeInForce='GTC',
        quantity=quantity,
        price=limit_price
    )
    print(f"   ✓ Limit order placed successfully!")
    print(f"   Order ID: {order.get('orderId')}")
    print(f"   Status: {order.get('status')}")
    print(f"   Limit Price: ${limit_price}")
    print(f"   Quantity: {quantity} BTC")
    
    limit_order_id = order.get('orderId')
    
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
    limit_order_id = None
except Exception as e:
    print(f"   ✗ Error: {e}")
    limit_order_id = None

print("\n7. Checking open orders...")
try:
    open_orders = client.futures_get_open_orders(symbol='BTCUSDT')
    if open_orders:
        print(f"   Open Orders: {len(open_orders)}")
        for order in open_orders:
            print(f"     - Order ID: {order['orderId']}")
            print(f"       Type: {order['type']}, Side: {order['side']}")
            print(f"       Price: ${order.get('price')}, Qty: {order['origQty']}")
            print(f"       Status: {order['status']}")
    else:
        print(f"   No open orders")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n8. Cancelling limit order (if exists)...")
if limit_order_id:
    try:
        result = client.futures_cancel_order(symbol='BTCUSDT', orderId=limit_order_id)
        print(f"   ✓ Order cancelled successfully!")
        print(f"   Order ID: {result.get('orderId')}")
        print(f"   Status: {result.get('status')}")
    except Exception as e:
        print(f"   Note: {e}")

print("\n9. Closing position with MARKET order...")
if market_order_id:
    try:
        order = client.futures_create_order(
            symbol='BTCUSDT',
            side='SELL',
            type='MARKET',
            quantity=quantity
        )
        print(f"   ✓ Position closed successfully!")
        print(f"   Order ID: {order.get('orderId')}")
        print(f"   Status: {order.get('status')}")
        print(f"   Executed Qty: {order.get('executedQty')} BTC")
        print(f"   Average Price: ${order.get('avgPrice')}")
    except Exception as e:
        print(f"   Note: {e}")

print("\n10. Final account balance...")
try:
    account = client.futures_account()
    for asset in account.get('assets', []):
        if asset['asset'] == 'USDT':
            final_balance = float(asset['availableBalance'])
            print(f"   ✓ Final USDT Balance: ${final_balance}")
            print(f"   Change: ${final_balance - usdt_balance:.2f}")
            break
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("FUTURES TRADING TEST COMPLETED SUCCESSFULLY!")
print("=" * 70)
