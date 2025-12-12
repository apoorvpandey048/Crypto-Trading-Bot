from pydantic import BaseModel, EmailStr, Field, field_validator, ConfigDict
from typing import Optional, List
from datetime import datetime
from enum import Enum


# Enums
class OrderSide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    MARKET = "MARKET"
    LIMIT = "LIMIT"
    STOP_LIMIT = "STOP_LIMIT"


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=6)


class User(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    created_at: datetime
    
    model_config = ConfigDict(from_attributes=True)


class UserLogin(BaseModel):
    username: str
    password: str


# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    username: Optional[str] = None


# Bot Config Schemas
class BotConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    api_key: str
    api_secret: str
    is_testnet: bool = True
    is_active: bool = True


class BotConfigCreate(BotConfigBase):
    pass


class BotConfigUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    api_key: Optional[str] = None
    api_secret: Optional[str] = None
    is_testnet: Optional[bool] = None
    is_active: Optional[bool] = None


class BotConfig(BotConfigBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# Trade Schemas
class TradeBase(BaseModel):
    symbol: str = Field(..., min_length=1)
    side: OrderSide
    order_type: OrderType
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0)
    stop_price: Optional[float] = Field(None, gt=0)


class TradeCreate(TradeBase):
    bot_config_id: Optional[int] = None


class TradeUpdate(BaseModel):
    status: Optional[OrderStatus] = None
    executed_quantity: Optional[float] = None
    price: Optional[float] = None
    error_message: Optional[str] = None


class Trade(TradeBase):
    id: int
    user_id: int
    bot_config_id: Optional[int]
    binance_order_id: Optional[str]
    status: OrderStatus
    executed_quantity: float
    executed_at: Optional[datetime]
    error_message: Optional[str]
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# Order Execution Schemas
class OrderRequest(BaseModel):
    symbol: str = Field(..., description="Trading pair (e.g., BTCUSDT)")
    side: OrderSide
    order_type: OrderType
    quantity: float = Field(..., gt=0)
    price: Optional[float] = Field(None, gt=0, description="Required for LIMIT orders")
    stop_price: Optional[float] = Field(None, gt=0, description="Required for STOP_LIMIT orders")
    bot_config_id: Optional[int] = Field(None, description="Bot config to use, uses default if not provided")


class OrderResponse(BaseModel):
    success: bool
    trade_id: Optional[int] = None
    order_id: Optional[str] = None
    message: Optional[str] = None
    error: Optional[str] = None
    details: Optional[dict] = None


# Note Schemas (Sample CRUD entity)
class NoteBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: Optional[str] = None
    tags: Optional[str] = None
    is_pinned: bool = False


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = None
    tags: Optional[str] = None
    is_pinned: Optional[bool] = None


class Note(NoteBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    model_config = ConfigDict(from_attributes=True)


# Account Balance Schema
class AccountBalance(BaseModel):
    total_wallet_balance: str
    total_unrealized_profit: str
    total_margin_balance: str
    available_balance: str
    assets: List[dict]


# Dashboard Stats Schema
class DashboardStats(BaseModel):
    total_trades: int
    successful_trades: int
    failed_trades: int
    pending_trades: int
    total_profit: float
    active_bot_configs: int
