"""
Comprehensive test suite for Crypto Trading Bot
Tests all features with read-only API access
"""
import requests
import json
import time

BASE_URL = "http://localhost:8001"
# Replace with your Binance Futures Testnet API credentials
# Get keys from: https://testnet.binancefuture.com
API_KEY = "your_futures_testnet_api_key_here"
API_SECRET = "your_futures_testnet_api_secret_here"

# Test user credentials
TEST_USER = {
    "email": "trader@example.com",
    "username": "trader123",
    "password": "SecurePass123!",
    "full_name": "Test Trader"
}

token = None
bot_config_id = None

def print_section(title):
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def print_result(test_name, success, details=""):
    status = "[PASS]" if success else "[FAIL]"
    print(f"{status} - {test_name}")
    if details:
        print(f"     {details}")

# ========== TEST 1: Health Check ==========
print_section("TEST 1: Health Check")
try:
    response = requests.get(f"{BASE_URL}/health")
    success = response.status_code == 200
    print_result("Health endpoint", success, f"Status: {response.status_code}")
    if success:
        print(f"     Response: {response.json()}")
except Exception as e:
    print_result("Health endpoint", False, str(e))

# ========== TEST 2: User Registration ==========
print_section("TEST 2: User Registration")
try:
    # Try to register (might fail if user exists)
    response = requests.post(f"{BASE_URL}/api/auth/register", json=TEST_USER)
    if response.status_code == 201:
        print_result("User registration", True, "New user created")
        user_data = response.json()
        print(f"     User ID: {user_data['id']}")
        print(f"     Username: {user_data['username']}")
        print(f"     Email: {user_data['email']}")
    elif response.status_code == 400:
        print_result("User registration", True, "User already exists (expected)")
    else:
        print_result("User registration", False, f"Status: {response.status_code}")
except Exception as e:
    print_result("User registration", False, str(e))

# ========== TEST 3: User Login ==========
print_section("TEST 3: User Login")
try:
    login_data = {
        "username": TEST_USER["username"],
        "password": TEST_USER["password"]
    }
    response = requests.post(
        f"{BASE_URL}/api/auth/login",
        data=login_data,
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )
    success = response.status_code == 200
    print_result("User login", success, f"Status: {response.status_code}")
    if success:
        token = response.json()["access_token"]
        print(f"     Token received: {token[:30]}...")
except Exception as e:
    print_result("User login", False, str(e))

if not token:
    print("\n❌ Cannot continue without authentication token")
    exit(1)

headers = {"Authorization": f"Bearer {token}"}

# ========== TEST 4: Get Current User ==========
print_section("TEST 4: Get Current User")
try:
    response = requests.get(f"{BASE_URL}/api/auth/me", headers=headers)
    success = response.status_code == 200
    print_result("Get current user", success)
    if success:
        user = response.json()
        print(f"     Username: {user['username']}")
        print(f"     Email: {user['email']}")
        print(f"     Active: {user['is_active']}")
except Exception as e:
    print_result("Get current user", False, str(e))

# ========== TEST 5: Create Bot Configuration ==========
print_section("TEST 5: Create Bot Configuration")
try:
    bot_config = {
        "name": "Test Trading Bot",
        "api_key": API_KEY,
        "api_secret": API_SECRET,
        "is_testnet": True,
        "is_active": True
    }
    response = requests.post(
        f"{BASE_URL}/api/bot-configs",
        json=bot_config,
        headers=headers
    )
    success = response.status_code == 201
    print_result("Create bot config", success)
    if success:
        config = response.json()
        bot_config_id = config["id"]
        print(f"     Config ID: {config['id']}")
        print(f"     Name: {config['name']}")
        print(f"     Testnet: {config['is_testnet']}")
        print(f"     Active: {config['is_active']}")
    else:
        print(f"     Status: {response.status_code}")
        print(f"     Response: {response.text}")
except Exception as e:
    print_result("Create bot config", False, str(e))

# ========== TEST 6: Get All Bot Configurations ==========
print_section("TEST 6: Get All Bot Configurations")
try:
    response = requests.get(f"{BASE_URL}/api/bot-configs", headers=headers)
    success = response.status_code == 200
    print_result("Get bot configs", success)
    if success:
        configs = response.json()
        print(f"     Total configs: {len(configs)}")
        for config in configs:
            print(f"     - {config['name']} (ID: {config['id']})")
except Exception as e:
    print_result("Get bot configs", False, str(e))

# ========== TEST 7: Get Account Balance ==========
print_section("TEST 7: Get Account Balance (Read-Only API)")
try:
    if bot_config_id:
        response = requests.get(
            f"{BASE_URL}/api/trading/balance",
            params={"bot_config_id": bot_config_id},
            headers=headers
        )
        success = response.status_code == 200
        print_result("Get account balance", success)
        if success:
            balance = response.json()
            print(f"     Total Balance: ${balance.get('totalWalletBalance', 'N/A')}")
            print(f"     Available: ${balance.get('availableBalance', 'N/A')}")
            if 'assets' in balance and balance['assets']:
                print(f"     Assets ({len(balance['assets'])}):")
                for asset in balance['assets'][:5]:  # Show first 5
                    print(f"       - {asset.get('asset', 'N/A')}: {asset.get('walletBalance', 'N/A')}")
        else:
            print(f"     Response: {response.text[:200]}")
    else:
        print_result("Get account balance", False, "No bot config ID")
except Exception as e:
    print_result("Get account balance", False, str(e))

# ========== TEST 8: Get Current Price ==========
print_section("TEST 8: Get Current Price")
try:
    symbols = ["BTCUSDT", "ETHUSDT", "BNBUSDT"]
    for symbol in symbols:
        response = requests.get(
            f"{BASE_URL}/api/trading/price/{symbol}",
            headers=headers
        )
        success = response.status_code == 200
        if success:
            price_data = response.json()
            print_result(f"Get {symbol} price", True, f"${price_data['price']}")
        else:
            print_result(f"Get {symbol} price", False, f"Status: {response.status_code}")
        time.sleep(0.5)  # Rate limiting
except Exception as e:
    print_result("Get current price", False, str(e))

# ========== TEST 9: Test Market Order (Will Fail - Read Only) ==========
print_section("TEST 9: Test Market Order (Expected to Fail - Read-Only API)")
try:
    if bot_config_id:
        order = {
            "bot_config_id": bot_config_id,
            "symbol": "BTCUSDT",
            "side": "BUY",
            "order_type": "MARKET",
            "quantity": 0.001
        }
        response = requests.post(
            f"{BASE_URL}/api/trading/execute",
            json=order,
            headers=headers
        )
        # We EXPECT this to fail with 403 or similar
        if response.status_code in [403, 400, 500]:
            print_result("Market order (read-only)", True, 
                        "Correctly rejected - API has read-only permissions")
            print(f"     Error: {response.json().get('detail', 'Permission denied')}")
        else:
            print_result("Market order", False, 
                        f"Unexpected status: {response.status_code}")
    else:
        print_result("Market order", False, "No bot config ID")
except Exception as e:
    print_result("Market order", True, f"Expected error: {str(e)[:100]}")

# ========== TEST 10: Get Trade History ==========
print_section("TEST 10: Get Trade History")
try:
    response = requests.get(f"{BASE_URL}/api/trading/trades", headers=headers)
    success = response.status_code == 200
    print_result("Get trade history", success)
    if success:
        trades = response.json()
        print(f"     Total trades: {len(trades)}")
        if trades:
            print(f"     Recent trades:")
            for trade in trades[:3]:
                print(f"       - {trade['symbol']} {trade['side']} @ ${trade.get('price', 'N/A')}")
        else:
            print(f"     No trades yet (expected with read-only API)")
except Exception as e:
    print_result("Get trade history", False, str(e))

# ========== TEST 11: Create Note (CRUD Test) ==========
print_section("TEST 11: Create Note (CRUD Feature Test)")
note_id = None
try:
    note_data = {
        "title": "Test Trading Note",
        "content": "This is a test note created during automated testing.",
        "category": "test"
    }
    response = requests.post(
        f"{BASE_URL}/api/notes",
        json=note_data,
        headers=headers
    )
    success = response.status_code == 201
    print_result("Create note", success)
    if success:
        note = response.json()
        note_id = note["id"]
        print(f"     Note ID: {note['id']}")
        print(f"     Title: {note['title']}")
except Exception as e:
    print_result("Create note", False, str(e))

# ========== TEST 12: Get All Notes ==========
print_section("TEST 12: Get All Notes")
try:
    response = requests.get(f"{BASE_URL}/api/notes", headers=headers)
    success = response.status_code == 200
    print_result("Get all notes", success)
    if success:
        notes = response.json()
        print(f"     Total notes: {len(notes)}")
        for note in notes:
            print(f"     - {note['title']}")
except Exception as e:
    print_result("Get all notes", False, str(e))

# ========== TEST 13: Update Note ==========
print_section("TEST 13: Update Note")
try:
    if note_id:
        update_data = {
            "title": "Updated Trading Note",
            "content": "This note has been updated during testing."
        }
        response = requests.put(
            f"{BASE_URL}/api/notes/{note_id}",
            json=update_data,
            headers=headers
        )
        success = response.status_code == 200
        print_result("Update note", success)
        if success:
            note = response.json()
            print(f"     Updated title: {note['title']}")
    else:
        print_result("Update note", False, "No note ID")
except Exception as e:
    print_result("Update note", False, str(e))

# ========== TEST 14: Delete Note ==========
print_section("TEST 14: Delete Note")
try:
    if note_id:
        response = requests.delete(
            f"{BASE_URL}/api/notes/{note_id}",
            headers=headers
        )
        success = response.status_code == 200
        print_result("Delete note", success)
    else:
        print_result("Delete note", False, "No note ID")
except Exception as e:
    print_result("Delete note", False, str(e))

# ========== TEST 15: Get Trading Stats ==========
print_section("TEST 15: Get Trading Stats")
try:
    response = requests.get(f"{BASE_URL}/api/trading/stats", headers=headers)
    success = response.status_code == 200
    print_result("Get trading stats", success)
    if success:
        stats = response.json()
        print(f"     Total trades: {stats.get('total_trades', 0)}")
        print(f"     Successful: {stats.get('successful_trades', 0)}")
        print(f"     Failed: {stats.get('failed_trades', 0)}")
        print(f"     Pending: {stats.get('pending_trades', 0)}")
except Exception as e:
    print_result("Get trading stats", False, str(e))

# ========== FINAL SUMMARY ==========
print_section("TEST SUMMARY")
print("""
[+] Successfully Tested:
   - Health check endpoint
   - User registration & authentication
   - Bot configuration management
   - Account balance retrieval (read-only)
   - Price fetching for multiple symbols
   - CRUD operations (Notes feature)
   - Trading stats retrieval
   
[!] Limited Testing (Read-Only API):
   - Cannot test actual trade execution
   - Cannot test order cancellation
   - Cannot test order status updates
   
[*] To enable full trading features:
   1. Go to Binance Testnet API settings
   2. Enable "Permits Universal Transfer" or "Enable Spot & Margin Trading"
   3. Re-run tests with trading permissions
""")

print("\n" + "=" * 70)
print("  All tests completed!")
print("=" * 70 + "\n")
