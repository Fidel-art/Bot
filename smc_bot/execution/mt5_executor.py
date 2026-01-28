"""
MT5 Execution Engine for XAUUSD SMC/ICT Trading Bot

Handles all trade execution operations:
- Order placement (market and pending)
- Stop-loss and take-profit management
- Position monitoring and modification
- Order validation and error handling
- Broker-compliant execution

Interfaces directly with MetaTrader 5 for trade execution.
"""

import MetaTrader5 as mt5
import logging
import time
from typing import Optional, Dict, Tuple
from datetime import datetime

from config import settings
from strategy.smc_engine import TradeSignal


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Dashboard support (import conditionally to avoid circular dependency)
_dashboard = None

def _get_dashboard():
    """Lazy import dashboard to avoid circular dependencies."""
    global _dashboard
    if _dashboard is None:
        try:
            from dashboard.dashboard import get_dashboard
            _dashboard = get_dashboard()
        except ImportError:
            _dashboard = None
    return _dashboard


class MT5Executor:
    """
    Handles all trade execution operations with MetaTrader 5.
    Implements order placement, modification, and monitoring.
    """
    
    def __init__(self, symbol: str = settings.SYMBOL):
        """
        Initialize the MT5 Executor.
        
        Args:
            symbol: Trading symbol (default: XAUUSD)
        """
        self.symbol = symbol
        self.symbol_info = None
        self.magic_number = settings.MAGIC_NUMBER
    
    def initialize(self) -> bool:
        """
        Initialize executor and validate symbol.
        
        Returns:
            bool: True if successful
        """
        try:
            self.symbol_info = mt5.symbol_info(self.symbol)
            
            if self.symbol_info is None:
                logger.error(f"Symbol {self.symbol} not found")
                return False
            
            if not self.symbol_info.visible:
                if not mt5.symbol_select(self.symbol, True):
                    logger.error(f"Failed to enable symbol {self.symbol}")
                    return False
            
            logger.info(f"Executor initialized for {self.symbol}")
            logger.info(f"  Min lot: {self.symbol_info.volume_min}")
            logger.info(f"  Max lot: {self.symbol_info.volume_max}")
            logger.info(f"  Lot step: {self.symbol_info.volume_step}")
            logger.info(f"  Point: {self.symbol_info.point}")
            logger.info(f"  Digits: {self.symbol_info.digits}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error initializing executor: {e}")
            return False
    
    def place_market_order(self, 
                          signal: TradeSignal,
                          lot_size: float,
                          stop_loss: float,
                          take_profit: float,
                          comment: str = "SMC Bot") -> Optional[int]:
        """
        Place a market order with stop-loss and take-profit.
        
        Args:
            signal: BUY or SELL signal
            lot_size: Position size in lots
            stop_loss: Stop loss price
            take_profit: Take profit price
            comment: Order comment
            
        Returns:
            Order ticket number if successful, None otherwise
        """
        if signal not in [TradeSignal.BUY, TradeSignal.SELL]:
            logger.error(f"Invalid signal: {signal}")
            return None
        
        try:
            # Get current price
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                logger.error("Failed to get current tick")
                return None
            
            # Determine order type and price
            if signal == TradeSignal.BUY:
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            else:
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
            
            # Normalize prices
            sl = self._normalize_price(stop_loss)
            tp = self._normalize_price(take_profit)
            lot = self._normalize_lot_size(lot_size)
            
            # Validate lot size
            if not self._validate_lot_size(lot):
                logger.error(f"Invalid lot size: {lot}")
                return None
            
            # Create order request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": lot,
                "type": order_type,
                "price": price,
                "sl": sl,
                "tp": tp,
                "deviation": settings.SLIPPAGE,
                "magic": self.magic_number,
                "comment": comment,
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK if settings.ORDER_FILLING == "FOK" else mt5.ORDER_FILLING_IOC,
            }
            
            # Log order details
            logger.info("=" * 50)
            logger.info("PLACING ORDER")
            logger.info(f"Signal: {signal.value}")
            logger.info(f"Price: {price}")
            logger.info(f"Lot Size: {lot}")
            logger.info(f"Stop Loss: {sl}")
            logger.info(f"Take Profit: {tp}")
            logger.info(f"Risk-Reward: {abs(tp - price) / abs(sl - price):.2f}")
            logger.info("=" * 50)
            
            # Send order with retry logic
            for attempt in range(settings.MAX_RETRY_ATTEMPTS):
                result = mt5.order_send(request)
                
                if result is None:
                    logger.error(f"Order send failed (attempt {attempt + 1})")
                    if attempt < settings.MAX_RETRY_ATTEMPTS - 1:
                        time.sleep(settings.RETRY_DELAY)
                    continue
                
                if result.retcode == mt5.TRADE_RETCODE_DONE:
                    logger.info(f"✅ ORDER EXECUTED SUCCESSFULLY")
                    logger.info(f"  Ticket: {result.order}")
                    logger.info(f"  Volume: {result.volume}")
                    logger.info(f"  Price: {result.price}")
                    
                    # Display dashboard notification
                    dashboard = _get_dashboard()
                    if dashboard:
                        dashboard.print_trade_notification(
                            signal=signal.value,
                            entry=result.price,
                            sl=sl,
                            tp=tp,
                            lots=result.volume
                        )
                        time.sleep(3)  # Show notification for 3 seconds
                    
                    return result.order
                
                else:
                    logger.error(f"Order failed (attempt {attempt + 1}): {result.retcode}")
                    logger.error(f"  Comment: {result.comment}")
                    
                    if attempt < settings.MAX_RETRY_ATTEMPTS - 1:
                        logger.info(f"Retrying in {settings.RETRY_DELAY} seconds...")
                        time.sleep(settings.RETRY_DELAY)
            
            logger.error("All order placement attempts failed")
            return None
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            return None
    
    def modify_position(self, 
                       ticket: int,
                       new_sl: Optional[float] = None,
                       new_tp: Optional[float] = None) -> bool:
        """
        Modify stop-loss or take-profit of existing position.
        
        Args:
            ticket: Position ticket number
            new_sl: New stop loss price (optional)
            new_tp: New take profit price (optional)
            
        Returns:
            bool: True if modification successful
        """
        try:
            # Get position info
            positions = mt5.positions_get(ticket=ticket)
            
            if positions is None or len(positions) == 0:
                logger.error(f"Position {ticket} not found")
                return False
            
            position = positions[0]
            
            # Use existing values if not provided
            sl = self._normalize_price(new_sl) if new_sl else position.sl
            tp = self._normalize_price(new_tp) if new_tp else position.tp
            
            # Create modify request
            request = {
                "action": mt5.TRADE_ACTION_SLTP,
                "symbol": self.symbol,
                "sl": sl,
                "tp": tp,
                "position": ticket,
            }
            
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("Position modification failed")
                return False
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Position {ticket} modified successfully")
                logger.info(f"  New SL: {sl}")
                logger.info(f"  New TP: {tp}")
                return True
            else:
                logger.error(f"Position modification failed: {result.retcode}")
                logger.error(f"  Comment: {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Error modifying position: {e}")
            return False
    
    def close_position(self, ticket: int) -> bool:
        """
        Close an open position.
        
        Args:
            ticket: Position ticket number
            
        Returns:
            bool: True if position closed successfully
        """
        try:
            # Get position info
            positions = mt5.positions_get(ticket=ticket)
            
            if positions is None or len(positions) == 0:
                logger.error(f"Position {ticket} not found")
                return False
            
            position = positions[0]
            
            # Get current price
            tick = mt5.symbol_info_tick(self.symbol)
            if tick is None:
                logger.error("Failed to get current tick")
                return False
            
            # Determine close parameters
            if position.type == mt5.ORDER_TYPE_BUY:
                order_type = mt5.ORDER_TYPE_SELL
                price = tick.bid
            else:
                order_type = mt5.ORDER_TYPE_BUY
                price = tick.ask
            
            # Create close request
            request = {
                "action": mt5.TRADE_ACTION_DEAL,
                "symbol": self.symbol,
                "volume": position.volume,
                "type": order_type,
                "position": ticket,
                "price": price,
                "deviation": settings.SLIPPAGE,
                "magic": self.magic_number,
                "comment": "Close by Bot",
                "type_time": mt5.ORDER_TIME_GTC,
                "type_filling": mt5.ORDER_FILLING_FOK if settings.ORDER_FILLING == "FOK" else mt5.ORDER_FILLING_IOC,
            }
            
            result = mt5.order_send(request)
            
            if result is None:
                logger.error("Position close failed")
                return False
            
            if result.retcode == mt5.TRADE_RETCODE_DONE:
                logger.info(f"✅ Position {ticket} closed successfully")
                logger.info(f"  Close price: {result.price}")
                logger.info(f"  Profit: ${position.profit:.2f}")
                return True
            else:
                logger.error(f"Position close failed: {result.retcode}")
                logger.error(f"  Comment: {result.comment}")
                return False
                
        except Exception as e:
            logger.error(f"Error closing position: {e}")
            return False
    
    def get_position_info(self, ticket: int) -> Optional[Dict]:
        """
        Get detailed information about a position.
        
        Args:
            ticket: Position ticket number
            
        Returns:
            Dictionary with position details or None
        """
        try:
            positions = mt5.positions_get(ticket=ticket)
            
            if positions is None or len(positions) == 0:
                return None
            
            pos = positions[0]
            
            return {
                'ticket': pos.ticket,
                'time': datetime.fromtimestamp(pos.time),
                'type': 'BUY' if pos.type == mt5.ORDER_TYPE_BUY else 'SELL',
                'volume': pos.volume,
                'price_open': pos.price_open,
                'sl': pos.sl,
                'tp': pos.tp,
                'price_current': pos.price_current,
                'profit': pos.profit,
                'comment': pos.comment
            }
            
        except Exception as e:
            logger.error(f"Error getting position info: {e}")
            return None
    
    def _normalize_price(self, price: float) -> float:
        """
        Normalize price according to symbol's digit precision.
        
        Args:
            price: Raw price value
            
        Returns:
            Normalized price
        """
        if self.symbol_info is None:
            return round(price, 5)
        
        return round(price, self.symbol_info.digits)
    
    def _normalize_lot_size(self, lot: float) -> float:
        """
        Normalize lot size according to symbol specifications.
        
        Args:
            lot: Raw lot size
            
        Returns:
            Normalized lot size
        """
        if self.symbol_info is None:
            return lot
        
        # Round to nearest lot step
        lot_step = self.symbol_info.volume_step
        normalized = round(lot / lot_step) * lot_step
        
        return round(normalized, 2)
    
    def _validate_lot_size(self, lot: float) -> bool:
        """
        Validate that lot size meets broker requirements.
        
        Args:
            lot: Lot size to validate
            
        Returns:
            bool: True if valid
        """
        if self.symbol_info is None:
            return False
        
        if lot < self.symbol_info.volume_min:
            logger.error(f"Lot size {lot} below minimum {self.symbol_info.volume_min}")
            return False
        
        if lot > self.symbol_info.volume_max:
            logger.error(f"Lot size {lot} above maximum {self.symbol_info.volume_max}")
            return False
        
        return True
    
    def get_open_positions_count(self) -> int:
        """
        Get count of currently open positions for this symbol.
        
        Returns:
            Number of open positions
        """
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            
            if positions is None:
                return 0
            
            # Filter by magic number
            bot_positions = [p for p in positions if p.magic == self.magic_number]
            
            return len(bot_positions)
            
        except Exception as e:
            logger.error(f"Error getting position count: {e}")
            return 0
    
    def get_all_positions_data(self) -> list:
        """
        Get detailed data for all open positions.
        
        Returns:
            List of position dictionaries
        """
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            
            if positions is None:
                return []
            
            # Filter by magic number and format data
            bot_positions = []
            for p in positions:
                if p.magic == self.magic_number:
                    bot_positions.append({
                        'ticket': p.ticket,
                        'type': 'BUY' if p.type == mt5.ORDER_TYPE_BUY else 'SELL',
                        'volume': p.volume,
                        'price': p.price_open,
                        'sl': p.sl,
                        'tp': p.tp,
                        'profit': p.profit,
                        'current_price': p.price_current
                    })
            
            return bot_positions
            
        except Exception as e:
            logger.error(f"Error getting positions data: {e}")
            return []
    
    def close_all_positions(self) -> int:
        """
        Close all open positions for this symbol and magic number.
        
        Returns:
            Number of positions closed
        """
        try:
            positions = mt5.positions_get(symbol=self.symbol)
            
            if positions is None or len(positions) == 0:
                logger.info("No positions to close")
                return 0
            
            closed_count = 0
            
            for position in positions:
                if position.magic == self.magic_number:
                    if self.close_position(position.ticket):
                        closed_count += 1
            
            logger.info(f"Closed {closed_count} positions")
            return closed_count
            
        except Exception as e:
            logger.error(f"Error closing all positions: {e}")
            return 0
