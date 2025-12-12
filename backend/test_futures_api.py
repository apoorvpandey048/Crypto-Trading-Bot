"""Test Futures Testnet with new API keys"""
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Replace with your Binance Futures Testnet API credentials
# Get keys from: https://testnet.binancefuture.com
API_KEY = "your_futures_testnet_api_key_here"
API_SECRET = "your_futures_testnet_api_secret_here"

print("=" * 70)
print("BINANCE FUTURES TESTNET CONNECTION TEST")
print("=" * 70)

print("\n1. Testing Futures Testnet Connection...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com'
    
    # Try to get futures account info
    account = client.futures_account()
    print(f"   ✓ Connected successfully to FUTURES Testnet!")
    print(f"   Total Wallet Balance: ${account.get('totalWalletBalance', 'N/A')}")
    print(f"   Total Unrealized Profit: ${account.get('totalUnrealizedProfit', 'N/A')}")
    print(f"   Available Balance: ${account.get('availableBalance', 'N/A')}")
    print(f"   Max Withdraw Amount: ${account.get('maxWithdrawAmount', 'N/A')}")
    
    print(f"\n   Assets:")
    for asset in account.get('assets', []):
        wallet_balance = float(asset.get('walletBalance', 0))
        if wallet_balance > 0:
            print(f"     - {asset['asset']}: {wallet_balance} (available: {asset.get('availableBalance', 'N/A')})")
    
    print(f"\n   Positions:")
    for position in account.get('positions', []):
        position_amt = float(position.get('positionAmt', 0))
        if position_amt != 0:
            print(f"     - {position['symbol']}: {position_amt} (unrealized PnL: ${position.get('unrealizedProfit', 'N/A')})")
    
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n2. Testing Price Fetch...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com'
    
    # Get current price
    ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
    print(f"   ✓ BTCUSDT Price: ${ticker['price']}")
    
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n3. Testing Order Placement (Market Order - VERY SMALL AMOUNT)...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com'
    
    # Place a very small market order
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side='BUY',
        type='MARKET',
        quantity=0.001  # Very small amount
    )
    print(f"   ✓ Order placed successfully!")
    print(f"   Order ID: {order.get('orderId')}")
    print(f"   Symbol: {order.get('symbol')}")
    print(f"   Status: {order.get('status')}")
    print(f"   Executed Qty: {order.get('executedQty')}")
    print(f"   Cum Quote: ${order.get('cumQuote')}")
    
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n4. Testing Limit Order...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com'
    
    # Get current price
    ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
    current_price = float(ticker['price'])
    limit_price = round(current_price * 0.95, 2)  # 5% below current price
    
    # Place limit order
    order = client.futures_create_order(
        symbol='BTCUSDT',
        side='BUY',
        type='LIMIT',
        timeInForce='GTC',
        quantity=0.001,
        price=limit_price
    )
    print(f"   ✓ Limit order placed successfully!")
    print(f"   Order ID: {order.get('orderId')}")
    print(f"   Symbol: {order.get('symbol')}")
    print(f"   Status: {order.get('status')}")
    print(f"   Limit Price: ${limit_price}")
    
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
except Exception as e:
    print(f"   ✗ Error: {e}")

print("\n" + "=" * 70)
print("FUTURES TESTNET TEST COMPLETED")
print("=" * 70)
