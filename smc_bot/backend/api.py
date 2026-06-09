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
import json
import time
import threading
import logging
try:
    import MetaTrader5 as mt5
except ImportError:
    mt5 = None  # MT5 is Windows-only; API server can still start for non-MT5 endpoints
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import backend modules
from backend.auth import get_auth_manager, is_token_blacklisted, blacklist_token
from database.db import get_db_manager
from backend.bot_controller import (
    get_bot_controller,
    is_mt5_running,
    find_mt5_executable,
    launch_mt5,
    open_mt5_charts,
)


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
mt5_trade_lock = threading.Lock()
mt5_session_state = {
    "initialized": False,
    "logged_in_account": None,
}
logger = logging.getLogger(__name__)


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
    symbols: List[str] = ["XAUUSD", "EURUSD", "GBPUSD", "USDJPY", "AUDUSD", "USDCAD", "NZDUSD", "EURJPY", "GBPJPY", "EURGBP"]
    timeframes: List[str] = ["D1", "H4", "H1", "M15"]

class SubscriptionRequest(BaseModel):
    """Subscription creation request."""
    plan: str  # free, weekly, monthly, quarterly, yearly
    payment_method: Optional[str] = None
    payment_details: Optional[str] = None

class PaymentRequest(BaseModel):
    """Payment processing request."""
    plan: str
    payment_method: str  # paypal, mpesa, card
    payment_details: Optional[str] = None

class BotControlRequest(BaseModel):
    """Bot control request."""
    action: str  # start, stop, pause, resume

class InstantTradeRequest(BaseModel):
    """Instant execution trade request."""
    symbol: str
    side: str  # BUY or SELL
    risk_per_trade: float


def _load_trader_mt5_credentials(trader_id: str) -> Dict[str, Any]:
    """Load trader MT5 credentials from saved config and secrets."""
    config = db_manager.get_bot_config(trader_id)
    if not config:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No bot configuration found. Please complete bot setup first."
        )

    secrets_file = Path("config/trader_configs") / f"{trader_id}_secrets.json"
    if not secrets_file.exists():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MT5 password not found. Please re-enter your MT5 credentials in bot setup."
        )

    try:
        with open(secrets_file, 'r', encoding='utf-8') as f:
            secrets = json.load(f)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to read MT5 secrets: {str(exc)}"
        )

    mt5_password = secrets.get("mt5_password")
    if not mt5_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MT5 password is empty. Please update your MT5 credentials."
        )

    return {
        "mt5_login": config.get("mt5_login"),
        "mt5_server": config.get("mt5_server"),
        "mt5_password": mt5_password,
    }


def _load_trader_mt5_credentials_optional(trader_id: str) -> Optional[Dict[str, Any]]:
    """Best-effort MT5 credential load; returns None if setup is not completed."""
    try:
        return _load_trader_mt5_credentials(trader_id)
    except HTTPException as exc:
        if exc.status_code in [400, 404]:
            return None
        raise


def _normalize_lot_for_symbol(symbol_info, lot: float) -> float:
    """Normalize lot size based on symbol constraints."""
    min_lot = float(symbol_info.volume_min)
    max_lot = float(symbol_info.volume_max)
    step = float(symbol_info.volume_step) if float(symbol_info.volume_step) > 0 else 0.01

    bounded = max(min_lot, min(max_lot, lot))
    normalized = round(bounded / step) * step
    return round(normalized, 2)


def _calculate_lot_by_risk(account_balance: float,
                           risk_percent: float,
                           entry_price: float,
                           stop_loss_price: float,
                           symbol_info) -> float:
    """Calculate lot size from risk percent and SL distance."""
    risk_amount = account_balance * (risk_percent / 100.0)
    sl_distance = abs(entry_price - stop_loss_price)
    if sl_distance <= 0:
        return float(symbol_info.volume_min)

    tick_size = float(symbol_info.trade_tick_size or 0)
    tick_value = float(symbol_info.trade_tick_value or 0)
    if tick_size <= 0 or tick_value <= 0:
        return float(symbol_info.volume_min)

    value_per_price_unit = tick_value / tick_size
    risk_per_lot = sl_distance * value_per_price_unit
    if risk_per_lot <= 0:
        return float(symbol_info.volume_min)

    raw_lot = risk_amount / risk_per_lot
    return _normalize_lot_for_symbol(symbol_info, raw_lot)


def _initialize_mt5_with_retry(max_attempts: int = 2) -> tuple[bool, Any]:
    """Initialize MT5 robustly to avoid transient IPC timeout errors."""
    if mt5 is None:
        return False, "MetaTrader5 is not available in this environment (Windows-only library)"
    last_error = None
    mt5_path = find_mt5_executable()

    if not is_mt5_running():
        launch_mt5()
        time.sleep(4)

    for attempt in range(max_attempts):
        init_ok = False

        # Reset any stale IPC state first
        try:
            mt5.shutdown()
        except Exception:
            pass

        try:
            # First try to attach to currently running/last-used terminal (best for live opened MT5)
            init_ok = mt5.initialize(timeout=10000)
        except TypeError:
            init_ok = mt5.initialize(timeout=10000)

        # Fallback: explicit executable path
        if not init_ok and mt5_path:
            try:
                init_ok = mt5.initialize(path=mt5_path, timeout=10000)
            except TypeError:
                init_ok = mt5.initialize(path=mt5_path)

        if init_ok:
            mt5_session_state["initialized"] = True
            return True, None

        last_error = mt5.last_error()
        logger.warning(f"MT5 initialize attempt {attempt + 1}/{max_attempts} failed: {last_error}")

        if attempt == 1:
            launch_mt5()
            time.sleep(5)
        else:
            time.sleep(2)

    return False, last_error


def _ensure_mt5_logged_in(credentials: Dict[str, Any]) -> tuple[bool, Any]:
    """Ensure MT5 session is initialized and logged in for the configured account."""
    terminal_info = None
    try:
        terminal_info = mt5.terminal_info()
    except Exception:
        terminal_info = None

    if terminal_info is None:
        init_ok, init_error = _initialize_mt5_with_retry()
        if not init_ok:
            return False, init_error

    current_account = mt5.account_info()
    target_login = int(credentials["mt5_login"])

    if current_account and int(current_account.login) == target_login:
        mt5_session_state["logged_in_account"] = target_login
        return True, None

    login_error = None
    for attempt in range(3):
        if mt5.login(
            login=target_login,
            password=credentials["mt5_password"],
            server=credentials["mt5_server"]
        ):
            mt5_session_state["logged_in_account"] = target_login
            return True, None

        login_error = mt5.last_error()
        logger.warning(f"MT5 login attempt {attempt + 1}/3 failed: {login_error}")

        # Recover from IPC channel instability by reinitializing MT5 bridge
        if isinstance(login_error, tuple) and len(login_error) > 0 and login_error[0] == -10005:
            # If terminal is already logged into the target account, proceed
            active_account = mt5.account_info()
            if active_account and int(active_account.login) == target_login:
                mt5_session_state["logged_in_account"] = target_login
                logger.warning("MT5 login call timed out, but terminal is already on target account; proceeding")
                return True, None

            _initialize_mt5_with_retry(max_attempts=2)

        time.sleep(2)

    active_account = mt5.account_info()
    if active_account and int(active_account.login) != target_login:
        return False, f"Terminal logged into {active_account.login}, but bot config expects {target_login}"

    return False, login_error


def _sync_trader_trades_with_mt5(trader_id: str) -> None:
    """Sync DB trades with MT5 positions/history. Creates DB records for MT5 trades not yet tracked."""
    credentials = _load_trader_mt5_credentials_optional(trader_id)

    with mt5_trade_lock:
        if credentials:
            mt5_ok, _ = _ensure_mt5_logged_in(credentials)
        else:
            mt5_ok, _ = _initialize_mt5_with_retry(max_attempts=2)
            if mt5_ok:
                active_account = mt5.account_info()
                if active_account is None:
                    mt5_ok = False

        if not mt5_ok:
            return

        try:
            positions = mt5.positions_get() or []
            now = datetime.now()
            from_date = now - timedelta(days=365)
            deals = mt5.history_deals_get(from_date, now) or []

            # Build maps
            position_by_ticket = {int(p.ticket): p for p in positions if hasattr(p, 'ticket')}
            db_open_trades = db_manager.get_open_trades(trader_id)
            # Track ALL existing trade tickets (open + closed) to prevent duplicates
            db_tickets = db_manager.get_all_trade_tickets(trader_id)

            # 1) Update existing open trades (floating P&L) and close if gone
            for trade in db_open_trades:
                ticket = int(trade.get('ticket') or 0)
                if not ticket:
                    continue

                live_position = position_by_ticket.get(ticket)

                if live_position:
                    db_manager.update_trade_open_profit(
                        trader_id=trader_id,
                        ticket=ticket,
                        profit=float(getattr(live_position, 'profit', 0.0))
                    )
                    continue

                # Not in MT5 open positions — find close deals
                related_deals = [
                    d for d in deals
                    if int(getattr(d, 'position_id', 0) or 0) == ticket
                    or int(getattr(d, 'order', 0) or 0) == ticket
                ]

                if related_deals:
                    last_deal = related_deals[-1]
                    final_profit = sum(float(getattr(d, 'profit', 0.0) or 0.0) for d in related_deals)
                    exit_price = float(getattr(last_deal, 'price', 0.0) or 0.0)
                else:
                    final_profit = float(trade.get('profit') or 0.0)
                    exit_price = float(trade.get('entry_price') or 0.0)

                db_manager.close_trade(
                    trader_id=trader_id,
                    ticket=ticket,
                    exit_price=exit_price,
                    profit=final_profit,
                    exit_time=now.isoformat()
                )

            # 2) Import MT5 open positions not yet tracked in DB
            for pos in positions:
                ticket = int(getattr(pos, 'ticket', 0))
                if not ticket or ticket in db_tickets:
                    continue
                pos_type = 'BUY' if int(getattr(pos, 'type', 0)) == 0 else 'SELL'
                db_manager.save_trade(trader_id, {
                    'ticket': ticket,
                    'signal': pos_type,
                    'symbol': str(getattr(pos, 'symbol', '')),
                    'entry_price': float(getattr(pos, 'price_open', 0.0)),
                    'stop_loss': float(getattr(pos, 'sl', 0.0)),
                    'take_profit': float(getattr(pos, 'tp', 0.0)),
                    'lot_size': float(getattr(pos, 'volume', 0.0)),
                    'profit': float(getattr(pos, 'profit', 0.0)),
                    'entry_time': datetime.fromtimestamp(int(getattr(pos, 'time', 0))).isoformat(),
                    'exit_time': None,
                    'status': 'open',
                    'risk_reward': 0.0,
                })
                db_tickets.add(ticket)

            # 3) Import recently closed MT5 positions not yet tracked in DB
            closed_deals: dict = {}
            for deal in deals:
                pos_id = int(getattr(deal, 'position_id', 0) or 0)
                if not pos_id or pos_id in db_tickets:
                    continue
                deal_type = int(getattr(deal, 'type', -1) or -1)
                entry = int(getattr(deal, 'entry', -1) or -1)
                if deal_type not in {0, 1}:  # DEAL_TYPE_BUY, DEAL_TYPE_SELL
                    continue
                if entry in {1, 2}:  # DEAL_ENTRY_OUT, DEAL_ENTRY_OUT_BY
                    if pos_id not in closed_deals:
                        closed_deals[pos_id] = []
                    closed_deals[pos_id].append(deal)

            for pos_id, exit_deals in closed_deals.items():
                if pos_id in db_tickets:
                    continue
                # Find entry deal for this position - try multiple strategies
                entry_deal = None
                # Strategy 1: match by position_id and entry type 0
                entry_deals = [
                    d for d in deals
                    if int(getattr(d, 'position_id', 0) or 0) == pos_id
                    and int(getattr(d, 'entry', -1) or -1) in {0}
                ]
                if entry_deals:
                    entry_deal = entry_deals[0]
                else:
                    # Strategy 2: match by order or ticket
                    first_exit = exit_deals[0]
                    exit_order = int(getattr(first_exit, 'order', 0) or 0)
                    entry_deals = [
                        d for d in deals
                        if int(getattr(d, 'order', 0) or 0) == exit_order
                        and int(getattr(d, 'entry', -1) or -1) in {0}
                    ]
                    if entry_deals:
                        entry_deal = entry_deals[0]
                    else:
                        # Strategy 3: sort all deals for this position by time, first is entry
                        all_pos_deals = sorted(
                            [d for d in deals if int(getattr(d, 'position_id', 0) or 0) == pos_id],
                            key=lambda d: int(getattr(d, 'time', 0) or 0)
                        )
                        if all_pos_deals:
                            entry_deal = all_pos_deals[0]

                last_exit = exit_deals[-1]
                side = 'SELL'
                if entry_deal:
                    entry_type = int(getattr(entry_deal, 'type', -1) or -1)
                    if entry_type == 0:
                        side = 'BUY'
                    elif entry_type == 1:
                        side = 'SELL'
                total_profit = sum(float(getattr(d, 'profit', 0.0) or 0.0) for d in exit_deals)
                # Determine exit reason from last exit deal
                exit_reason = int(getattr(last_exit, 'reason', 0) or 0)
                if exit_reason == 2:
                    notes = 'TP Hit'
                elif exit_reason == 3:
                    notes = 'SL Hit'
                elif exit_reason == 1:
                    notes = 'Manual Close'
                elif exit_reason == 4:
                    notes = 'Stop Out'
                else:
                    notes = 'Closed'
                db_manager.save_trade(trader_id, {
                    'ticket': pos_id,
                    'signal': side,
                    'symbol': str(getattr(last_exit, 'symbol', '')),
                    'entry_price': float(getattr(entry_deal, 'price', 0.0)) if entry_deal else float(getattr(last_exit, 'price', 0.0)),
                    'exit_price': float(getattr(last_exit, 'price', 0.0)),
                    'stop_loss': float(getattr(entry_deal, 'sl', 0.0)) if entry_deal else 0.0,
                    'take_profit': float(getattr(entry_deal, 'tp', 0.0)) if entry_deal else 0.0,
                    'lot_size': float(getattr(entry_deal, 'volume', 0.0)) if entry_deal else float(getattr(last_exit, 'volume', 0.0)),
                    'profit': total_profit,
                    'commission': sum(float(getattr(d, 'commission', 0.0) or 0.0) for d in exit_deals + ([entry_deal] if entry_deal else [])),
                    'swap': sum(float(getattr(d, 'swap', 0.0) or 0.0) for d in exit_deals + ([entry_deal] if entry_deal else [])),
                    'entry_time': datetime.fromtimestamp(int(getattr(entry_deal, 'time', 0))).isoformat() if entry_deal else datetime.fromtimestamp(int(getattr(last_exit, 'time', 0))).isoformat(),
                    'exit_time': datetime.fromtimestamp(int(getattr(last_exit, 'time', 0))).isoformat(),
                    'status': 'closed',
                    'risk_reward': 0.0,
                    'notes': notes,
                })
        finally:
            try:
                mt5.shutdown()
            except Exception:
                pass


def _get_mt5_statistics_for_trader(trader_id: str) -> Optional[Dict[str, Any]]:
    """Compute live trader statistics directly from MT5 deals/positions."""
    credentials = _load_trader_mt5_credentials_optional(trader_id)

    with mt5_trade_lock:
        if credentials:
            mt5_ok, _ = _ensure_mt5_logged_in(credentials)
        else:
            mt5_ok, _ = _initialize_mt5_with_retry(max_attempts=2)

            if mt5_ok:
                active_account = mt5.account_info()
                if active_account is None:
                    mt5_ok = False

        if not mt5_ok:
            return None

        now = datetime.now()
        from_date = now - timedelta(days=365)
        deals = mt5.history_deals_get(from_date, now) or []

        out_entries = {
            int(getattr(mt5, 'DEAL_ENTRY_OUT', 1)),
            int(getattr(mt5, 'DEAL_ENTRY_OUT_BY', 3)),
        }
        in_entries = {
            int(getattr(mt5, 'DEAL_ENTRY_IN', 0)),
            int(getattr(mt5, 'DEAL_ENTRY_INOUT', 2)),
        }
        trade_types = {
            int(getattr(mt5, 'DEAL_TYPE_BUY', 0)),
            int(getattr(mt5, 'DEAL_TYPE_SELL', 1)),
        }

        all_position_ids = set()
        closed_position_ids = set()
        profit_by_position: Dict[int, float] = {}
        reason_by_position: Dict[int, str] = {}
        considered_deals = 0

        for deal in deals:
            symbol = str(getattr(deal, 'symbol', '') or '')
            if not symbol:
                continue

            entry_type = int(getattr(deal, 'entry', -1) or -1)
            deal_type = int(getattr(deal, 'type', -1) or -1)
            if deal_type not in trade_types:
                continue

            considered_deals += 1

            position_id = int(getattr(deal, 'position_id', 0) or 0)
            if position_id:
                all_position_ids.add(position_id)

            deal_profit = float(getattr(deal, 'profit', 0.0) or 0.0)

            if entry_type in out_entries and position_id:
                closed_position_ids.add(position_id)
                profit_by_position[position_id] = profit_by_position.get(position_id, 0.0) + deal_profit
                deal_reason = int(getattr(deal, 'reason', 0) or 0)
                if deal_reason == 2:
                    reason_by_position[position_id] = 'TP'
                elif deal_reason == 3:
                    reason_by_position[position_id] = 'SL'
                elif deal_reason == 1:
                    reason_by_position.setdefault(position_id, 'Manual')
                elif deal_reason == 4:
                    reason_by_position.setdefault(position_id, 'StopOut')
                else:
                    reason_by_position.setdefault(position_id, 'Closed')
            elif entry_type in out_entries and not position_id:
                synthetic_id = int(getattr(deal, 'order', 0) or getattr(deal, 'ticket', 0) or 0)
                if synthetic_id:
                    all_position_ids.add(synthetic_id)
                    closed_position_ids.add(synthetic_id)
                    profit_by_position[synthetic_id] = profit_by_position.get(synthetic_id, 0.0) + deal_profit
            elif abs(deal_profit) > 0:
                synthetic_id = int(position_id or getattr(deal, 'order', 0) or getattr(deal, 'ticket', 0) or 0)
                if synthetic_id:
                    all_position_ids.add(synthetic_id)
                    closed_position_ids.add(synthetic_id)
                    profit_by_position[synthetic_id] = profit_by_position.get(synthetic_id, 0.0) + deal_profit

        positions = mt5.positions_get() or []
        open_positions = [pos for pos in positions]

        closed_profits = list(profit_by_position.values())
        closed_count = len(closed_position_ids)

        total_trades_from_history = len(all_position_ids)
        open_count = len(open_positions)

        wins = [profit for profit in closed_profits if profit > 0]
        losses = [profit for profit in closed_profits if profit < 0]

        total_pnl = sum(closed_profits)
        avg_profit = (total_pnl / closed_count) if closed_count else 0.0
        win_rate = (len(wins) / closed_count * 100.0) if closed_count else 0.0

        total_trades = max(total_trades_from_history, closed_count + open_count)

        return {
            'total_trades': total_trades,
            'open_trades': open_count,
            'closed_trades': closed_count,
            'winning_trades': len(wins),
            'losing_trades': len(losses),
            'win_rate': win_rate,
            'total_profit': total_pnl,
            'total_pnl': total_pnl,
            'average_profit': avg_profit,
            'avg_profit': avg_profit,
            'best_trade': max(closed_profits) if closed_profits else 0.0,
            'worst_trade': min(closed_profits) if closed_profits else 0.0,
            'profit_factor': (sum(wins) / abs(sum(losses))) if losses else 0.0,
            'source': 'mt5',
            'wins_by_tp': len([pid for pid in closed_position_ids if reason_by_position.get(pid) == 'TP' and profit_by_position.get(pid, 0) > 0]),
            'losses_by_sl': len([pid for pid in closed_position_ids if reason_by_position.get(pid) == 'SL' and profit_by_position.get(pid, 0) < 0]),
            'debug_mt5_total_deals': len(deals),
            'debug_mt5_considered_trade_deals': considered_deals,
            'debug_mt5_closed_positions': closed_count,
        }


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
        "weekly": {"days": 7, "amount": 29.0},
        "monthly": {"days": 30, "amount": 99.0},
        "quarterly": {"days": 90, "amount": 249.0},
        "yearly": {"days": 365, "amount": 799.0}
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
        amount=plan_info['amount'],
        payment_method=request.payment_method,
        payment_details=request.payment_details
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
        "amount": plan_info['amount'],
        "payment_method": request.payment_method
    }


@app.post("/api/subscription/pay")
async def process_payment(request: PaymentRequest,
                          trader_id: str = Depends(get_current_trader)):
    """Process payment and activate subscription."""
    plans = {
        "free": {"days": 7, "amount": 0.0},
        "weekly": {"days": 7, "amount": 29.0},
        "monthly": {"days": 30, "amount": 99.0},
        "quarterly": {"days": 90, "amount": 249.0},
        "yearly": {"days": 365, "amount": 799.0},
        "lifetime": {"days": 36500, "amount": 2499.0}
    }

    if request.plan not in plans:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid plan. Choose from: {', '.join(plans.keys())}"
        )

    valid_methods = ["paypal", "mpesa", "card"]
    if request.payment_method not in valid_methods:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid payment method. Choose from: {', '.join(valid_methods)}"
        )

    plan_info = plans[request.plan]
    start_date = datetime.now().date()
    expiry_date = start_date + timedelta(days=plan_info['days'])

    # Simulate payment processing
    # In production, integrate actual payment gateway:
    # - PayPal: use PayPal REST API SDK
    # - MPesa: use Safaricom MPesa API (Daraja)
    # - Card: use Stripe/PayPal card processing
    payment_reference = f"{request.payment_method.upper()}-{datetime.now().strftime('%Y%m%d%H%M%S')}-{trader_id[:8]}"

    # Activate subscription
    success = db_manager.create_subscription(
        trader_id=trader_id,
        plan=request.plan,
        start_date=start_date.isoformat(),
        expiry_date=expiry_date.isoformat(),
        amount=plan_info['amount'],
        payment_method=request.payment_method,
        payment_details=payment_reference
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create subscription after payment"
        )

    return {
        "success": True,
        "message": f"Payment successful via {request.payment_method.upper()}",
        "plan": request.plan,
        "amount": plan_info['amount'],
        "payment_method": request.payment_method,
        "payment_reference": payment_reference,
        "expiry_date": expiry_date.isoformat()
    }


# ==================== BOT CONFIGURATION ENDPOINTS ====================

@app.post("/api/config/save")
async def save_config(config: BotConfigRequest,
                     trader_id: str = Depends(get_current_trader)):
    """Save bot configuration."""
    config_dict = config.dict()

    # Persist MT5 password separately (outside DB) for bot start operations
    mt5_password = config_dict.get('mt5_password', '')
    if mt5_password:
        secrets_dir = Path("config/trader_configs")
        secrets_dir.mkdir(parents=True, exist_ok=True)
        secrets_file = secrets_dir / f"{trader_id}_secrets.json"
        with open(secrets_file, 'w', encoding='utf-8') as f:
            json.dump({"mt5_password": mt5_password}, f)

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

        # Inject MT5 password from secure per-trader file
        secrets_file = Path("config/trader_configs") / f"{trader_id}_secrets.json"
        if secrets_file.exists():
            try:
                with open(secrets_file, 'r', encoding='utf-8') as f:
                    secrets_data = json.load(f)
                config_dict['mt5_password'] = secrets_data.get('mt5_password', '')
            except Exception:
                config_dict['mt5_password'] = ''
    else:
        config_dict = config.dict()

    # Validate required MT5 credentials before attempting start
    if not config_dict.get('mt5_login') or not config_dict.get('mt5_server') or not config_dict.get('mt5_password'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MT5 credentials are incomplete. Please re-enter your MT5 password in setup before starting the bot."
        )
    
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
    """Get bot status including connection status and selected pairs."""
    status_data = bot_controller.get_bot_status(trader_id)
    
    if not status_data:
        return {
            "is_running": False,
            "status": None,
            "is_connected": False,
            "selected_symbols": [],
            "session_status": "inactive",
            "message": "Bot is not running"
        }
    
    # Check if we're in NYC session
    from datetime import datetime, timezone
    import pytz
    ny_tz = pytz.timezone('America/New_York')
    ny_time = datetime.now(ny_tz)
    session_start = ny_time.replace(hour=3, minute=0, second=0, microsecond=0)
    session_end = ny_time.replace(hour=11, minute=0, second=0, microsecond=0)
    is_session_active = session_start <= ny_time <= session_end
    session_status = "active" if is_session_active else "inactive"
    
    # Return status in the format the frontend expects
    return {
        "is_running": status_data.get("is_alive", False),
        "status": status_data.get("status", "stopped"),
        "is_connected": status_data.get("is_connected", False),
        "selected_symbols": status_data.get("selected_symbols", []),
        "session_status": session_status,
        "session_time": ny_time.strftime("%H:%M NYT"),
        "uptime": status_data.get("uptime_seconds", 0),
        "active_trades": status_data.get("trades_count", 0),
        "daily_pnl": status_data.get("profit", 0.0),
        "start_time": status_data.get("start_time"),
        "message": f"Bot is {status_data.get('status', 'stopped')}" + (f" - Connected to {', '.join(status_data.get('selected_symbols', []))}" if status_data.get("is_connected") else "")
    }


@app.post("/api/bot/instant-trade")
def instant_trade(request: InstantTradeRequest,
                  trader_id: str = Depends(get_current_trader)):
    """Execute an immediate market BUY/SELL order from dashboard input."""
    side = (request.side or "").upper()
    if side not in ["BUY", "SELL"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid side. Use BUY or SELL."
        )

    if request.risk_per_trade <= 0 or request.risk_per_trade > 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="risk_per_trade must be between 0 and 100."
        )

    credentials = _load_trader_mt5_credentials_optional(trader_id)

    with mt5_trade_lock:
        if credentials:
            mt5_ok, mt5_error = _ensure_mt5_logged_in(credentials)
        else:
            mt5_ok, mt5_error = _initialize_mt5_with_retry(max_attempts=2)

            if mt5_ok:
                active_account = mt5.account_info()
                if active_account is None:
                    mt5_ok = False
                    mt5_error = "No active MT5 account session. Please login in MetaTrader 5 first."

        if not mt5_ok:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=(
                    f"MT5 connection failed after retries: {mt5_error}. "
                    "Please ensure MetaTrader 5 is open and reachable, then try again."
                )
            )

        try:
            symbol = request.symbol.upper()
            if not mt5.symbol_select(symbol, True):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Failed to select symbol {symbol}"
                )

            symbol_info = mt5.symbol_info(symbol)
            tick = mt5.symbol_info_tick(symbol)
            account_info = mt5.account_info()

            if symbol_info is None or tick is None or account_info is None:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to fetch symbol, tick, or account info from MT5."
                )

            point = float(symbol_info.point)
            stop_loss_points = 500  # 50 pips for instant execution default
            take_profit_points = 1000  # 100 pips default (2R)

            entry_price = float(tick.ask if side == "BUY" else tick.bid)
            if side == "BUY":
                stop_loss = entry_price - (stop_loss_points * point)
                take_profit = entry_price + (take_profit_points * point)
                order_type = mt5.ORDER_TYPE_BUY
            else:
                stop_loss = entry_price + (stop_loss_points * point)
                take_profit = entry_price - (take_profit_points * point)
                order_type = mt5.ORDER_TYPE_SELL

            lot = _calculate_lot_by_risk(
                account_balance=float(account_info.balance),
                risk_percent=float(request.risk_per_trade),
                entry_price=entry_price,
                stop_loss_price=stop_loss,
                symbol_info=symbol_info,
            )

            request_payload = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": symbol,
                "volume": lot,
                "type": order_type,
                "price": entry_price,
                "sl": round(stop_loss, int(symbol_info.digits)),
                "tp": round(take_profit, int(symbol_info.digits)),
                "deviation": 20,
                "magic": 234567,
                "comment": f"Instant {side} via Dashboard",
                "type_time": mt5.ORDER_TIME_GTC,
            }

            preferred_mode = int(getattr(symbol_info, "filling_mode", mt5.ORDER_FILLING_FOK))
            candidate_modes = [
                preferred_mode,
                mt5.ORDER_FILLING_RETURN,
                mt5.ORDER_FILLING_IOC,
                mt5.ORDER_FILLING_FOK,
            ]

            # preserve order while removing duplicates
            unique_modes = []
            for mode in candidate_modes:
                if mode not in unique_modes:
                    unique_modes.append(mode)

            result = None
            for mode in unique_modes:
                payload = dict(request_payload)
                payload["type_filling"] = mode
                result = mt5.order_send(payload)

                if result is not None and result.retcode == mt5.TRADE_RETCODE_DONE:
                    request_payload = payload
                    break

                if result is None:
                    continue

                # 10030 = unsupported filling mode, try next candidate
                if int(result.retcode) == 10030:
                    logger.warning(f"Filling mode {mode} unsupported for {symbol}, trying next mode")
                    continue

                # For other errors, stop retries and return that specific error
                break

            if result is None or result.retcode != mt5.TRADE_RETCODE_DONE:
                error_comment = result.comment if result else "No result from MT5"
                error_code = result.retcode if result else "N/A"
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Order failed ({error_code}): {error_comment}"
                )

            # Persist open trade record for dashboard history
            db_manager.save_trade(
                trader_id,
                {
                    "ticket": int(result.order),
                    "signal": side,
                    "symbol": symbol,
                    "entry_price": float(result.price),
                    "stop_loss": request_payload["sl"],
                    "take_profit": request_payload["tp"],
                    "lot_size": float(lot),
                    "profit": 0.0,
                    "entry_time": datetime.now().isoformat(),
                    "exit_time": None,
                    "status": "open",
                    "risk_reward": 2.0,
                }
            )

            return {
                "success": True,
                "message": f"{side} order executed instantly",
                "ticket": int(result.order),
                "symbol": symbol,
                "side": side,
                "entry_price": float(result.price),
                "lot_size": float(lot),
                "stop_loss": request_payload["sl"],
                "take_profit": request_payload["tp"],
                "risk_per_trade": float(request.risk_per_trade),
            }

        finally:
            try:
                mt5.shutdown()
            except Exception:
                pass


# ==================== TRADING DATA ENDPOINTS ====================

@app.get("/api/trades/history")
async def get_trade_history(trader_id: str = Depends(get_current_trader),
                           limit: int = 100):
    """Get trade history."""
    _sync_trader_trades_with_mt5(trader_id)
    trades = db_manager.get_trades(trader_id, limit)
    
    return {
        "trades": trades,
        "count": len(trades)
    }

@app.get("/api/trades/statistics")
async def get_statistics(trader_id: str = Depends(get_current_trader)):
    """Get performance statistics."""
    mt5_stats = _get_mt5_statistics_for_trader(trader_id)
    _sync_trader_trades_with_mt5(trader_id)
    db_stats = db_manager.get_performance_stats(trader_id)

    if mt5_stats is not None:
        mt5_has_realized_data = (mt5_stats.get('closed_trades', 0) or 0) > 0
        db_has_realized_data = (db_stats.get('closed_trades', 0) or 0) > 0

        if mt5_has_realized_data or not db_has_realized_data:
            return {"statistics": mt5_stats, "source": "mt5"}

    db_stats['source'] = 'database'
    return {"statistics": db_stats, "source": "database"}


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
    """Check MT5 status via the Bridge (Windows host)."""
    import os
    import platform
    import json
    import urllib.request
    import urllib.error

    bridge_url = os.environ.get("MT5_BRIDGE_URL", "http://host.docker.internal:8765")
    try:
        req = urllib.request.Request(f"{bridge_url}/health", method="GET")
        with urllib.request.urlopen(req, timeout=5) as resp:
            bridge_data = json.loads(resp.read().decode())
            return {
                "is_running": bridge_data.get("status") == "ok",
                "mt5_found": bridge_data.get("mt5_initialized", False),
                "connected": bridge_data.get("connected", False),
                "account": bridge_data.get("account"),
                "server": bridge_data.get("server"),
                "balance": bridge_data.get("balance"),
                "equity": bridge_data.get("equity"),
                "status": "connected" if bridge_data.get("connected") else "disconnected",
                "platform": platform.system().lower(),
                "source": "bridge",
            }
    except Exception as e:
        return {
            "is_running": False,
            "mt5_found": False,
            "status": "bridge_unreachable",
            "platform": platform.system().lower(),
            "error": str(e),
            "note": "Cannot reach MT5 Bridge on Windows host. Ensure mt5_bridge/server.py is running."
        }

@app.post("/api/system/launch-mt5")
async def launch_mt5_endpoint():
    """Launch MetaTrader 5."""
    import platform
    if platform.system() != "Windows":
        return {
            "success": True,
            "message": "MT5 runs on Windows host; ensure it is running there"
        }
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
