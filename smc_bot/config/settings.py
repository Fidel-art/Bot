"""
Configuration Module for XAUUSD SMC/ICT Trading Bot

This module stores all system parameters including:
- Symbol configuration
- Timeframes for multi-timeframe analysis
- Risk management parameters
- Account protection settings

Designed for easy extension to multi-symbol trading in the future.
"""

# ==================== SYMBOL CONFIGURATION ====================

# Primary trading symbol (easily extensible to list for multi-symbol trading)
SYMBOL = "XAUUSD"

# Future extension: Replace with SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD", ...]


# ==================== TIMEFRAMES ====================

# Multi-timeframe analysis hierarchy
TIMEFRAMES = {
    'D1': 'D1',      # Macro market bias
    'H4': 'H4',      # Institutional structure
    'H1': 'H1',      # Trade setup zones
    'M15': 'M15'     # Entry confirmation
}

# Number of candles to fetch for each timeframe
CANDLE_COUNT = {
    'D1': 100,
    'H4': 200,
    'H1': 300,
    'M15': 500
}


# ==================== TRADING PARAMETERS ====================

# Fixed lot size for all trades
LOT_SIZE = 0.001

# Maximum number of concurrent open positions
MAX_OPEN_TRADES = 1

# Minimum risk-reward ratio
MIN_RISK_REWARD = 2.0

# Slippage tolerance in points
SLIPPAGE = 10

# Magic number for bot identification
MAGIC_NUMBER = 234567


# ==================== RISK MANAGEMENT ====================

# Maximum account drawdown percentage (CRITICAL PROTECTION)
MAX_DRAWDOWN_PERCENT = 5.0

# Risk per trade as percentage of balance
RISK_PER_TRADE_PERCENT = 1.0

# Stop loss buffer in points (beyond key levels)
SL_BUFFER_POINTS = 10

# Take profit multiplier based on risk
TP_MULTIPLIER = 2.0


# ==================== ACCOUNT PROTECTION ====================

# Lock file to prevent trading after max drawdown breach
DRAWDOWN_LOCK_FILE = "drawdown_lock.txt"

# Flag to enable/disable drawdown protection
ENABLE_DRAWDOWN_PROTECTION = True


# ==================== SMC/ICT PARAMETERS ====================

# Minimum structure swing points for trend determination
MIN_SWING_POINTS = 3

# Order block validity period (in candles)
ORDER_BLOCK_VALIDITY = 20

# Fair Value Gap minimum size in points
FVG_MIN_SIZE = 50

# Liquidity sweep tolerance in points
LIQUIDITY_SWEEP_TOLERANCE = 20


# ==================== SESSION FILTERS ====================

# Trading sessions (UTC time)
TRADING_SESSIONS = {
    'LONDON': {'start': 8, 'end': 12},
    'NEW_YORK': {'start': 13, 'end': 17},
    'ASIAN': {'start': 0, 'end': 4}
}

# Enable session-based filtering
ENABLE_SESSION_FILTER = True

# Preferred sessions for entry
PREFERRED_SESSIONS = ['LONDON', 'NEW_YORK']


# ==================== EXECUTION SETTINGS ====================

# Order execution type
ORDER_TYPE = "MARKET"  # MARKET or PENDING

# Order filling mode
ORDER_FILLING = "FOK"  # FOK (Fill or Kill) or IOC (Immediate or Cancel)

# Retry attempts for failed orders
MAX_RETRY_ATTEMPTS = 3

# Delay between retry attempts (seconds)
RETRY_DELAY = 2


# ==================== LOGGING CONFIGURATION ====================

# Log file path
LOG_FILE = "logs/trading_bot.log"

# Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
LOG_LEVEL = "INFO"

# Enable console logging
ENABLE_CONSOLE_LOG = True


# ==================== MT5 CONNECTION ====================

# MT5 connection timeout (seconds)
MT5_TIMEOUT = 60

# Reconnection attempts on failure
MT5_RECONNECT_ATTEMPTS = 5

# Delay between reconnection attempts (seconds)
MT5_RECONNECT_DELAY = 10


# ==================== BACKTESTING MODE ====================

# Enable backtesting mode (uses historical data only)
BACKTESTING_MODE = False

# Backtesting date range
BACKTEST_START_DATE = "2023-01-01"
BACKTEST_END_DATE = "2023-12-31"


# ==================== NOTIFICATION SETTINGS ====================

# Enable trade notifications
ENABLE_NOTIFICATIONS = False

# Notification methods (future implementation)
NOTIFICATION_METHODS = ['EMAIL', 'TELEGRAM']


# ==================== VALIDATION ====================

def validate_settings():
    """
    Validates critical configuration parameters.
    Raises ValueError if any setting is invalid.
    """
    if MAX_DRAWDOWN_PERCENT <= 0 or MAX_DRAWDOWN_PERCENT > 100:
        raise ValueError("MAX_DRAWDOWN_PERCENT must be between 0 and 100")
    
    if RISK_PER_TRADE_PERCENT <= 0 or RISK_PER_TRADE_PERCENT > MAX_DRAWDOWN_PERCENT:
        raise ValueError(f"RISK_PER_TRADE_PERCENT must be between 0 and {MAX_DRAWDOWN_PERCENT}")
    
    if LOT_SIZE <= 0:
        raise ValueError("LOT_SIZE must be positive")
    
    if MIN_RISK_REWARD < 1:
        raise ValueError("MIN_RISK_REWARD must be at least 1")
    
    if MAX_OPEN_TRADES < 1:
        raise ValueError("MAX_OPEN_TRADES must be at least 1")
    
    return True


# Validate settings on module import
validate_settings()
