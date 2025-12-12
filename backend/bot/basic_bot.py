import logging
from typing import Dict, Any, Optional, Literal
from binance.client import Client
from binance.exceptions import BinanceAPIException, BinanceOrderException
from decimal import Decimal, ROUND_DOWN
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('trading_bot.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


class BasicBot:
    """
    A basic trading bot for Binance Futures Testnet.
    Supports market orders, limit orders, and advanced order types.
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = True):
        """
        Initialize the trading bot.
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            testnet: Whether to use testnet (default: True)
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        try:
            self.client = Client(api_key, api_secret, testnet=testnet)
            if testnet:
                self.client.API_URL = 'https://testnet.binancefuture.com'
            
            logger.info(f"Bot initialized successfully. Testnet: {testnet}")
            self._test_connection()
        except Exception as e:
            logger.error(f"Failed to initialize bot: {str(e)}")
            raise
    
    def _test_connection(self) -> bool:
        """Test connection to Binance API."""
        try:
            self.client.ping()
            logger.info("Successfully connected to Binance API")
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False
    
    def get_account_balance(self) -> Dict[str, Any]:
        """
        Get account balance information.
        
        Returns:
            Dictionary containing account balance information
        """
        try:
            logger.info("Fetching account balance...")
            account = self.client.futures_account()
            
            balances = []
            for asset in account['assets']:
                if float(asset['walletBalance']) > 0:
                    balances.append({
                        'asset': asset['asset'],
                        'wallet_balance': asset['walletBalance'],
                        'available_balance': asset['availableBalance'],
                        'unrealized_profit': asset['unrealizedProfit']
                    })
            
            result = {
                'total_wallet_balance': account['totalWalletBalance'],
                'total_unrealized_profit': account['totalUnrealizedProfit'],
                'total_margin_balance': account['totalMarginBalance'],
                'available_balance': account['availableBalance'],
                'assets': balances
            }
            
            logger.info(f"Account balance retrieved successfully")
            return result
            
        except BinanceAPIException as e:
            logger.error(f"API error while fetching balance: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error while fetching balance: {str(e)}")
            raise
    
    def get_symbol_info(self, symbol: str) -> Dict[str, Any]:
        """
        Get symbol information including price filters and lot sizes.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            
        Returns:
            Dictionary containing symbol information
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return s
            
            raise ValueError(f"Symbol {symbol} not found")
            
        except Exception as e:
            logger.error(f"Error fetching symbol info: {str(e)}")
            raise
    
    def _validate_and_format_quantity(self, symbol: str, quantity: float) -> str:
        """
        Validate and format quantity according to symbol's lot size rules.
        
        Args:
            symbol: Trading pair symbol
            quantity: Order quantity
            
        Returns:
            Formatted quantity as string
        """
        try:
            symbol_info = self.get_symbol_info(symbol)
            
            # Find LOT_SIZE filter
            lot_size_filter = None
            for f in symbol_info['filters']:
                if f['filterType'] == 'LOT_SIZE':
                    lot_size_filter = f
                    break
            
            if not lot_size_filter:
                return str(quantity)
            
            min_qty = Decimal(lot_size_filter['minQty'])
            max_qty = Decimal(lot_size_filter['maxQty'])
            step_size = Decimal(lot_size_filter['stepSize'])
            
            qty = Decimal(str(quantity))
            
            # Check minimum quantity
            if qty < min_qty:
                raise ValueError(f"Quantity {quantity} is below minimum {min_qty}")
            
            # Check maximum quantity
            if qty > max_qty:
                raise ValueError(f"Quantity {quantity} exceeds maximum {max_qty}")
            
            # Round to step size
            precision = abs(step_size.as_tuple().exponent)
            qty = qty.quantize(step_size, rounding=ROUND_DOWN)
            
            return str(qty)
            
        except Exception as e:
            logger.error(f"Error validating quantity: {str(e)}")
            raise
    
    def place_market_order(
        self,
        symbol: str,
        side: Literal['BUY', 'SELL'],
        quantity: float
    ) -> Dict[str, Any]:
        """
        Place a market order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            
        Returns:
            Dictionary containing order details
        """
        try:
            logger.info(f"Placing MARKET {side} order: {quantity} {symbol}")
            
            # Validate inputs
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            # Format quantity
            formatted_quantity = self._validate_and_format_quantity(symbol, quantity)
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=formatted_quantity
            )
            
            logger.info(f"Market order placed successfully. Order ID: {order['orderId']}")
            logger.info(f"Order details: {order}")
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'quantity': order['origQty'],
                'status': order['status'],
                'price': order.get('avgPrice', 'N/A'),
                'time': order['updateTime'],
                'raw_response': order
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except BinanceOrderException as e:
            logger.error(f"Binance order error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error placing market order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def place_limit_order(
        self,
        symbol: str,
        side: Literal['BUY', 'SELL'],
        quantity: float,
        price: float,
        time_in_force: str = 'GTC'
    ) -> Dict[str, Any]:
        """
        Place a limit order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            price: Limit price
            time_in_force: Time in force (default: 'GTC' - Good Till Cancel)
            
        Returns:
            Dictionary containing order details
        """
        try:
            logger.info(f"Placing LIMIT {side} order: {quantity} {symbol} @ {price}")
            
            # Validate inputs
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            # Format quantity
            formatted_quantity = self._validate_and_format_quantity(symbol, quantity)
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=formatted_quantity,
                price=str(price),
                timeInForce=time_in_force
            )
            
            logger.info(f"Limit order placed successfully. Order ID: {order['orderId']}")
            logger.info(f"Order details: {order}")
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'quantity': order['origQty'],
                'price': order['price'],
                'status': order['status'],
                'time_in_force': order['timeInForce'],
                'time': order['updateTime'],
                'raw_response': order
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except BinanceOrderException as e:
            logger.error(f"Binance order error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error placing limit order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def place_stop_limit_order(
        self,
        symbol: str,
        side: Literal['BUY', 'SELL'],
        quantity: float,
        stop_price: float,
        limit_price: float,
        time_in_force: str = 'GTC'
    ) -> Dict[str, Any]:
        """
        Place a stop-limit order.
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            side: Order side ('BUY' or 'SELL')
            quantity: Order quantity
            stop_price: Stop price to trigger the order
            limit_price: Limit price for the order
            time_in_force: Time in force (default: 'GTC' - Good Till Cancel)
            
        Returns:
            Dictionary containing order details
        """
        try:
            logger.info(f"Placing STOP_LIMIT {side} order: {quantity} {symbol} stop@{stop_price} limit@{limit_price}")
            
            # Validate inputs
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            # Format quantity
            formatted_quantity = self._validate_and_format_quantity(symbol, quantity)
            
            # Place order
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                quantity=formatted_quantity,
                price=str(limit_price),
                stopPrice=str(stop_price),
                timeInForce=time_in_force
            )
            
            logger.info(f"Stop-limit order placed successfully. Order ID: {order['orderId']}")
            logger.info(f"Order details: {order}")
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'quantity': order['origQty'],
                'stop_price': order['stopPrice'],
                'limit_price': order['price'],
                'status': order['status'],
                'time_in_force': order['timeInForce'],
                'time': order['updateTime'],
                'raw_response': order
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error placing stop-limit order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_order(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Cancel an existing order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID to cancel
            
        Returns:
            Dictionary containing cancellation details
        """
        try:
            logger.info(f"Cancelling order {order_id} for {symbol}")
            
            result = self.client.futures_cancel_order(
                symbol=symbol,
                orderId=order_id
            )
            
            logger.info(f"Order {order_id} cancelled successfully")
            
            return {
                'success': True,
                'order_id': result['orderId'],
                'symbol': result['symbol'],
                'status': result['status'],
                'raw_response': result
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error cancelling order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_order_status(self, symbol: str, order_id: int) -> Dict[str, Any]:
        """
        Get the status of an order.
        
        Args:
            symbol: Trading pair symbol
            order_id: Order ID
            
        Returns:
            Dictionary containing order status
        """
        try:
            logger.info(f"Fetching status for order {order_id} on {symbol}")
            
            order = self.client.futures_get_order(
                symbol=symbol,
                orderId=order_id
            )
            
            return {
                'success': True,
                'order_id': order['orderId'],
                'symbol': order['symbol'],
                'side': order['side'],
                'type': order['type'],
                'status': order['status'],
                'quantity': order['origQty'],
                'executed_quantity': order['executedQty'],
                'price': order.get('price', 'N/A'),
                'avg_price': order.get('avgPrice', 'N/A'),
                'time': order['time'],
                'update_time': order['updateTime'],
                'raw_response': order
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching order status: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_open_orders(self, symbol: Optional[str] = None) -> Dict[str, Any]:
        """
        Get all open orders.
        
        Args:
            symbol: Optional trading pair symbol. If None, returns all open orders.
            
        Returns:
            Dictionary containing open orders
        """
        try:
            logger.info(f"Fetching open orders{' for ' + symbol if symbol else ''}")
            
            if symbol:
                orders = self.client.futures_get_open_orders(symbol=symbol)
            else:
                orders = self.client.futures_get_open_orders()
            
            formatted_orders = []
            for order in orders:
                formatted_orders.append({
                    'order_id': order['orderId'],
                    'symbol': order['symbol'],
                    'side': order['side'],
                    'type': order['type'],
                    'status': order['status'],
                    'quantity': order['origQty'],
                    'executed_quantity': order['executedQty'],
                    'price': order.get('price', 'N/A'),
                    'stop_price': order.get('stopPrice', 'N/A'),
                    'time': order['time']
                })
            
            logger.info(f"Found {len(formatted_orders)} open orders")
            
            return {
                'success': True,
                'count': len(formatted_orders),
                'orders': formatted_orders
            }
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error: {e.message} (Code: {e.code})")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Unexpected error fetching open orders: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get the current price for a symbol.
        
        Args:
            symbol: Trading pair symbol
            
        Returns:
            Current price as float, or None if error
        """
        try:
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            price = float(ticker['price'])
            logger.info(f"Current price for {symbol}: {price}")
            return price
            
        except Exception as e:
            logger.error(f"Error fetching current price: {str(e)}")
            return None
