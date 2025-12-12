# API Documentation

## Base URL
```
http://localhost:8000
```

## Authentication

All protected endpoints require a JWT token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Endpoints

### Authentication

#### Register User
```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "johndoe",
  "password": "securepassword",
  "full_name": "John Doe" (optional)
}

Response: 201 Created
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Login
```http
POST /api/auth/login
Content-Type: multipart/form-data

username=johndoe
password=securepassword

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/auth/me
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Logout
```http
POST /api/auth/logout
Authorization: Bearer <token>

Response: 200 OK
{
  "message": "Successfully logged out"
}
```

### Trading

#### Execute Order
```http
POST /api/trading/execute
Authorization: Bearer <token>
Content-Type: application/json

{
  "symbol": "BTCUSDT",
  "side": "BUY",           // BUY or SELL
  "order_type": "MARKET",  // MARKET, LIMIT, or STOP_LIMIT
  "quantity": 0.001,
  "price": 30000.00,       // Required for LIMIT and STOP_LIMIT
  "stop_price": 30500.00,  // Required for STOP_LIMIT
  "bot_config_id": 1       // Optional, uses default if not provided
}

Response: 200 OK
{
  "success": true,
  "trade_id": 1,
  "order_id": "12345678",
  "message": "Order executed successfully",
  "details": {...}
}
```

#### Get Trade History
```http
GET /api/trading/trades?skip=0&limit=100&symbol=BTCUSDT&status=FILLED
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "symbol": "BTCUSDT",
    "side": "BUY",
    "order_type": "MARKET",
    "status": "FILLED",
    "quantity": 0.001,
    "executed_quantity": 0.001,
    "price": 30000.00,
    "created_at": "2024-01-01T00:00:00",
    ...
  }
]
```

#### Get Account Balance
```http
GET /api/trading/balance?bot_config_id=1
Authorization: Bearer <token>

Response: 200 OK
{
  "total_wallet_balance": "10000.00",
  "total_unrealized_profit": "0.00",
  "total_margin_balance": "10000.00",
  "available_balance": "10000.00",
  "assets": [
    {
      "asset": "USDT",
      "wallet_balance": "10000.00",
      "available_balance": "10000.00",
      "unrealized_profit": "0.00"
    }
  ]
}
```

#### Get Current Price
```http
GET /api/trading/price/BTCUSDT?bot_config_id=1
Authorization: Bearer <token>

Response: 200 OK
{
  "symbol": "BTCUSDT",
  "price": 30000.00
}
```

#### Get Dashboard Statistics
```http
GET /api/trading/stats
Authorization: Bearer <token>

Response: 200 OK
{
  "total_trades": 100,
  "successful_trades": 85,
  "failed_trades": 5,
  "pending_trades": 10,
  "total_profit": 1234.56,
  "active_bot_configs": 2
}
```

### Bot Configurations

#### List Bot Configurations
```http
GET /api/bot-configs/?skip=0&limit=100
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "user_id": 1,
    "name": "My Trading Bot",
    "api_key": "abc123...",
    "api_secret": "secret123...",
    "is_testnet": true,
    "is_active": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": null
  }
]
```

#### Create Bot Configuration
```http
POST /api/bot-configs/
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Trading Bot",
  "api_key": "your_binance_api_key",
  "api_secret": "your_binance_api_secret",
  "is_testnet": true,
  "is_active": true
}

Response: 201 Created
{
  "id": 1,
  "user_id": 1,
  "name": "My Trading Bot",
  "api_key": "your_binance_api_key",
  "is_testnet": true,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Update Bot Configuration
```http
PUT /api/bot-configs/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "Updated Bot Name",
  "is_active": false
}

Response: 200 OK
{
  "id": 1,
  "name": "Updated Bot Name",
  "is_active": false,
  ...
}
```

#### Delete Bot Configuration
```http
DELETE /api/bot-configs/1
Authorization: Bearer <token>

Response: 204 No Content
```

### Notes

#### List Notes
```http
GET /api/notes/?skip=0&limit=100&search=trading&pinned_only=false
Authorization: Bearer <token>

Response: 200 OK
[
  {
    "id": 1,
    "user_id": 1,
    "title": "Trading Strategy",
    "content": "My trading strategy notes...",
    "tags": "strategy,important",
    "is_pinned": true,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-02T00:00:00"
  }
]
```

#### Create Note
```http
POST /api/notes/
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Trading Strategy",
  "content": "My trading strategy notes...",
  "tags": "strategy,important",
  "is_pinned": false
}

Response: 201 Created
{
  "id": 1,
  "title": "Trading Strategy",
  ...
}
```

#### Update Note
```http
PUT /api/notes/1
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "Updated Title",
  "is_pinned": true
}

Response: 200 OK
{
  "id": 1,
  "title": "Updated Title",
  "is_pinned": true,
  ...
}
```

#### Delete Note
```http
DELETE /api/notes/1
Authorization: Bearer <token>

Response: 204 No Content
```

### User Profile

#### Get Profile
```http
GET /api/users/profile
Authorization: Bearer <token>

Response: 200 OK
{
  "id": 1,
  "email": "user@example.com",
  "username": "johndoe",
  "full_name": "John Doe",
  "is_active": true,
  "is_verified": false,
  "created_at": "2024-01-01T00:00:00"
}
```

#### Update Profile
```http
PUT /api/users/profile
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newemail@example.com",
  "username": "newusername",
  "full_name": "New Name",
  "password": "newpassword" (optional)
}

Response: 200 OK
{
  "id": 1,
  "email": "newemail@example.com",
  "username": "newusername",
  ...
}
```

#### Delete Profile
```http
DELETE /api/users/profile
Authorization: Bearer <token>

Response: 204 No Content
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request
```json
{
  "detail": "Validation error message"
}
```

### 401 Unauthorized
```json
{
  "detail": "Could not validate credentials"
}
```

### 404 Not Found
```json
{
  "detail": "Resource not found"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Internal server error message"
}
```

## Rate Limiting

Currently no rate limiting is implemented. In production, consider:
- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated endpoints

## Postman Collection

A Postman collection is available in the repository for easy API testing.

## Interactive Documentation

Visit `http://localhost:8000/docs` for interactive Swagger UI documentation.
