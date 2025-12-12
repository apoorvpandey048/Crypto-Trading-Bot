"""Test direct Binance API connection"""
from binance.client import Client
from binance.exceptions import BinanceAPIException

# Replace with your Binance Testnet API credentials
API_KEY = "your_testnet_api_key_here"
API_SECRET = "your_testnet_api_secret_here"

print("=" * 70)
print("BINANCE API CONNECTION TEST")
print("=" * 70)

# Test 1: Spot Testnet
print("\n1. Testing SPOT Testnet (testnet.binance.vision)...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    
    # Try to get account info
    account = client.get_account()
    print(f"   ✓ Connected successfully to SPOT Testnet!")
    print(f"   Can Trade: {account['canTrade']}")
    print(f"   Can Withdraw: {account['canWithdraw']}")
    print(f"   Can Deposit: {account['canDeposit']}")
    print(f"   Balances with assets:")
    for balance in account['balances']:
        if float(balance['free']) > 0 or float(balance['locked']) > 0:
            print(f"     - {balance['asset']}: {balance['free']} (locked: {balance['locked']})")
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 2: Futures Testnet
print("\n2. Testing FUTURES Testnet (testnet.binancefuture.com)...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    client.API_URL = 'https://testnet.binancefuture.com'
    
    # Try to get futures account info
    account = client.futures_account()
    print(f"   ✓ Connected successfully to FUTURES Testnet!")
    print(f"   Total Wallet Balance: {account.get('totalWalletBalance', 'N/A')}")
    print(f"   Available Balance: {account.get('availableBalance', 'N/A')}")
    print(f"   Assets:")
    for asset in account.get('assets', []):
        if float(asset.get('walletBalance', 0)) > 0:
            print(f"     - {asset['asset']}: {asset['walletBalance']} (available: {asset.get('availableBalance', 'N/A')})")
except BinanceAPIException as e:
    print(f"   ✗ Binance API Error: {e}")
    print(f"   Error Code: {e.code}")
    print(f"   Error Message: {e.message}")
except Exception as e:
    print(f"   ✗ Error: {e}")

# Test 3: Check API key permissions
print("\n3. Checking API key status...")
try:
    client = Client(API_KEY, API_SECRET, testnet=True)
    status = client.get_account_api_trading_status()
    print(f"   ✓ API Status retrieved:")
    print(f"   Status: {status}")
except Exception as e:
    print(f"   Note: {e}")

print("\n" + "=" * 70)
print("CONNECTION TEST COMPLETED")
print("=" * 70)
