from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from database import get_db
from models import User as UserModel, Trade as TradeModel, BotConfig as BotConfigModel
from schemas import (
    OrderRequest, OrderResponse, Trade, TradeCreate, TradeUpdate,
    OrderStatus, OrderType, AccountBalance, DashboardStats
)
from auth import get_current_active_user
from bot.basic_bot import BasicBot
from config import settings
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trading", tags=["Trading"])


def get_bot_instance(bot_config: BotConfigModel) -> BasicBot:
    """Create a bot instance from bot config."""
    return BasicBot(
        api_key=bot_config.api_key,
        api_secret=bot_config.api_secret,
        testnet=bot_config.is_testnet
    )


def get_default_bot_config(user_id: int, db: Session) -> Optional[BotConfigModel]:
    """Get the default (first active) bot config for a user."""
    return db.query(BotConfigModel).filter(
        BotConfigModel.user_id == user_id,
        BotConfigModel.is_active == True
    ).first()


@router.post("/execute", response_model=OrderResponse)
def execute_order(
    order: OrderRequest,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Execute a trading order."""
    logger.info(f"Order execution request from user {current_user.username}: {order.dict()}")
    
    try:
        # Get bot config
        if order.bot_config_id:
            bot_config = db.query(BotConfigModel).filter(
                BotConfigModel.id == order.bot_config_id,
                BotConfigModel.user_id == current_user.id
            ).first()
            
            if not bot_config:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Bot configuration not found"
                )
        else:
            bot_config = get_default_bot_config(current_user.id, db)
            
            if not bot_config:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No bot configuration found. Please create one first."
                )
        
        if not bot_config.is_active:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Bot configuration is not active"
            )
        
        # Create trade record
        trade = TradeModel(
            user_id=current_user.id,
            bot_config_id=bot_config.id,
            symbol=order.symbol.upper(),
            side=order.side,
            order_type=order.order_type,
            quantity=order.quantity,
            price=order.price,
            stop_price=order.stop_price,
            status=OrderStatus.PENDING
        )
        db.add(trade)
        db.commit()
        db.refresh(trade)
        
        # Initialize bot and execute order
        bot = get_bot_instance(bot_config)
        
        result = None
        if order.order_type == OrderType.MARKET:
            result = bot.place_market_order(
                symbol=order.symbol.upper(),
                side=order.side.value,
                quantity=order.quantity
            )
        elif order.order_type == OrderType.LIMIT:
            if not order.price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Price is required for limit orders"
                )
            result = bot.place_limit_order(
                symbol=order.symbol.upper(),
                side=order.side.value,
                quantity=order.quantity,
                price=order.price
            )
        elif order.order_type == OrderType.STOP_LIMIT:
            if not order.stop_price or not order.price:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Both stop_price and price are required for stop-limit orders"
                )
            result = bot.place_stop_limit_order(
                symbol=order.symbol.upper(),
                side=order.side.value,
                quantity=order.quantity,
                stop_price=order.stop_price,
                limit_price=order.price
            )
        
        # Update trade record with result
        if result.get('success'):
            trade.status = OrderStatus.FILLED if order.order_type == OrderType.MARKET else OrderStatus.PENDING
            trade.binance_order_id = str(result.get('order_id'))
            trade.executed_quantity = float(result.get('quantity', 0))
            if 'price' in result and result['price'] != 'N/A':
                trade.price = float(result['price'])
        else:
            trade.status = OrderStatus.FAILED
            trade.error_message = result.get('error', 'Unknown error')
        
        db.commit()
        db.refresh(trade)
        
        return OrderResponse(
            success=result.get('success', False),
            trade_id=trade.id,
            order_id=result.get('order_id'),
            message="Order executed successfully" if result.get('success') else "Order failed",
            error=result.get('error'),
            details=result
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error executing order: {str(e)}")
        # Update trade status to failed if it was created
        if 'trade' in locals():
            trade.status = OrderStatus.FAILED
            trade.error_message = str(e)
            db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error executing order: {str(e)}"
        )


@router.get("/trades", response_model=List[Trade])
def get_trades(
    skip: int = 0,
    limit: int = 100,
    symbol: Optional[str] = None,
    status: Optional[OrderStatus] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's trade history."""
    query = db.query(TradeModel).filter(TradeModel.user_id == current_user.id)
    
    if symbol:
        query = query.filter(TradeModel.symbol == symbol.upper())
    
    if status:
        query = query.filter(TradeModel.status == status)
    
    trades = query.order_by(TradeModel.created_at.desc()).offset(skip).limit(limit).all()
    return trades


@router.get("/trades/{trade_id}", response_model=Trade)
def get_trade(
    trade_id: int,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific trade."""
    trade = db.query(TradeModel).filter(
        TradeModel.id == trade_id,
        TradeModel.user_id == current_user.id
    ).first()
    
    if not trade:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trade not found"
        )
    
    return trade


@router.get("/balance", response_model=AccountBalance)
def get_balance(
    bot_config_id: Optional[int] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get account balance."""
    try:
        # Get bot config
        if bot_config_id:
            bot_config = db.query(BotConfigModel).filter(
                BotConfigModel.id == bot_config_id,
                BotConfigModel.user_id == current_user.id
            ).first()
        else:
            bot_config = get_default_bot_config(current_user.id, db)
        
        if not bot_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot configuration not found"
            )
        
        # Get balance
        bot = get_bot_instance(bot_config)
        balance = bot.get_account_balance()
        
        return AccountBalance(**balance)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching balance: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching balance: {str(e)}"
        )


@router.get("/price/{symbol}")
def get_price(
    symbol: str,
    bot_config_id: Optional[int] = None,
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current price for a symbol."""
    try:
        # Get bot config
        if bot_config_id:
            bot_config = db.query(BotConfigModel).filter(
                BotConfigModel.id == bot_config_id,
                BotConfigModel.user_id == current_user.id
            ).first()
        else:
            bot_config = get_default_bot_config(current_user.id, db)
        
        if not bot_config:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Bot configuration not found"
            )
        
        # Get price
        bot = get_bot_instance(bot_config)
        price = bot.get_current_price(symbol.upper())
        
        if price is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Price not found for {symbol}"
            )
        
        return {"symbol": symbol.upper(), "price": price}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching price: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching price: {str(e)}"
        )


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    current_user: UserModel = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get dashboard statistics."""
    try:
        total_trades = db.query(TradeModel).filter(
            TradeModel.user_id == current_user.id
        ).count()
        
        successful_trades = db.query(TradeModel).filter(
            TradeModel.user_id == current_user.id,
            TradeModel.status == OrderStatus.FILLED
        ).count()
        
        failed_trades = db.query(TradeModel).filter(
            TradeModel.user_id == current_user.id,
            TradeModel.status == OrderStatus.FAILED
        ).count()
        
        pending_trades = db.query(TradeModel).filter(
            TradeModel.user_id == current_user.id,
            TradeModel.status == OrderStatus.PENDING
        ).count()
        
        active_bot_configs = db.query(BotConfigModel).filter(
            BotConfigModel.user_id == current_user.id,
            BotConfigModel.is_active == True
        ).count()
        
        return DashboardStats(
            total_trades=total_trades,
            successful_trades=successful_trades,
            failed_trades=failed_trades,
            pending_trades=pending_trades,
            total_profit=0.0,  # This would require calculating P&L
            active_bot_configs=active_bot_configs
        )
        
    except Exception as e:
        logger.error(f"Error fetching dashboard stats: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching dashboard stats: {str(e)}"
        )
