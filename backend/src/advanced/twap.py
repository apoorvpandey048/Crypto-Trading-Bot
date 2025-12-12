"""
TWAP (Time-Weighted Average Price) Order CLI
Usage: python twap.py SYMBOL SIDE TOTAL_QUANTITY DURATION_MINUTES NUM_ORDERS
Example: python twap.py BTCUSDT BUY 0.01 30 10
"""

import sys
import os
import logging
from pathlib import Path
import time

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
    """Execute TWAP order from command line."""
    
    # Load environment variables
    load_dotenv()
    
    # Check arguments
    if len(sys.argv) < 6:
        print("❌ Error: Insufficient arguments")
        print("\nUsage: python twap.py SYMBOL SIDE TOTAL_QUANTITY DURATION_MINUTES NUM_ORDERS")
        print("\nExample:")
        print("  python twap.py BTCUSDT BUY 0.01 30 10")
        print("\nDescription:")
        print("  SYMBOL            - Trading pair (e.g., BTCUSDT)")
        print("  SIDE              - BUY or SELL")
        print("  TOTAL_QUANTITY    - Total quantity to trade")
        print("  DURATION_MINUTES  - Time period to spread orders over (minutes)")
        print("  NUM_ORDERS        - Number of smaller orders to split into")
        print("\nWhat is TWAP?")
        print("  TWAP splits a large order into smaller chunks executed at")
        print("  regular intervals to minimize market impact and get better")
        print("  average execution price.")
        sys.exit(1)
    
    # Parse arguments
    symbol = sys.argv[1].upper()
    side = sys.argv[2].upper()
    total_quantity = float(sys.argv[3])
    duration_minutes = int(sys.argv[4])
    num_orders = int(sys.argv[5])
    
    # Validate inputs
    if side not in ['BUY', 'SELL']:
        print(f"❌ Error: Invalid side '{side}'. Must be BUY or SELL")
        sys.exit(1)
    
    if total_quantity <= 0:
        print(f"❌ Error: Total quantity must be positive")
        sys.exit(1)
    
    if duration_minutes <= 0:
        print(f"❌ Error: Duration must be positive")
        sys.exit(1)
    
    if num_orders <= 0:
        print(f"❌ Error: Number of orders must be positive")
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
        print("TWAP (Time-Weighted Average Price) ORDER")
        print("=" * 70)
        print(f"Symbol: {symbol}")
        print(f"Side: {side}")
        print(f"Total Quantity: {total_quantity}")
        print(f"Duration: {duration_minutes} minutes")
        print(f"Number of Orders: {num_orders}")
        print(f"Order Quantity: {total_quantity / num_orders:.6f} per order")
        print(f"Interval: {(duration_minutes * 60) / num_orders:.2f} seconds between orders")
        print(f"Testnet: {testnet}")
        print("=" * 70)
        
        # Initialize client
        logger.info(f"Initializing Binance client (testnet={testnet})")
        client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            client.API_URL = 'https://testnet.binancefuture.com'
        
        # Initialize advanced bot
        bot = AdvancedOrderBot(client)
        
        # Place TWAP order
        print("\nInitiating TWAP strategy...")
        result = bot.place_twap_order(
            symbol=symbol,
            side=side,
            total_quantity=total_quantity,
            duration_minutes=duration_minutes,
            num_orders=num_orders
        )
        
        if result['success']:
            print("\n✅ TWAP Strategy Started Successfully!")
            print(f"\nTWAP ID: {result['twap_id']}")
            print(f"Total Quantity: {result['total_quantity']}")
            print(f"Order Quantity: {result['order_quantity']} per order")
            print(f"Number of Orders: {result['num_orders']}")
            print(f"Interval: {result['interval_seconds']:.2f} seconds")
            print(f"Estimated Completion: {result['estimated_completion']}")
            
            print("\n✓ Orders are being placed in the background...")
            print("\nMonitoring TWAP execution:")
            print("-" * 70)
            
            # Monitor progress
            twap_id = result['twap_id']
            total_orders = result['num_orders']
            
            try:
                while True:
                    time.sleep(5)
                    
                    status = bot.get_strategy_status(twap_id)
                    if status['success']:
                        strategy = status['strategy']
                        orders_placed = strategy.get('orders_placed', 0)
                        status_str = strategy.get('status', 'unknown')
                        
                        print(f"Progress: {orders_placed}/{total_orders} orders placed | Status: {status_str}")
                        
                        if status_str in ['completed', 'error', 'cancelled']:
                            break
                            
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped. TWAP will continue executing in the background.")
            
            print("\n✅ TWAP execution completed!")
            
            # Show final summary
            final_status = bot.get_strategy_status(twap_id)
            if final_status['success']:
                strategy = final_status['strategy']
                print(f"\nFinal Summary:")
                print(f"Orders Placed: {strategy.get('orders_placed', 0)}/{total_orders}")
                print(f"Status: {strategy.get('status', 'unknown')}")
                
        else:
            print(f"\n❌ TWAP Strategy Failed!")
            print(f"Error: {result.get('error', 'Unknown error')}")
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
