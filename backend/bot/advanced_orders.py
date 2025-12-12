"""
Advanced Trading Strategies for Binance Futures
Implements: OCO, TWAP, and Grid Trading
"""

import logging
import time
from typing import Dict, Any, List, Optional
from binance.client import Client
from binance.exceptions import BinanceAPIException
from decimal import Decimal, ROUND_DOWN
import threading
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class AdvancedOrderBot:
    """
    Advanced trading bot with OCO, TWAP, and Grid Trading support.
    """
    
    def __init__(self, client: Client):
        """
        Initialize advanced order bot.
        
        Args:
            client: Initialized Binance client
        """
        self.client = client
        self.active_strategies = {}
        logger.info("Advanced Order Bot initialized")
    
    def place_oco_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        stop_price: float,
        stop_limit_price: float
    ) -> Dict[str, Any]:
        """
        Place OCO (One-Cancels-the-Other) order.
        Combines a limit order with a stop-limit order.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit order price (take profit)
            stop_price: Stop price (stop loss trigger)
            stop_limit_price: Stop limit price (stop loss execution)
            
        Returns:
            Dictionary with order details
            
        Example:
            # Buy BTC, set take-profit at $95,000 and stop-loss at $90,000
            bot.place_oco_order('BTCUSDT', 'SELL', 0.001, 95000, 90000, 89900)
        """
        try:
            logger.info(f"Placing OCO order for {symbol}")
            logger.info(f"Side: {side}, Quantity: {quantity}")
            logger.info(f"Take Profit: ${price}, Stop: ${stop_price}, Stop Limit: ${stop_limit_price}")
            
            # Validate inputs
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if quantity <= 0:
                raise ValueError("Quantity must be positive")
            
            if side == 'SELL':
                if price <= stop_price:
                    raise ValueError("For SELL: Take profit price must be higher than stop price")
            else:
                if price >= stop_price:
                    raise ValueError("For BUY: Take profit price must be lower than stop price")
            
            # Get symbol info for price precision
            exchange_info = self.client.futures_exchange_info()
            symbol_info = next(s for s in exchange_info['symbols'] if s['symbol'] == symbol)
            price_filter = next(f for f in symbol_info['filters'] if f['filterType'] == 'PRICE_FILTER')
            tick_size = float(price_filter['tickSize'])
            
            # Round prices to tick size
            import math
            price = math.floor(price / tick_size) * tick_size
            stop_price = math.floor(stop_price / tick_size) * tick_size
            stop_limit_price = math.floor(stop_limit_price / tick_size) * tick_size
            
            # Place limit order (take profit)
            take_profit_order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                timeInForce='GTC',
                quantity=quantity,
                price=price
            )
            
            logger.info(f"Take profit order placed: {take_profit_order['orderId']}")
            
            # Place stop-limit order (stop loss) - same side as take profit
            # For closing a position, both orders should be on the same side
            stop_loss_order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP',
                timeInForce='GTC',
                quantity=quantity,
                stopPrice=stop_price,
                price=stop_limit_price
            )
            
            logger.info(f"Stop loss order placed: {stop_loss_order['orderId']}")
            
            # Store OCO pair
            oco_id = f"OCO_{int(time.time())}"
            self.active_strategies[oco_id] = {
                'type': 'OCO',
                'symbol': symbol,
                'take_profit_order_id': take_profit_order['orderId'],
                'stop_loss_order_id': stop_loss_order['orderId'],
                'created_at': datetime.now().isoformat()
            }
            
            # Monitor OCO orders in background
            threading.Thread(
                target=self._monitor_oco_orders,
                args=(oco_id, symbol, take_profit_order['orderId'], stop_loss_order['orderId']),
                daemon=True
            ).start()
            
            result = {
                'success': True,
                'oco_id': oco_id,
                'take_profit_order': {
                    'order_id': take_profit_order['orderId'],
                    'price': price,
                    'status': take_profit_order['status']
                },
                'stop_loss_order': {
                    'order_id': stop_loss_order['orderId'],
                    'stop_price': stop_price,
                    'limit_price': stop_limit_price,
                    'status': stop_loss_order['status']
                }
            }
            
            logger.info(f"OCO order placed successfully: {oco_id}")
            return result
            
        except BinanceAPIException as e:
            logger.error(f"Binance API error in OCO order: {e.message}")
            return {
                'success': False,
                'error': e.message,
                'error_code': e.code
            }
        except Exception as e:
            logger.error(f"Error placing OCO order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _monitor_oco_orders(self, oco_id: str, symbol: str, tp_order_id: int, sl_order_id: int):
        """Monitor OCO orders and cancel the opposite one when one is filled."""
        try:
            while True:
                time.sleep(2)
                
                # Check take profit order
                tp_order = self.client.futures_get_order(symbol=symbol, orderId=tp_order_id)
                
                if tp_order['status'] == 'FILLED':
                    logger.info(f"OCO {oco_id}: Take profit filled, cancelling stop loss")
                    try:
                        self.client.futures_cancel_order(symbol=symbol, orderId=sl_order_id)
                    except:
                        pass
                    break
                
                # Check stop loss order
                sl_order = self.client.futures_get_order(symbol=symbol, orderId=sl_order_id)
                
                if sl_order['status'] == 'FILLED':
                    logger.info(f"OCO {oco_id}: Stop loss triggered, cancelling take profit")
                    try:
                        self.client.futures_cancel_order(symbol=symbol, orderId=tp_order_id)
                    except:
                        pass
                    break
                
                # Check if both are cancelled
                if tp_order['status'] == 'CANCELED' and sl_order['status'] == 'CANCELED':
                    logger.info(f"OCO {oco_id}: Both orders cancelled")
                    break
                    
        except Exception as e:
            logger.error(f"Error monitoring OCO orders: {str(e)}")
    
    def place_twap_order(
        self,
        symbol: str,
        side: str,
        total_quantity: float,
        duration_minutes: int,
        num_orders: int = 10
    ) -> Dict[str, Any]:
        """
        Place TWAP (Time-Weighted Average Price) order.
        Splits a large order into smaller chunks executed over time.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            side: 'BUY' or 'SELL'
            total_quantity: Total quantity to trade
            duration_minutes: Time period to spread orders over
            num_orders: Number of smaller orders to split into
            
        Returns:
            Dictionary with strategy details
            
        Example:
            # Buy 0.1 BTC over 30 minutes in 10 equal chunks
            bot.place_twap_order('BTCUSDT', 'BUY', 0.1, 30, 10)
        """
        try:
            logger.info(f"Placing TWAP order for {symbol}")
            logger.info(f"Total quantity: {total_quantity}, Duration: {duration_minutes}min, Orders: {num_orders}")
            
            # Validate inputs
            if side not in ['BUY', 'SELL']:
                raise ValueError("Side must be 'BUY' or 'SELL'")
            
            if total_quantity <= 0:
                raise ValueError("Total quantity must be positive")
            
            if duration_minutes <= 0:
                raise ValueError("Duration must be positive")
            
            if num_orders <= 0:
                raise ValueError("Number of orders must be positive")
            
            # Calculate order parameters
            order_quantity = total_quantity / num_orders
            interval_seconds = (duration_minutes * 60) / num_orders
            
            # Get symbol info for precision
            exchange_info = self.client.futures_exchange_info()
            symbol_info = None
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    symbol_info = s
                    break
            
            if not symbol_info:
                raise ValueError(f"Symbol {symbol} not found")
            
            # Get quantity precision
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'LOT_SIZE':
                    step_size = float(filter['stepSize'])
                    # Round quantity to step size
                    order_quantity = round(order_quantity / step_size) * step_size
                    break
            
            twap_id = f"TWAP_{int(time.time())}"
            self.active_strategies[twap_id] = {
                'type': 'TWAP',
                'symbol': symbol,
                'side': side,
                'total_quantity': total_quantity,
                'order_quantity': order_quantity,
                'num_orders': num_orders,
                'interval_seconds': interval_seconds,
                'orders_placed': 0,
                'orders': [],
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
            # Execute TWAP in background thread
            threading.Thread(
                target=self._execute_twap,
                args=(twap_id, symbol, side, order_quantity, num_orders, interval_seconds),
                daemon=True
            ).start()
            
            result = {
                'success': True,
                'twap_id': twap_id,
                'total_quantity': total_quantity,
                'order_quantity': order_quantity,
                'num_orders': num_orders,
                'interval_seconds': interval_seconds,
                'estimated_completion': datetime.now() + timedelta(minutes=duration_minutes)
            }
            
            logger.info(f"TWAP order initiated: {twap_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error placing TWAP order: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _execute_twap(self, twap_id: str, symbol: str, side: str, quantity: float, num_orders: int, interval: float):
        """Execute TWAP strategy in background."""
        try:
            strategy = self.active_strategies[twap_id]
            
            for i in range(num_orders):
                if strategy.get('status') == 'cancelled':
                    logger.info(f"TWAP {twap_id} cancelled after {i} orders")
                    break
                
                try:
                    # Place market order for this chunk
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type='MARKET',
                        quantity=quantity
                    )
                    
                    strategy['orders'].append({
                        'order_id': order['orderId'],
                        'quantity': quantity,
                        'status': order['status'],
                        'timestamp': datetime.now().isoformat()
                    })
                    strategy['orders_placed'] += 1
                    
                    logger.info(f"TWAP {twap_id}: Order {i+1}/{num_orders} placed - {order['orderId']}")
                    
                    # Wait for next interval (except for last order)
                    if i < num_orders - 1:
                        time.sleep(interval)
                        
                except BinanceAPIException as e:
                    logger.error(f"TWAP {twap_id}: Order {i+1} failed - {e.message}")
                    strategy['orders'].append({
                        'error': e.message,
                        'timestamp': datetime.now().isoformat()
                    })
            
            strategy['status'] = 'completed'
            logger.info(f"TWAP {twap_id} completed: {strategy['orders_placed']}/{num_orders} orders placed")
            
        except Exception as e:
            logger.error(f"Error executing TWAP {twap_id}: {str(e)}")
            self.active_strategies[twap_id]['status'] = 'error'
    
    def start_grid_trading(
        self,
        symbol: str,
        lower_price: float,
        upper_price: float,
        num_grids: int,
        quantity_per_grid: float
    ) -> Dict[str, Any]:
        """
        Start Grid Trading strategy.
        Places buy orders below current price and sell orders above.
        
        Args:
            symbol: Trading pair (e.g., 'BTCUSDT')
            lower_price: Lower bound of grid
            upper_price: Upper bound of grid
            num_grids: Number of grid levels
            quantity_per_grid: Quantity for each grid order
            
        Returns:
            Dictionary with grid strategy details
            
        Example:
            # Create 10 grid levels between $90,000 and $95,000
            bot.start_grid_trading('BTCUSDT', 90000, 95000, 10, 0.001)
        """
        try:
            logger.info(f"Starting Grid Trading for {symbol}")
            logger.info(f"Range: ${lower_price} - ${upper_price}, Grids: {num_grids}")
            
            # Validate inputs
            if lower_price >= upper_price:
                raise ValueError("Lower price must be less than upper price")
            
            if num_grids < 2:
                raise ValueError("Number of grids must be at least 2")
            
            if quantity_per_grid <= 0:
                raise ValueError("Quantity per grid must be positive")
            
            # Get current price
            ticker = self.client.futures_symbol_ticker(symbol=symbol)
            current_price = float(ticker['price'])
            
            logger.info(f"Current price: ${current_price}")
            
            # Calculate grid levels
            price_step = (upper_price - lower_price) / (num_grids - 1)
            grid_levels = [lower_price + (i * price_step) for i in range(num_grids)]
            
            # Get symbol info for precision
            exchange_info = self.client.futures_exchange_info()
            symbol_info = None
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    symbol_info = s
                    break
            
            # Get price precision
            tick_size = None
            for filter in symbol_info['filters']:
                if filter['filterType'] == 'PRICE_FILTER':
                    tick_size = float(filter['tickSize'])
                    break
            
            grid_id = f"GRID_{int(time.time())}"
            self.active_strategies[grid_id] = {
                'type': 'GRID',
                'symbol': symbol,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'num_grids': num_grids,
                'quantity_per_grid': quantity_per_grid,
                'grid_levels': grid_levels,
                'orders': [],
                'active_orders': 0,
                'total_trades': 0,
                'status': 'active',
                'created_at': datetime.now().isoformat()
            }
            
            # Place initial grid orders
            for level in grid_levels:
                # Round to tick size
                level = round(level / tick_size) * tick_size
                
                try:
                    if level < current_price:
                        # Place buy order below current price
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side='BUY',
                            type='LIMIT',
                            timeInForce='GTC',
                            quantity=quantity_per_grid,
                            price=level
                        )
                        logger.info(f"Grid buy order placed at ${level}: {order['orderId']}")
                    else:
                        # Place sell order above current price
                        order = self.client.futures_create_order(
                            symbol=symbol,
                            side='SELL',
                            type='LIMIT',
                            timeInForce='GTC',
                            quantity=quantity_per_grid,
                            price=level
                        )
                        logger.info(f"Grid sell order placed at ${level}: {order['orderId']}")
                    
                    self.active_strategies[grid_id]['orders'].append({
                        'order_id': order['orderId'],
                        'price': level,
                        'quantity': quantity_per_grid,
                        'side': 'BUY' if level < current_price else 'SELL',
                        'status': order['status']
                    })
                    self.active_strategies[grid_id]['active_orders'] += 1
                    
                except BinanceAPIException as e:
                    logger.error(f"Failed to place grid order at ${level}: {e.message}")
            
            # Monitor grid in background
            threading.Thread(
                target=self._monitor_grid,
                args=(grid_id, symbol, current_price, grid_levels, quantity_per_grid, tick_size),
                daemon=True
            ).start()
            
            result = {
                'success': True,
                'grid_id': grid_id,
                'num_grids': num_grids,
                'lower_price': lower_price,
                'upper_price': upper_price,
                'grid_spacing': price_step,
                'quantity_per_grid': quantity_per_grid,
                'grid_levels': grid_levels,
                'orders': self.active_strategies[grid_id]['orders'],
                'current_price': current_price
            }
            
            logger.info(f"Grid trading started: {grid_id}")
            return result
            
        except Exception as e:
            logger.error(f"Error starting grid trading: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _monitor_grid(self, grid_id: str, symbol: str, initial_price: float, grid_levels: List[float], quantity: float, tick_size: float):
        """Monitor grid orders and replace filled ones."""
        try:
            strategy = self.active_strategies[grid_id]
            
            while strategy.get('status') == 'active':
                time.sleep(5)
                
                # Check each order
                for order_info in strategy['orders']:
                    if order_info.get('checked'):
                        continue
                    
                    try:
                        order = self.client.futures_get_order(
                            symbol=symbol,
                            orderId=order_info['order_id']
                        )
                        
                        if order['status'] == 'FILLED':
                            logger.info(f"Grid order filled: {order_info['order_id']} at ${order_info['price']}")
                            order_info['checked'] = True
                            strategy['total_trades'] += 1
                            strategy['active_orders'] -= 1
                            
                            # Place opposite order at the same level
                            opposite_side = 'SELL' if order_info['side'] == 'BUY' else 'BUY'
                            price = round(order_info['price'] / tick_size) * tick_size
                            
                            new_order = self.client.futures_create_order(
                                symbol=symbol,
                                side=opposite_side,
                                type='LIMIT',
                                timeInForce='GTC',
                                quantity=quantity,
                                price=price
                            )
                            
                            strategy['orders'].append({
                                'order_id': new_order['orderId'],
                                'price': price,
                                'side': opposite_side,
                                'status': new_order['status']
                            })
                            strategy['active_orders'] += 1
                            
                            logger.info(f"Grid order replaced with {opposite_side} at ${price}")
                            
                    except Exception as e:
                        logger.error(f"Error checking grid order: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error monitoring grid {grid_id}: {str(e)}")
    
    def stop_grid_trading(self, grid_id: str) -> Dict[str, Any]:
        """Stop grid trading and cancel all orders."""
        try:
            if grid_id not in self.active_strategies:
                return {'success': False, 'error': 'Grid ID not found'}
            
            strategy = self.active_strategies[grid_id]
            strategy['status'] = 'stopped'
            
            symbol = strategy['symbol']
            cancelled = 0
            
            for order_info in strategy['orders']:
                try:
                    self.client.futures_cancel_order(
                        symbol=symbol,
                        orderId=order_info['order_id']
                    )
                    cancelled += 1
                except:
                    pass
            
            logger.info(f"Grid {grid_id} stopped. Cancelled {cancelled} orders.")
            
            return {
                'success': True,
                'grid_id': grid_id,
                'orders_cancelled': cancelled
            }
            
        except Exception as e:
            logger.error(f"Error stopping grid: {str(e)}")
            return {'success': False, 'error': str(e)}
    
    def get_strategy_status(self, strategy_id: str) -> Dict[str, Any]:
        """Get status of an active strategy."""
        if strategy_id not in self.active_strategies:
            return {'success': False, 'error': 'Strategy ID not found'}
        
        return {
            'success': True,
            'strategy': self.active_strategies[strategy_id]
        }
    
    def list_active_strategies(self) -> Dict[str, Any]:
        """List all active strategies."""
        return {
            'success': True,
            'strategies': {
                sid: {
                    'type': s['type'],
                    'symbol': s['symbol'],
                    'status': s.get('status', 'unknown'),
                    'created_at': s['created_at']
                }
                for sid, s in self.active_strategies.items()
            }
        }
