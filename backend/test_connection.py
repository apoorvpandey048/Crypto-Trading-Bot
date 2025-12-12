"""Quick API connection test"""
from binance.client import Client
import os
from dotenv import load_dotenv

load_dotenv()

client = Client(os.getenv('BINANCE_API_KEY'), os.getenv('BINANCE_API_SECRET'), testnet=True)
client.API_URL = 'https://testnet.binancefuture.com'

# Test connection
ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
balance = client.futures_account_balance()
usdt = [b for b in balance if b['asset'] == 'USDT'][0]

print("=" * 70)
print("✅ API CONNECTION SUCCESSFUL!")
print("=" * 70)
print(f"Current BTC Price: ${float(ticker['price']):,.2f}")
print(f"USDT Balance: ${float(usdt['balance']):,.2f}")
print("=" * 70)
print("\n✅ Ready to run tests!")
