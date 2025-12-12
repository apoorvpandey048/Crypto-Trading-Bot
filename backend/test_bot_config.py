"""Test bot config creation"""
import requests

BASE_URL = "http://localhost:8001"

# Use the debug user we created earlier
print("1. Logging in...")
r = requests.post(f"{BASE_URL}/api/auth/login", data={
    "username": "debug_user@test.com",
    "password": "Debug123!"
})
print(f"   Status: {r.status_code}")
if r.status_code != 200:
    print(f"   Error: {r.text}")
    exit(1)

token = r.json()["access_token"]
headers = {"Authorization": f"Bearer {token}"}
print("   ✓ Logged in successfully")

# Get existing bot configs
print("\n2. Getting bot configs...")
r = requests.get(f"{BASE_URL}/api/bot-configs", headers=headers)
print(f"   Status: {r.status_code}")
if r.status_code == 200:
    configs = r.json()
    if configs:
        bot_config_id = configs[0]['id']
        print(f"   ✓ Using existing bot config (ID: {bot_config_id})")
    
    # Test getting account balance
    print("\n3. Testing account balance...")
    r = requests.get(f"{BASE_URL}/api/trading/balance?bot_config_id={bot_config_id}", headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text}")
    
    # Test market order
    print("\n4. Testing market order...")
    order = {
        "symbol": "BTCUSDT",
        "order_type": "MARKET",
        "side": "BUY",
        "quantity": 0.001,
        "bot_config_id": bot_config_id
    }
    r = requests.post(f"{BASE_URL}/api/trading/execute", json=order, headers=headers)
    print(f"   Status: {r.status_code}")
    print(f"   Response: {r.text}")
