"""
OCO (One-Cancels-the-Other) Order CLI
Usage: python oco.py SYMBOL SIDE QUANTITY TAKE_PROFIT_PRICE STOP_PRICE STOP_LIMIT_PRICE
Example: python oco.py BTCUSDT SELL 0.002 95000 90000 89900
"""

import sys
import os
import logging
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from binance.client import Client
from bot.advanced_orders import AdvancedOrderBot
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


def main():
    """Execute OCO order from command line."""
    
    # Load environment variables
    load_dotenv()
    
    # Check arguments
    if len(sys.argv) < 7:
        print("❌ Error: Insufficient arguments")
        print("\nUsage: python oco.py SYMBOL SIDE QUANTITY TAKE_PROFIT_PRICE STOP_PRICE STOP_LIMIT_PRICE")
        print("\nExample:")
        print("  python oco.py BTCUSDT SELL 0.002 95000 90000 89900")
        print("\nDescription:")
        print("  SYMBOL              - Trading pair (e.g., BTCUSDT)")
        print("  SIDE                - BUY or SELL")
        print("  QUANTITY            - Order quantity")
        print("  TAKE_PROFIT_PRICE   - Limit order price (take profit)")
        print("  STOP_PRICE          - Stop price (stop loss trigger)")
        print("  STOP_LIMIT_PRICE    - Stop limit price (stop loss execution)")
        sys.exit(1)
    
    # Parse arguments
    symbol = sys.argv[1].upper()
    side = sys.argv[2].upper()
    quantity = float(sys.argv[3])
    take_profit_price = float(sys.argv[4])
    stop_price = float(sys.argv[5])
    stop_limit_price = float(sys.argv[6])
    
    # Validate inputs
    if side not in ['BUY', 'SELL']:
        print(f"❌ Error: Invalid side '{side}'. Must be BUY or SELL")
        sys.exit(1)
    
    if quantity <= 0:
        print(f"❌ Error: Quantity must be positive")
        sys.exit(1)
    
    # Get API credentials
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    testnet = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    if not api_key or not api_secret:
        print("❌ Error: API credentials not found in .env file")
        print("Please set BINANCE_API_KEY and BINANCE_API_SECRET")
        sys.exit(1)
    
    try:
        print("=" * 70)
        print("OCO (One-Cancels-the-Other) ORDER")
        print("=" * 70)
        print(f"Symbol: {symbol}")
        print(f"Side: {side}")
        print(f"Quantity: {quantity}")
        print(f"Take Profit Price: ${take_profit_price}")
        print(f"Stop Price: ${stop_price}")
        print(f"Stop Limit Price: ${stop_limit_price}")
        print(f"Testnet: {testnet}")
        print("=" * 70)
        
        # Initialize client
        logger.info(f"Initializing Binance client (testnet={testnet})")
        client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            client.API_URL = 'https://testnet.binancefuture.com'
        
        # Initialize advanced bot
        bot = AdvancedOrderBot(client)
        
        # Place OCO order
        print("\nPlacing OCO order...")
        result = bot.place_oco_order(
            symbol=symbol,
            side=side,
            quantity=quantity,
            price=take_profit_price,
            stop_price=stop_price,
            stop_limit_price=stop_limit_price
        )
        
        if result['success']:
            print("\n✅ OCO Order Placed Successfully!")
            print(f"\nOCO ID: {result['oco_id']}")
            print(f"\nTake Profit Order:")
            print(f"  Order ID: {result['take_profit_order']['order_id']}")
            print(f"  Price: ${result['take_profit_order']['price']}")
            print(f"  Status: {result['take_profit_order']['status']}")
            print(f"\nStop Loss Order:")
            print(f"  Order ID: {result['stop_loss_order']['order_id']}")
            print(f"  Stop Price: ${result['stop_loss_order']['stop_price']}")
            print(f"  Limit Price: ${result['stop_loss_order']['limit_price']}")
            print(f"  Status: {result['stop_loss_order']['status']}")
            print("\n✓ Monitoring orders in background...")
            print("✓ When one order is filled, the other will be automatically cancelled")
            
            # Keep script running to monitor orders
            print("\nPress Ctrl+C to stop monitoring and exit")
            try:
                import time
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped. Orders will continue to be monitored by the system.")
        else:
            print(f"\n❌ OCO Order Failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
            if 'error_code' in result:
                print(f"Error Code: {result['error_code']}")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        print(f"\n❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
