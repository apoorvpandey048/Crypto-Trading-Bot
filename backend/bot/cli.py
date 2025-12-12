#!/usr/bin/env python3
"""
Command-line interface for the Crypto Trading Bot.
Allows users to interact with the bot via terminal.
"""

import argparse
import sys
from typing import Optional
from getpass import getpass
import json
from basic_bot import BasicBot
import logging

# Configure logging for CLI
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_credentials() -> tuple[str, str]:
    """
    Get API credentials from user input.
    
    Returns:
        Tuple of (api_key, api_secret)
    """
    print("\n=== Binance API Credentials ===")
    api_key = input("Enter your Binance API Key: ").strip()
    api_secret = getpass("Enter your Binance API Secret: ").strip()
    return api_key, api_secret


def display_order_result(result: dict) -> None:
    """Display order result in a formatted way."""
    print("\n" + "="*50)
    if result.get('success'):
        print("✓ ORDER EXECUTED SUCCESSFULLY")
        print("="*50)
        for key, value in result.items():
            if key != 'raw_response' and key != 'success':
                print(f"{key.replace('_', ' ').title()}: {value}")
    else:
        print("✗ ORDER FAILED")
        print("="*50)
        print(f"Error: {result.get('error', 'Unknown error')}")
        if 'error_code' in result:
            print(f"Error Code: {result['error_code']}")
    print("="*50 + "\n")


def display_balance(balance: dict) -> None:
    """Display account balance in a formatted way."""
    print("\n" + "="*50)
    print("ACCOUNT BALANCE")
    print("="*50)
    print(f"Total Wallet Balance: {balance['total_wallet_balance']} USDT")
    print(f"Total Unrealized Profit: {balance['total_unrealized_profit']} USDT")
    print(f"Available Balance: {balance['available_balance']} USDT")
    print("\nAsset Breakdown:")
    for asset in balance['assets']:
        print(f"  {asset['asset']}:")
        print(f"    Wallet: {asset['wallet_balance']}")
        print(f"    Available: {asset['available_balance']}")
        print(f"    Unrealized P&L: {asset['unrealized_profit']}")
    print("="*50 + "\n")


def display_orders(orders_result: dict) -> None:
    """Display open orders in a formatted way."""
    print("\n" + "="*50)
    print(f"OPEN ORDERS ({orders_result['count']})")
    print("="*50)
    
    if orders_result['count'] == 0:
        print("No open orders")
    else:
        for order in orders_result['orders']:
            print(f"\nOrder ID: {order['order_id']}")
            print(f"  Symbol: {order['symbol']}")
            print(f"  Side: {order['side']}")
            print(f"  Type: {order['type']}")
            print(f"  Quantity: {order['quantity']}")
            print(f"  Price: {order['price']}")
            print(f"  Status: {order['status']}")
    print("="*50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description='Crypto Trading Bot CLI - Trade on Binance Futures Testnet',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Place a market buy order
  python cli.py market --symbol BTCUSDT --side BUY --quantity 0.001
  
  # Place a limit sell order
  python cli.py limit --symbol ETHUSDT --side SELL --quantity 0.01 --price 2000
  
  # Place a stop-limit order
  python cli.py stop-limit --symbol BTCUSDT --side SELL --quantity 0.001 --stop-price 30000 --limit-price 29900
  
  # Check account balance
  python cli.py balance
  
  # View open orders
  python cli.py orders --symbol BTCUSDT
  
  # Cancel an order
  python cli.py cancel --symbol BTCUSDT --order-id 12345
        """
    )
    
    parser.add_argument(
        '--api-key',
        help='Binance API Key (will prompt if not provided)',
        default=None
    )
    parser.add_argument(
        '--api-secret',
        help='Binance API Secret (will prompt if not provided)',
        default=None
    )
    parser.add_argument(
        '--no-testnet',
        action='store_true',
        help='Use production API instead of testnet (USE WITH CAUTION!)'
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Command to execute')
    
    # Market order command
    market_parser = subparsers.add_parser('market', help='Place a market order')
    market_parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    market_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    market_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    
    # Limit order command
    limit_parser = subparsers.add_parser('limit', help='Place a limit order')
    limit_parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    limit_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    limit_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    limit_parser.add_argument('--price', required=True, type=float, help='Limit price')
    limit_parser.add_argument('--time-in-force', default='GTC', help='Time in force (default: GTC)')
    
    # Stop-limit order command
    stop_parser = subparsers.add_parser('stop-limit', help='Place a stop-limit order')
    stop_parser.add_argument('--symbol', required=True, help='Trading pair (e.g., BTCUSDT)')
    stop_parser.add_argument('--side', required=True, choices=['BUY', 'SELL'], help='Order side')
    stop_parser.add_argument('--quantity', required=True, type=float, help='Order quantity')
    stop_parser.add_argument('--stop-price', required=True, type=float, help='Stop price')
    stop_parser.add_argument('--limit-price', required=True, type=float, help='Limit price')
    stop_parser.add_argument('--time-in-force', default='GTC', help='Time in force (default: GTC)')
    
    # Balance command
    balance_parser = subparsers.add_parser('balance', help='Get account balance')
    
    # Orders command
    orders_parser = subparsers.add_parser('orders', help='Get open orders')
    orders_parser.add_argument('--symbol', help='Trading pair (optional, shows all if not provided)')
    
    # Cancel command
    cancel_parser = subparsers.add_parser('cancel', help='Cancel an order')
    cancel_parser.add_argument('--symbol', required=True, help='Trading pair')
    cancel_parser.add_argument('--order-id', required=True, type=int, help='Order ID to cancel')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Get order status')
    status_parser.add_argument('--symbol', required=True, help='Trading pair')
    status_parser.add_argument('--order-id', required=True, type=int, help='Order ID')
    
    # Price command
    price_parser = subparsers.add_parser('price', help='Get current price')
    price_parser.add_argument('--symbol', required=True, help='Trading pair')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Get credentials
    if args.api_key and args.api_secret:
        api_key = args.api_key
        api_secret = args.api_secret
    else:
        api_key, api_secret = get_credentials()
    
    if not api_key or not api_secret:
        print("Error: API credentials are required")
        sys.exit(1)
    
    # Initialize bot
    try:
        testnet = not args.no_testnet
        if not testnet:
            confirm = input("\n⚠️  WARNING: You are about to use PRODUCTION API! Type 'YES' to confirm: ")
            if confirm != 'YES':
                print("Cancelled.")
                return
        
        print(f"\n🤖 Initializing bot (Testnet: {testnet})...")
        bot = BasicBot(api_key, api_secret, testnet=testnet)
        print("✓ Bot initialized successfully\n")
        
    except Exception as e:
        print(f"✗ Failed to initialize bot: {str(e)}")
        sys.exit(1)
    
    # Execute command
    try:
        if args.command == 'market':
            result = bot.place_market_order(
                symbol=args.symbol.upper(),
                side=args.side,
                quantity=args.quantity
            )
            display_order_result(result)
            
        elif args.command == 'limit':
            result = bot.place_limit_order(
                symbol=args.symbol.upper(),
                side=args.side,
                quantity=args.quantity,
                price=args.price,
                time_in_force=args.time_in_force
            )
            display_order_result(result)
            
        elif args.command == 'stop-limit':
            result = bot.place_stop_limit_order(
                symbol=args.symbol.upper(),
                side=args.side,
                quantity=args.quantity,
                stop_price=args.stop_price,
                limit_price=args.limit_price,
                time_in_force=args.time_in_force
            )
            display_order_result(result)
            
        elif args.command == 'balance':
            balance = bot.get_account_balance()
            display_balance(balance)
            
        elif args.command == 'orders':
            symbol = args.symbol.upper() if args.symbol else None
            result = bot.get_open_orders(symbol)
            display_orders(result)
            
        elif args.command == 'cancel':
            result = bot.cancel_order(
                symbol=args.symbol.upper(),
                order_id=args.order_id
            )
            display_order_result(result)
            
        elif args.command == 'status':
            result = bot.get_order_status(
                symbol=args.symbol.upper(),
                order_id=args.order_id
            )
            display_order_result(result)
            
        elif args.command == 'price':
            price = bot.get_current_price(args.symbol.upper())
            if price:
                print(f"\n{args.symbol.upper()}: ${price:,.2f}\n")
            else:
                print("\n✗ Failed to fetch price\n")
                
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n✗ Error: {str(e)}\n")
        sys.exit(1)


if __name__ == '__main__':
    main()
