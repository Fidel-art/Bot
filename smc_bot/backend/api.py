"""
FastAPI Web Dashboard for SMC Trading Bot

REST API Endpoints:
- Authentication (login, logout, register)
- Subscription management
- Bot control (start, stop, pause)
- Trading data (positions, history, analytics)
- Configuration management
"""

from fastapi import FastAPI, HTTPException, Depends, status, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import uvicorn
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import backend modules
from backend.auth import get_auth_manager, is_token_blacklisted, blacklist_token
from database.db import get_db_manager
from backend.bot_controller import get_bot_controller


# Initialize FastAPI app
app = FastAPI(
    title="SMC Trading Bot Dashboard API",
    description="REST API for managing SMC/ICT trading bot",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get managers
auth_manager = get_auth_manager()
db_manager = get_db_manager()
bot_controller = get_bot_controller()


# ==================== REQUEST/RESPONSE MODELS ====================

class RegisterRequest(BaseModel):
    """Registration request model."""
    trader_id: str
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    """Login request model."""
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    """Token response model."""
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int

class BotConfigRequest(BaseModel):
    """Bot configuration request."""
    mt5_login: int
    mt5_server: str
    mt5_password: str  # Not stored in DB, only used for connection
    lot_size: float = 0.01
    risk_per_trade: float = 1.0
    max_drawdown: float = 5.0
    max_trades_per_day: int = 3
    symbols: List[str] = ["XAUUSD"]
    timeframes: List[str] = ["D1", "H4", "H1", "M15"]

class SubscriptionRequest(BaseModel):
    """Subscription creation request."""
    plan: str  # free, monthly, quarterly, vip
    payment_method: Optional[str] = None

class BotControlRequest(BaseModel):
    """Bot control request."""
    action: str  # start, stop, pause, resume


# ==================== AUTHENTICATION DEPENDENCY ====================

async def get_current_trader(authorization: str = Header(None)) -> str:
    """
    Dependency to extract and validate trader from JWT token.
    
    Args:
        authorization: Authorization header (Bearer token)
        
    Returns:
        Trader ID
        
    Raises:
        HTTPException: If token invalid or missing
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Check if blacklisted
    if is_token_blacklisted(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has been revoked"
        )
    
    # Validate token
    is_valid, trader_id, error = auth_manager.validate_session(token)
    
    if not is_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=error or "Invalid token"
        )
    
    return trader_id


# ==================== AUTHENTICATION ENDPOINTS ====================

@app.post("/api/auth/register", status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """Register new trader account."""
    # Check if trader exists
    existing = db_manager.get_trader(trader_id=request.trader_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Trader ID already exists"
        )
    
    existing_email = db_manager.get_trader(email=request.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash password
    password_hash = auth_manager.hash_password(request.password)
    
    # Create trader
    success = db_manager.create_trader(
        trader_id=request.trader_id,
        email=request.email,
        password_hash=password_hash,
        name=request.name
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create trader account"
        )
    
    # Create free trial subscription (7 days)
    start_date = datetime.now().date()
    expiry_date = start_date + timedelta(days=7)
    
    db_manager.create_subscription(
        trader_id=request.trader_id,
        plan="free_trial",
        start_date=start_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
        amount=0.0
    )
    
    return {
        "success": True,
        "message": "Account created successfully with 7-day free trial",
        "trader_id": request.trader_id
    }

@app.post("/api/auth/login", response_model=TokenResponse)
async def login(request: LoginRequest):
    """Login and get access token."""
    # Get trader by email
    trader = db_manager.get_trader(email=request.email)
    
    if not trader:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not auth_manager.verify_password(request.password, trader['password_hash']):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Check if account active
    if not trader.get('is_active'):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is deactivated"
        )
    
    # Update last login
    db_manager.update_trader_login(trader['trader_id'])
    
    # Create tokens
    tokens = auth_manager.create_login_tokens(
        trader_id=trader['trader_id'],
        trader_data={
            "name": trader['name'],
            "email": trader['email']
        }
    )
    
    return tokens

@app.post("/api/auth/logout")
async def logout(trader_id: str = Depends(get_current_trader), 
                authorization: str = Header(None)):
    """Logout and invalidate token."""
    token = authorization.replace("Bearer ", "")
    blacklist_token(token)
    
    return {"success": True, "message": "Logged out successfully"}

@app.post("/api/auth/refresh")
async def refresh_token(refresh_token: str):
    """Refresh access token using refresh token."""
    new_token = auth_manager.refresh_access_token(refresh_token)
    
    if not new_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return {
        "access_token": new_token,
        "token_type": "bearer"
    }


# ==================== TRADER PROFILE ENDPOINTS ====================

@app.get("/api/profile")
async def get_profile(trader_id: str = Depends(get_current_trader)):
    """Get trader profile."""
    trader = db_manager.get_trader(trader_id=trader_id)
    
    if not trader:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Trader not found"
        )
    
    # Get subscription
    subscription = db_manager.get_active_subscription(trader_id)
    
    # Get bot config
    bot_config = db_manager.get_bot_config(trader_id)
    
    # Remove sensitive data
    trader.pop('password_hash', None)
    
    return {
        "trader": trader,
        "subscription": subscription,
        "bot_config": bot_config
    }


# ==================== SUBSCRIPTION ENDPOINTS ====================

@app.get("/api/subscription")
async def get_subscription(trader_id: str = Depends(get_current_trader)):
    """Get active subscription."""
    subscription = db_manager.get_active_subscription(trader_id)
    
    if not subscription:
        return {
            "has_subscription": False,
            "message": "No active subscription"
        }
    
    # Calculate days remaining
    expiry = datetime.strptime(subscription['expiry_date'], '%Y-%m-%d')
    days_remaining = (expiry - datetime.now()).days
    
    return {
        "has_subscription": True,
        "subscription": subscription,
        "days_remaining": days_remaining,
        "is_valid": days_remaining >= 0
    }

@app.post("/api/subscription/create")
async def create_subscription(request: SubscriptionRequest,
                              trader_id: str = Depends(get_current_trader)):
    """Create new subscription."""
    # Define subscription plans
    plans = {
        "free": {"days": 7, "amount": 0.0},
        "weekly": {"days": 7, "amount": 15.0},
        "monthly": {"days": 30, "amount": 50.0},
        "quarterly": {"days": 90, "amount": 135.0},
        "yearly": {"days": 365, "amount": 500.0}
    }
    
    if request.plan not in plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Choose from: {', '.join(plans.keys())}"
        )
    
    plan_info = plans[request.plan]
    start_date = datetime.now().date()
    expiry_date = start_date + timedelta(days=plan_info['days'])
    
    success = db_manager.create_subscription(
        trader_id=trader_id,
        plan=request.plan,
        start_date=start_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
        amount=plan_info['amount']
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription"
        )
    
    return {
        "success": True,
        "message": f"Subscription created: {request.plan}",
        "expiry_date": expiry_date.isoformat(),
        "amount": plan_info['amount']
    }


# ==================== BOT CONFIGURATION ENDPOINTS ====================

@app.post("/api/config/save")
async def save_config(config: BotConfigRequest,
                     trader_id: str = Depends(get_current_trader)):
    """Save bot configuration."""
    config_dict = config.dict()
    config_dict.pop('mt5_password')  # Don't store password
    
    success = db_manager.save_bot_config(trader_id, config_dict)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save configuration"
        )
    
    return {
        "success": True,
        "message": "Configuration saved successfully"
    }

@app.get("/api/config")
async def get_config(trader_id: str = Depends(get_current_trader)):
    """Get bot configuration."""
    config = db_manager.get_bot_config(trader_id)
    
    if not config:
        return {
            "has_config": False,
            "message": "No configuration found"
        }
    
    return {
        "has_config": True,
        "config": config
    }


# ==================== BOT CONTROL ENDPOINTS ====================

@app.post("/api/bot/start")
async def start_bot(config: Optional[BotConfigRequest] = None,
                   trader_id: str = Depends(get_current_trader)):
    """Start trading bot."""
    # Check subscription
    subscription = db_manager.get_active_subscription(trader_id)
    if not subscription:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Active subscription required"
        )
    
    # Get config from request or database
    if config is None:
        # Try to get saved config
        saved_config = db_manager.get_bot_config(trader_id)
        if not saved_config:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No bot configuration found. Please configure bot settings first."
            )
        config_dict = saved_config
    else:
        config_dict = config.dict()
    
    # Start bot
    success, message = bot_controller.start_bot(trader_id, config_dict)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }

@app.post("/api/bot/stop")
async def stop_bot(trader_id: str = Depends(get_current_trader)):
    """Stop trading bot."""
    success, message = bot_controller.stop_bot(trader_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }

@app.post("/api/bot/pause")
async def pause_bot(trader_id: str = Depends(get_current_trader)):
    """Pause trading bot."""
    success, message = bot_controller.pause_bot(trader_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }

@app.post("/api/bot/resume")
async def resume_bot(trader_id: str = Depends(get_current_trader)):
    """Resume trading bot."""
    success, message = bot_controller.resume_bot(trader_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }

@app.get("/api/bot/status")
async def get_bot_status(trader_id: str = Depends(get_current_trader)):
    """Get bot status."""
    status_data = bot_controller.get_bot_status(trader_id)
    
    if not status_data:
        return {
            "is_running": False,
            "status": None,
            "message": "Bot is not running"
        }
    
    # Return status in the format the frontend expects
    return {
        "is_running": status_data.get("is_alive", False),
        "status": status_data.get("status", "stopped"),
        "uptime": status_data.get("uptime_seconds", 0),
        "active_trades": status_data.get("trades_count", 0),
        "daily_pnl": status_data.get("profit", 0.0),
        "start_time": status_data.get("start_time"),
        "message": f"Bot is {status_data.get('status', 'stopped')}"
    }


# ==================== TRADING DATA ENDPOINTS ====================

@app.get("/api/trades/history")
async def get_trade_history(trader_id: str = Depends(get_current_trader),
                           limit: int = 100):
    """Get trade history."""
    trades = db_manager.get_trades(trader_id, limit)
    
    return {
        "trades": trades,
        "count": len(trades)
    }

@app.get("/api/trades/statistics")
async def get_statistics(trader_id: str = Depends(get_current_trader)):
    """Get performance statistics."""
    stats = db_manager.get_performance_stats(trader_id)
    
    return {"statistics": stats}


# ==================== SYSTEM ENDPOINTS ====================

@app.get("/api/system/health")
async def system_health():
    """Get system health metrics."""
    health = bot_controller.get_system_health()
    
    return {
        "status": "healthy",
        "metrics": health
    }

@app.get("/api/system/mt5-status")
async def mt5_status():
    """Check if MT5 is running."""
    from bot_controller import is_mt5_running, find_mt5_executable
    
    is_running = is_mt5_running()
    mt5_path = find_mt5_executable()
    
    return {
        "is_running": is_running,
        "mt5_found": mt5_path is not None,
        "mt5_path": mt5_path,
        "status": "connected" if is_running else "disconnected"
    }

@app.post("/api/system/launch-mt5")
async def launch_mt5_endpoint():
    """Launch MetaTrader 5."""
    from bot_controller import launch_mt5
    
    success, message = launch_mt5()
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }

@app.post("/api/system/open-mt5-charts")
async def open_mt5_charts_endpoint(symbol: str = "EURUSD", timeframe: str = "H1"):
    """Open MT5 charts for the specified symbol and timeframe."""
    from bot_controller import open_mt5_charts
    
    success, message = open_mt5_charts(symbol, timeframe)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message
        )
    
    return {
        "success": True,
        "message": message
    }

@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "SMC Trading Bot Dashboard API",
        "version": "1.0.0",
        "status": "running"
    }


# ==================== RUN SERVER ====================

def run_server(host: str = "0.0.0.0", port: int = 8000):
    """
    Run the FastAPI server.
    
    Args:
        host: Host address
        port: Port number
    """
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_server(port=8001)
