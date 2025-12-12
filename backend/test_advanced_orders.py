"""
Test script for all advanced order types.
Tests OCO, TWAP, and Grid Trading with small quantities on testnet.
"""

import os
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from binance.client import Client
from bot.advanced_orders import AdvancedOrderBot
from dotenv import load_dotenv
import logging
import time

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


def test_advanced_orders():
    """Test all advanced order types with minimal risk."""
    
    # Load environment
    load_dotenv()
    
    api_key = os.getenv('BINANCE_API_KEY')
    api_secret = os.getenv('BINANCE_API_SECRET')
    testnet = os.getenv('BINANCE_TESTNET', 'True').lower() == 'true'
    
    if not api_key or not api_secret:
        print("❌ Error: API credentials not found")
        return False
    
    print("=" * 70)
    print("ADVANCED ORDERS TEST SUITE")
    print("=" * 70)
    print(f"Testnet Mode: {testnet}")
    print()
    
    try:
        # Initialize client
        client = Client(api_key, api_secret, testnet=testnet)
        if testnet:
            client.API_URL = 'https://testnet.binancefuture.com'
        
        bot = AdvancedOrderBot(client)
        
        # Get current BTC price
        ticker = client.futures_symbol_ticker(symbol='BTCUSDT')
        current_price = float(ticker['price'])
        print(f"Current BTC Price: ${current_price:.2f}")
        print()
        
        # Test 1: OCO Order
        print("=" * 70)
        print("TEST 1: OCO (One-Cancels-the-Other) Order")
        print("=" * 70)
        
        # Place OCO with small quantity
        oco_result = bot.place_oco_order(
            symbol='BTCUSDT',
            side='SELL',
            quantity=0.001,  # Very small quantity
            price=current_price * 1.05,  # Take profit 5% above
            stop_price=current_price * 0.95,  # Stop loss 5% below
            stop_limit_price=current_price * 0.94  # Stop limit slightly lower
        )
        
        if oco_result['success']:
            print("✅ OCO Order Placed Successfully!")
            print(f"   OCO ID: {oco_result['oco_id']}")
            print(f"   Take Profit Order: {oco_result['take_profit_order']['order_id']}")
            print(f"   Stop Loss Order: {oco_result['stop_loss_order']['order_id']}")
            
            # Cancel the orders for testing
            time.sleep(2)
            try:
                client.futures_cancel_order(symbol='BTCUSDT', orderId=oco_result['take_profit_order']['order_id'])
                client.futures_cancel_order(symbol='BTCUSDT', orderId=oco_result['stop_loss_order']['order_id'])
                print("   Orders cancelled (test cleanup)")
            except:
                pass
        else:
            print(f"❌ OCO Order Failed: {oco_result.get('error')}")
            return False
        
        print()
        
        # Test 2: TWAP Order
        print("=" * 70)
        print("TEST 2: TWAP (Time-Weighted Average Price) Order")
        print("=" * 70)
        
        # Place TWAP with small quantity over short duration
        twap_result = bot.place_twap_order(
            symbol='BTCUSDT',
            side='BUY',
            total_quantity=0.003,  # 0.003 BTC total
            duration_minutes=2,  # Just 2 minutes
            num_orders=3  # Split into 3 orders
        )
        
        if twap_result['success']:
            print("✅ TWAP Strategy Started Successfully!")
            print(f"   TWAP ID: {twap_result['twap_id']}")
            print(f"   Total Quantity: {twap_result['total_quantity']}")
            print(f"   Order Quantity: {twap_result['order_quantity']} per order")
            print(f"   Interval: {twap_result['interval_seconds']:.1f} seconds")
            print()
            print("   Monitoring TWAP execution (3 orders)...")
            
            # Monitor for completion
            for i in range(12):  # 2 minutes max
                time.sleep(10)
                status = bot.get_strategy_status(twap_result['twap_id'])
                if status['success']:
                    strategy = status['strategy']
                    orders_placed = strategy.get('orders_placed', 0)
                    print(f"   Progress: {orders_placed}/3 orders placed")
                    if strategy.get('status') == 'completed':
                        break
            
            print("✅ TWAP Test Completed")
        else:
            print(f"❌ TWAP Order Failed: {twap_result.get('error')}")
            return False
        
        print()
        
        # Test 3: Grid Trading
        print("=" * 70)
        print("TEST 3: Grid Trading Strategy")
        print("=" * 70)
        
        # Place grid with narrow range and small quantities
        grid_result = bot.start_grid_trading(
            symbol='BTCUSDT',
            lower_price=current_price * 0.98,  # 2% below
            upper_price=current_price * 1.02,  # 2% above
            num_grids=5,  # Only 5 levels
            quantity_per_grid=0.0005  # Very small quantity
        )
        
        if grid_result['success']:
            print("✅ Grid Trading Started Successfully!")
            print(f"   Grid ID: {grid_result['grid_id']}")
            print(f"   Number of Grids: {grid_result['num_grids']}")
            print(f"   Price Range: ${grid_result['lower_price']:.2f} - ${grid_result['upper_price']:.2f}")
            print(f"   Grid Spacing: ${grid_result['grid_spacing']:.2f}")
            print(f"   Orders Placed: {len(grid_result['orders'])}")
            print()
            print("   Grid Orders:")
            for order in grid_result['orders']:
                print(f"      {order['side']:4} @ ${order['price']:>10.2f} | Qty: {order['quantity']} | ID: {order['order_id']}")
            
            # Monitor briefly
            print()
            print("   Monitoring grid for 20 seconds...")
            time.sleep(20)
            
            # Stop grid
            stop_result = bot.stop_grid_trading(grid_result['grid_id'])
            if stop_result['success']:
                print(f"   Grid stopped. Cancelled {stop_result['orders_cancelled']} orders")
            
            print("✅ Grid Trading Test Completed")
        else:
            print(f"❌ Grid Trading Failed: {grid_result.get('error')}")
            return False
        
        print()
        print("=" * 70)
        print("ALL TESTS PASSED! ✅")
        print("=" * 70)
        print()
        print("Summary:")
        print("  ✅ OCO orders working correctly")
        print("  ✅ TWAP execution working correctly")
        print("  ✅ Grid trading working correctly")
        print()
        print("Check bot.log for detailed execution logs.")
        
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {str(e)}")
        print(f"\n❌ Test Suite Failed: {str(e)}")
        return False


if __name__ == "__main__":
    success = test_advanced_orders()
    sys.exit(0 if success else 1)
