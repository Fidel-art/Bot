"""
Market Data Module for XAUUSD SMC/ICT Trading Bot

Handles all MT5 data operations:
- MT5 platform initialization and connection
- Multi-timeframe OHLC data retrieval
- Data validation and preprocessing
- Connection management and error handling
"""

import MetaTrader5 as mt5
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import logging
from typing import Dict, Optional, Tuple

from config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MarketDataHandler:
    """
    Handles all interactions with MetaTrader 5 for market data retrieval.
    Implements connection management and multi-timeframe data fetching.
    """
    
    def __init__(self, symbol: str = None):
        """
        Initialize the Market Data Handler.
        
        Args:
            symbol: Trading symbol (default: from settings.SYMBOL)
        """
        self.symbol = symbol or settings.SYMBOL
        self.connected = False
        self.symbol_info = None
        self.mt5_credentials = None
    
    def set_symbol(self, symbol: str) -> bool:
        """Switch to a different symbol and validate it."""
        self.symbol = symbol
        self.symbol_info = None
        return self._validate_symbol()
        
    def initialize_mt5(self, login: Optional[int] = None,
                       password: Optional[str] = None,
                       server: Optional[str] = None) -> bool:
        """
        Initialize connection to MetaTrader 5.
        
        Args:
            login: MT5 account login (optional)
            password: MT5 account password (optional)
            server: MT5 server name (optional)

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"MT5 initialization failed: {error}")
                return False

            if login is not None and password and server:
                if not mt5.login(login=int(login), password=password, server=server):
                    error = mt5.last_error()
                    logger.error(f"MT5 account login failed for account {login} on server '{server}': {error}")
                    return False

                self.mt5_credentials = {
                    'login': int(login),
                    'password': password,
                    'server': server
                }
                logger.info(f"MT5 logged in successfully for account {login} on {server}")
            elif any([login is not None, password, server]):
                logger.warning("Partial MT5 credentials provided; proceeding with current terminal account")
            
            self.connected = True
            logger.info("MT5 initialized successfully")
            
            # Verify symbol availability
            if not self._validate_symbol():
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing MT5: {e}")
            return False
    
    def _validate_symbol(self) -> bool:
        """
        Validate that the trading symbol is available.
        
        Returns:
            bool: True if symbol is valid and available
        """
        try:
            self.symbol_info = mt5.symbol_info(self.symbol)
            
            if self.symbol_info is None:
                logger.error(f"Symbol {self.symbol} not found")
                return False
            
            if not self.symbol_info.visible:
                logger.info(f"Symbol {self.symbol} not visible, attempting to enable")
                if not mt5.symbol_select(self.symbol, True):
                    logger.error(f"Failed to enable symbol {self.symbol}")
                    return False
            
            logger.info(f"Symbol {self.symbol} validated successfully")
            logger.info(f"  Spread: {self.symbol_info.spread}")
            logger.info(f"  Digits: {self.symbol_info.digits}")
            logger.info(f"  Point: {self.symbol_info.point}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error validating symbol: {e}")
            return False
    
    def get_candles(self, timeframe: str, count: int) -> Optional[pd.DataFrame]:
        """
        Fetch OHLC candle data for specified timeframe.
        
        Args:
            timeframe: MT5 timeframe string (D1, H4, H1, M15)
            count: Number of candles to retrieve
            
        Returns:
            DataFrame with columns: time, open, high, low, close, tick_volume
        """
        if not self.connected:
            logger.error("MT5 not connected. Call initialize_mt5() first")
            return None
        
        try:
            # Map timeframe string to MT5 constant
            tf_map = {
                'D1': mt5.TIMEFRAME_D1,
                'H4': mt5.TIMEFRAME_H4,
                'H1': mt5.TIMEFRAME_H1,
                'M15': mt5.TIMEFRAME_M15
            }
            
            if timeframe not in tf_map:
                logger.error(f"Invalid timeframe: {timeframe}")
                return None
            
            mt5_timeframe = tf_map[timeframe]
            
            # Fetch rates
            rates = mt5.copy_rates_from_pos(self.symbol, mt5_timeframe, 0, count)
            
            if rates is None or len(rates) == 0:
                logger.error(f"Failed to fetch {timeframe} data for {self.symbol}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s')
            
            logger.info(f"Fetched {len(df)} {timeframe} candles for {self.symbol}")
            
            return df[['time', 'open', 'high', 'low', 'close', 'tick_volume']]
            
        except Exception as e:
            logger.error(f"Error fetching {timeframe} candles: {e}")
            return None
    
    def get_multi_timeframe_data(self) -> Dict[str, pd.DataFrame]:
        """
        Fetch data for all required timeframes.
        
        Returns:
            Dictionary mapping timeframe to DataFrame
        """
        data = {}
        
        for tf_name, tf_value in settings.TIMEFRAMES.items():
            count = settings.CANDLE_COUNT.get(tf_name, 100)
            df = self.get_candles(tf_value, count)
            
            if df is not None:
                data[tf_name] = df
            else:
                logger.warning(f"Failed to fetch data for {tf_name}")
        
        if len(data) != len(settings.TIMEFRAMES):
            logger.error("Failed to fetch all required timeframes")
            return {}
        
        logger.info(f"Successfully fetched all {len(data)} timeframes")
        return data
    
    def get_current_price(self) -> Optional[Tuple[float, float]]:
        """
        Get current bid and ask price for the symbol.
        
        Returns:
            Tuple of (bid, ask) or None if failed
        """
        if not self.connected:
            logger.error("MT5 not connected")
            return None
        
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            
            if tick is None:
                logger.error(f"Failed to get tick data for {self.symbol}")
                return None
            
            return (tick.bid, tick.ask)
            
        except Exception as e:
            logger.error(f"Error getting current price: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict]:
        """
        Retrieve current account information.
        
        Returns:
            Dictionary with account details or None if failed
        """
        if not self.connected:
            logger.error("MT5 not connected")
            return None
        
        try:
            account = mt5.account_info()
            
            if account is None:
                logger.error("Failed to get account info")
                return None
            
            return {
                'balance': account.balance,
                'equity': account.equity,
                'profit': account.profit,
                'margin': account.margin,
                'free_margin': account.margin_free,
                'margin_level': account.margin_level,
                'currency': account.currency,
                'leverage': account.leverage
            }
            
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_open_positions(self) -> Optional[pd.DataFrame]:
        """
        Get all currently open positions for the symbol.
        
        Returns:
            DataFrame of open positions or None if failed
        """
        if not self.connected:
            logger.error("MT5 not connected")
            return None
        
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            
            if positions is None:
                logger.error("Failed to get positions")
                return None
            
            if len(positions) == 0:
                return pd.DataFrame()  # Return empty DataFrame
            
            # Convert to DataFrame
            df = pd.DataFrame(list(positions), columns=positions[0]._asdict().keys())
            
            logger.info(f"Found {len(df)} open positions for {self.symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error getting open positions: {e}")
            return None
    
    def calculate_swing_points(self, df: pd.DataFrame, lookback: int = 5) -> pd.DataFrame:
        """
        Identify swing highs and swing lows in price data.
        
        Args:
            df: OHLC DataFrame
            lookback: Number of candles to check on each side
            
        Returns:
            DataFrame with swing_high and swing_low columns added
        """
        try:
            df = df.copy()
            df['swing_high'] = False
            df['swing_low'] = False
            
            for i in range(lookback, len(df) - lookback):
                # Check for swing high
                is_swing_high = all(df.loc[i, 'high'] > df.loc[j, 'high'] 
                                   for j in range(i - lookback, i + lookback + 1) if j != i)
                if is_swing_high:
                    df.loc[i, 'swing_high'] = True
                
                # Check for swing low
                is_swing_low = all(df.loc[i, 'low'] < df.loc[j, 'low'] 
                                  for j in range(i - lookback, i + lookback + 1) if j != i)
                if is_swing_low:
                    df.loc[i, 'swing_low'] = True
            
            return df
            
        except Exception as e:
            logger.error(f"Error calculating swing points: {e}")
            return df
    
    def shutdown(self) -> None:
        """
        Cleanly shutdown MT5 connection.
        """
        if self.connected:
            mt5.shutdown()
            self.connected = False
            logger.info("MT5 connection closed")
    
    def reconnect(self) -> bool:
        """
        Attempt to reconnect to MT5 after connection loss.
        
        Returns:
            bool: True if reconnection successful
        """
        logger.warning("Attempting to reconnect to MT5...")
        self.shutdown()
        
        for attempt in range(settings.MT5_RECONNECT_ATTEMPTS):
            logger.info(f"Reconnection attempt {attempt + 1}/{settings.MT5_RECONNECT_ATTEMPTS}")
            
            if self.mt5_credentials:
                if self.initialize_mt5(**self.mt5_credentials):
                    logger.info("Reconnection successful")
                    return True
            elif self.initialize_mt5():
                logger.info("Reconnection successful")
                return True
            
            if attempt < settings.MT5_RECONNECT_ATTEMPTS - 1:
                logger.info(f"Waiting {settings.MT5_RECONNECT_DELAY} seconds before retry...")
                import time
                time.sleep(settings.MT5_RECONNECT_DELAY)
        
        logger.error("All reconnection attempts failed")
        return False


# Module-level convenience function
def get_market_data() -> Dict[str, pd.DataFrame]:
    """
    Convenience function to fetch all timeframe data.
    
    Returns:
        Dictionary of timeframe data
    """
    handler = MarketDataHandler()
    
    if not handler.initialize_mt5():
        return {}
    
    data = handler.get_multi_timeframe_data()
    handler.shutdown()
    
    return data
