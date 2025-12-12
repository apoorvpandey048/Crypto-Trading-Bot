"""
Grid Trading Strategy CLI
Usage: python grid.py SYMBOL LOWER_PRICE UPPER_PRICE NUM_GRIDS QUANTITY_PER_GRID
Example: python grid.py BTCUSDT 90000 95000 10 0.001
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
    """Execute Grid Trading strategy from command line."""
    
    # Load environment variables
    load_dotenv()
    
    # Check arguments
    if len(sys.argv) < 6:
        print("❌ Error: Insufficient arguments")
        print("\nUsage: python grid.py SYMBOL LOWER_PRICE UPPER_PRICE NUM_GRIDS QUANTITY_PER_GRID")
        print("\nExample:")
        print("  python grid.py BTCUSDT 90000 95000 10 0.001")
        print("\nDescription:")
        print("  SYMBOL              - Trading pair (e.g., BTCUSDT)")
        print("  LOWER_PRICE         - Bottom of price grid")
        print("  UPPER_PRICE         - Top of price grid")
        print("  NUM_GRIDS           - Number of price levels in grid")
        print("  QUANTITY_PER_GRID   - Quantity to trade at each level")
        print("\nWhat is Grid Trading?")
        print("  Grid trading places buy orders below current price and sell")
        print("  orders above current price at regular intervals. When an order")
        print("  fills, it's automatically replaced to profit from price swings.")
        print("  Best for ranging markets.")
        sys.exit(1)
    
    # Parse arguments
    symbol = sys.argv[1].upper()
    lower_price = float(sys.argv[2])
    upper_price = float(sys.argv[3])
    num_grids = int(sys.argv[4])
    quantity_per_grid = float(sys.argv[5])
    
    # Validate inputs
    if lower_price <= 0 or upper_price <= 0:
        print(f"❌ Error: Prices must be positive")
        sys.exit(1)
    
    if lower_price >= upper_price:
        print(f"❌ Error: Lower price must be less than upper price")
        sys.exit(1)
    
    if num_grids < 2:
        print(f"❌ Error: Must have at least 2 grid levels")
        sys.exit(1)
    
    if quantity_per_grid <= 0:
        print(f"❌ Error: Quantity per grid must be positive")
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
        print("GRID TRADING STRATEGY")
        print("=" * 70)
        print(f"Symbol: {symbol}")
        print(f"Price Range: {lower_price} - {upper_price}")
        print(f"Number of Grids: {num_grids}")
        print(f"Quantity per Grid: {quantity_per_grid}")
        print(f"Grid Spacing: {(upper_price - lower_price) / (num_grids - 1):.2f}")
        print(f"Testnet: {testnet}")
        print("=" * 70)
        
        # Initialize client
        logger.info(f"Initializing Binance client (testnet={testnet})")
        client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            client.API_URL = 'https://testnet.binancefuture.com'
        
        # Initialize advanced bot
        bot = AdvancedOrderBot(client)
        
        # Get current price
        try:
            ticker = client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            print(f"\nCurrent Price: {current_price}")
            
            # Calculate expected orders
            grid_spacing = (upper_price - lower_price) / (num_grids - 1)
            buy_orders = 0
            sell_orders = 0
            
            for i in range(num_grids):
                price = lower_price + (i * grid_spacing)
                if price < current_price:
                    buy_orders += 1
                else:
                    sell_orders += 1
            
            print(f"Expected: {buy_orders} buy orders below price, {sell_orders} sell orders above price")
            
        except Exception as e:
            print(f"Warning: Could not fetch current price: {str(e)}")
        
        # Start grid trading
        print("\nStarting Grid Trading strategy...")
        result = bot.start_grid_trading(
            symbol=symbol,
            lower_price=lower_price,
            upper_price=upper_price,
            num_grids=num_grids,
            quantity_per_grid=quantity_per_grid
        )
        
        if result['success']:
            print("\n✅ Grid Trading Started Successfully!")
            print(f"\nGrid ID: {result['grid_id']}")
            print(f"Number of Grids: {result['num_grids']}")
            print(f"Price Range: {result['lower_price']} - {result['upper_price']}")
            print(f"Grid Spacing: {result['grid_spacing']:.2f}")
            print(f"Quantity per Grid: {result['quantity_per_grid']}")
            print(f"Orders Placed: {len(result['orders'])} orders")
            
            # Show order details
            print("\nGrid Orders:")
            print("-" * 70)
            for order in result['orders']:
                print(f"  {order['side']:4} @ {order['price']:>10} | Qty: {order['quantity']} | Order ID: {order['order_id']}")
            
            print("\n✓ Grid is monitoring and will replace filled orders automatically...")
            print("\nMonitoring Grid Trading:")
            print("-" * 70)
            
            # Monitor grid
            grid_id = result['grid_id']
            
            try:
                while True:
                    time.sleep(10)
                    
                    status = bot.get_strategy_status(grid_id)
                    if status['success']:
                        strategy = status['strategy']
                        active_orders = strategy.get('active_orders', 0)
                        total_trades = strategy.get('total_trades', 0)
                        status_str = strategy.get('status', 'unknown')
                        
                        print(f"Active Orders: {active_orders} | Total Trades: {total_trades} | Status: {status_str}")
                        
                        if status_str in ['stopped', 'error']:
                            break
                            
            except KeyboardInterrupt:
                print("\n\nMonitoring stopped. Grid will continue running in the background.")
                print("To stop the grid, you need to manually cancel the orders.")
            
            print("\n✅ Grid monitoring ended")
            
            # Show final summary
            final_status = bot.get_strategy_status(grid_id)
            if final_status['success']:
                strategy = final_status['strategy']
                print(f"\nFinal Summary:")
                print(f"Active Orders: {strategy.get('active_orders', 0)}")
                print(f"Total Trades: {strategy.get('total_trades', 0)}")
                print(f"Status: {strategy.get('status', 'unknown')}")
                
        else:
            print(f"\n❌ Grid Trading Failed!")
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
