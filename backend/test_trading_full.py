"""Test trading with full permissions"""
import requests

BASE_URL = "http://localhost:8001"
# Replace with your Binance Testnet API credentials
API_KEY = "your_testnet_api_key_here"
API_SECRET = "your_testnet_api_secret_here"

# Use the debug user we created earlier
print("=" * 70)
print("FULL TRADING TEST WITH ENABLED PERMISSIONS")
print("=" * 70)

print("\n1. Logging in...")
r = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "debug_user@test.com",
    "password": "Debug123!"
})
if r.status_code != 200:
    print(f"   ✗ Login failed: {r.text}")
    exit(1)

token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   ✓ Logged in successfully")

# Create a fresh bot config with the correct credentials
print("\n2. Creating NEW bot config with testnet credentials...")
import time
bot_config = {
    "name": f"Trading Test {int(time.time())}",
    "api_key": API_KEY,
    "api_secret": API_SECRET,
    "is_testnet": True,
    "is_active": True
}
r = requests.post(f"{BASE_URL}/api/bot-configs", json=bot_config, headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code != 201:
    print(f"   Error: {r.text}")
    # Try to use existing config
    r = requests.get(f"{BASE_URL}/api/bot-configs", headers=headers)
    if r.status_code == 200:
        configs = r.json()
        if configs:
            bot_config_id = configs[0]['id']
            print(f"   Using existing config (ID: {bot_config_id})")
else:
    config = r.json()
    bot_config_id = config['id']
    print(f"   ✓ Bot config created (ID: {bot_config_id})")

# Test account balance
print("\n3. Testing account balance (with trading permissions)...")
r = requests.get(f"{BASE_URL}/api/trading/balance?bot_config_id={bot_config_id}", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    balance = r.json()
    print(f"   ✓ Balance retrieved successfully")
    print(f"   Total Balance: ${balance.get('total_balance', 'N/A')}")
    print(f"   Available Balance: ${balance.get('available_balance', 'N/A')}")
    if 'assets' in balance and balance['assets']:
        print(f"   Assets:")
        for asset in balance['assets'][:5]:  # Show first 5 assets
            print(f"     - {asset['asset']}: {asset['free']} (locked: {asset['locked']})")
else:
    print(f"   ✗ Error: {r.text}")

# Test getting current price
print("\n4. Testing price fetch...")
r = requests.get(f"{BASE_URL}/api/trading/price/BTCUSDT", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    price_data = r.json()
    print(f"   ✓ BTCUSDT Price: ${price_data.get('price', 'N/A')}")
else:
    print(f"   ✗ Error: {r.text}")

# Test market order (small amount)
print("\n5. Testing MARKET order execution...")
order = {
    "symbol": "BTCUSDT",
    "order_type": "MARKET",
    "side": "BUY",
    "quantity": 0.001,  # Very small amount for testing
    "bot_config_id": bot_config_id
}
r = requests.post(f"{BASE_URL}/api/trading/execute", json=order, headers=headers)
print(f"   Status: {r.status_code}")
response = r.json()
print(f"   Response: {response}")
if r.status_code == 200 and response.get('success'):
    print(f"   ✓ Order executed successfully!")
    print(f"   Trade ID: {response.get('trade_id')}")
    print(f"   Order ID: {response.get('order_id')}")
else:
    print(f"   ✗ Order failed: {response.get('message', 'Unknown error')}")
    if 'error' in response:
        print(f"   Error details: {response['error']}")

# Test limit order
print("\n6. Testing LIMIT order execution...")
# Get current price first
r = requests.get(f"{BASE_URL}/api/trading/price/BTCUSDT", headers=headers)
if r.status_code == 200:
    current_price = float(r.json().get('price', 0))
    limit_price = current_price * 0.95  # 5% below current price
    
    order = {
        "symbol": "BTCUSDT",
        "order_type": "LIMIT",
        "side": "BUY",
        "quantity": 0.001,
        "price": limit_price,
        "bot_config_id": bot_config_id
    }
    r = requests.post(f"{BASE_URL}/api/trading/execute", json=order, headers=headers)
    print(f"   Status: {r.status_code}")
    response = r.json()
    if r.status_code == 200 and response.get('success'):
        print(f"   ✓ Limit order placed successfully!")
        print(f"   Trade ID: {response.get('trade_id')}")
        print(f"   Order ID: {response.get('order_id')}")
        print(f"   Limit Price: ${limit_price:.2f}")
    else:
        print(f"   ✗ Order failed: {response.get('message', 'Unknown error')}")
        if 'error' in response:
            print(f"   Error details: {response['error']}")

# Test trade history
print("\n7. Testing trade history...")
r = requests.get(f"{BASE_URL}/api/trading/trades", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    trades = r.json()
    print(f"   ✓ Total trades: {len(trades)}")
    if trades:
        print(f"   Recent trades:")
        for trade in trades[:3]:  # Show last 3 trades
            print(f"     - {trade['symbol']} {trade['side']} @ ${trade.get('price', 'N/A')}")
            print(f"       Status: {trade['status']}, Quantity: {trade['quantity']}")
else:
    print(f"   ✗ Error: {r.text}")

# Test trading stats
print("\n8. Testing trading stats...")
r = requests.get(f"{BASE_URL}/api/trading/stats", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    stats = r.json()
    print(f"   ✓ Trading Statistics:")
    print(f"   Total Trades: {stats.get('total_trades', 0)}")
    print(f"   Successful: {stats.get('successful_trades', 0)}")
    print(f"   Failed: {stats.get('failed_trades', 0)}")
    print(f"   Total Volume: ${stats.get('total_volume', 0):.2f}")
else:
    print(f"   ✗ Error: {r.text}")

print("\n" + "=" * 70)
print("FULL TRADING TEST COMPLETED")
print("=" * 70)
