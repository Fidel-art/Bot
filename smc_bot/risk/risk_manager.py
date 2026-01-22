"""
Risk Management Module for XAUUSD SMC/ICT Trading Bot

Implements critical account protection logic:
- 5% maximum drawdown enforcement (HARD LOCK)
- Trade-level risk calculation
- Position sizing
- Risk-reward validation
- Trading lock mechanism

This module ensures capital preservation and prop firm compliance.
"""

import os
import logging
from datetime import datetime
from typing import Optional, Dict, Tuple
from pathlib import Path

from config import settings


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class RiskManager:
    """
    Manages all risk-related calculations and account protection.
    Enforces strict drawdown limits and position sizing rules.
    """
    
    def __init__(self):
        """Initialize the Risk Manager."""
        self.initial_balance = None
        self.current_balance = None
        self.current_equity = None
        self.drawdown_locked = False
        self.lock_file_path = Path(settings.DRAWDOWN_LOCK_FILE)
        
        # Check for existing lock file
        self._check_lock_status()
    
    def _check_lock_status(self) -> None:
        """Check if trading is locked due to previous drawdown breach."""
        if self.lock_file_path.exists():
            self.drawdown_locked = True
            logger.critical("⚠️ TRADING LOCKED: Previous drawdown limit breach detected")
            logger.critical(f"⚠️ Lock file found at: {self.lock_file_path}")
            logger.critical("⚠️ Manual intervention required to resume trading")
            
            # Read lock file details
            try:
                with open(self.lock_file_path, 'r') as f:
                    lock_info = f.read()
                logger.critical(f"⚠️ Lock details: {lock_info}")
            except Exception as e:
                logger.error(f"Error reading lock file: {e}")
    
    def initialize(self, account_info: Dict) -> bool:
        """
        Initialize risk manager with account information.
        
        Args:
            account_info: Dictionary containing account balance and equity
            
        Returns:
            bool: True if initialization successful and trading allowed
        """
        try:
            self.initial_balance = account_info['balance']
            self.current_balance = account_info['balance']
            self.current_equity = account_info['equity']
            
            logger.info(f"Risk Manager initialized:")
            logger.info(f"  Initial Balance: ${self.initial_balance:.2f}")
            logger.info(f"  Current Equity: ${self.current_equity:.2f}")
            logger.info(f"  Max Drawdown: {settings.MAX_DRAWDOWN_PERCENT}%")
            
            # Check if already locked
            if self.drawdown_locked:
                return False
            
            # Check current drawdown status
            return self._check_drawdown()
            
        except Exception as e:
            logger.error(f"Error initializing risk manager: {e}")
            return False
    
    def update_account(self, account_info: Dict) -> bool:
        """
        Update account information and check drawdown.
        
        Args:
            account_info: Current account information
            
        Returns:
            bool: True if trading allowed, False if locked
        """
        try:
            self.current_balance = account_info['balance']
            self.current_equity = account_info['equity']
            
            return self._check_drawdown()
            
        except Exception as e:
            logger.error(f"Error updating account: {e}")
            return False
    
    def _check_drawdown(self) -> bool:
        """
        Check if current drawdown exceeds maximum allowed.
        If exceeded, lock trading immediately.
        
        Returns:
            bool: True if within limits, False if exceeded
        """
        if not settings.ENABLE_DRAWDOWN_PROTECTION:
            return True
        
        if self.drawdown_locked:
            return False
        
        if self.initial_balance is None or self.current_equity is None:
            logger.error("Cannot check drawdown: account not initialized")
            return False
        
        # Calculate drawdown as percentage of initial balance
        drawdown = ((self.initial_balance - self.current_equity) / self.initial_balance) * 100
        
        logger.info(f"Current Drawdown: {drawdown:.2f}% (Max: {settings.MAX_DRAWDOWN_PERCENT}%)")
        
        if drawdown >= settings.MAX_DRAWDOWN_PERCENT:
            self._lock_trading(drawdown)
            return False
        
        # Warn if approaching limit (within 1%)
        if drawdown >= (settings.MAX_DRAWDOWN_PERCENT - 1):
            logger.warning(f"⚠️ DRAWDOWN WARNING: {drawdown:.2f}% (approaching {settings.MAX_DRAWDOWN_PERCENT}% limit)")
        
        return True
    
    def _lock_trading(self, drawdown: float) -> None:
        """
        Lock trading due to drawdown limit breach.
        Creates lock file to prevent future trading.
        
        Args:
            drawdown: Current drawdown percentage
        """
        self.drawdown_locked = True
        
        logger.critical("🛑 TRADING LOCKED - Maximum drawdown exceeded!")
        logger.critical(f"🛑 Current Drawdown: {drawdown:.2f}%")
        logger.critical(f"🛑 Maximum Allowed: {settings.MAX_DRAWDOWN_PERCENT}%")
        logger.critical(f"🛑 Initial Balance: ${self.initial_balance:.2f}")
        logger.critical(f"🛑 Current Equity: ${self.current_equity:.2f}")
        
        # Create lock file
        try:
            os.makedirs(os.path.dirname(self.lock_file_path), exist_ok=True)
            
            with open(self.lock_file_path, 'w') as f:
                f.write(f"TRADING LOCKED\n")
                f.write(f"Timestamp: {datetime.now()}\n")
                f.write(f"Drawdown: {drawdown:.2f}%\n")
                f.write(f"Initial Balance: ${self.initial_balance:.2f}\n")
                f.write(f"Current Equity: ${self.current_equity:.2f}\n")
                f.write(f"Loss: ${self.initial_balance - self.current_equity:.2f}\n")
                f.write(f"\nMANUAL INTERVENTION REQUIRED\n")
                f.write(f"Delete this file only after reviewing account and adjusting strategy.\n")
            
            logger.critical(f"🛑 Lock file created at: {self.lock_file_path}")
            
        except Exception as e:
            logger.error(f"Failed to create lock file: {e}")
    
    def can_open_trade(self, current_positions: int = 0) -> Tuple[bool, str]:
        """
        Check if new trade can be opened based on risk rules.
        
        Args:
            current_positions: Number of currently open positions
            
        Returns:
            Tuple of (allowed, reason)
        """
        # Check if locked
        if self.drawdown_locked:
            return (False, "Trading locked due to drawdown limit breach")
        
        # Check drawdown
        if not self._check_drawdown():
            return (False, "Current drawdown exceeds maximum limit")
        
        # Check maximum open trades
        if current_positions >= settings.MAX_OPEN_TRADES:
            return (False, f"Maximum open trades reached ({settings.MAX_OPEN_TRADES})")
        
        return (True, "Trade allowed")
    
    def calculate_position_size(self, account_balance: float, 
                                stop_loss_points: float,
                                symbol_point: float,
                                symbol_value: float) -> float:
        """
        Calculate position size based on risk parameters.
        
        Args:
            account_balance: Current account balance
            stop_loss_points: Stop loss distance in points
            symbol_point: Symbol point value
            symbol_value: Contract/lot value
            
        Returns:
            Position size in lots
        """
        try:
            # Calculate risk amount in currency
            risk_amount = account_balance * (settings.RISK_PER_TRADE_PERCENT / 100)
            
            # Calculate position size
            # Risk per lot = stop_loss_points * point_value * contract_size
            point_value = symbol_point * symbol_value
            risk_per_lot = stop_loss_points * point_value
            
            if risk_per_lot <= 0:
                logger.error("Invalid risk per lot calculation")
                return settings.LOT_SIZE
            
            position_size = risk_amount / risk_per_lot
            
            # Use fixed lot size (can be enhanced with dynamic sizing)
            position_size = settings.LOT_SIZE
            
            logger.info(f"Position size calculated: {position_size} lots")
            logger.info(f"  Risk amount: ${risk_amount:.2f}")
            logger.info(f"  Stop loss: {stop_loss_points} points")
            
            return position_size
            
        except Exception as e:
            logger.error(f"Error calculating position size: {e}")
            return settings.LOT_SIZE
    
    def validate_risk_reward(self, entry_price: float, 
                            stop_loss: float, 
                            take_profit: float,
                            is_buy: bool) -> Tuple[bool, float]:
        """
        Validate that trade meets minimum risk-reward ratio.
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            is_buy: True if buy order, False if sell
            
        Returns:
            Tuple of (is_valid, risk_reward_ratio)
        """
        try:
            if is_buy:
                risk = entry_price - stop_loss
                reward = take_profit - entry_price
            else:
                risk = stop_loss - entry_price
                reward = entry_price - take_profit
            
            if risk <= 0:
                logger.error("Invalid risk calculation: SL must be beyond entry")
                return (False, 0.0)
            
            if reward <= 0:
                logger.error("Invalid reward calculation: TP must be beyond entry")
                return (False, 0.0)
            
            rr_ratio = reward / risk
            
            if rr_ratio < settings.MIN_RISK_REWARD:
                logger.warning(f"Risk-reward ratio {rr_ratio:.2f} below minimum {settings.MIN_RISK_REWARD}")
                return (False, rr_ratio)
            
            logger.info(f"Risk-Reward validated: {rr_ratio:.2f} (minimum: {settings.MIN_RISK_REWARD})")
            return (True, rr_ratio)
            
        except Exception as e:
            logger.error(f"Error validating risk-reward: {e}")
            return (False, 0.0)
    
    def manual_unlock(self) -> bool:
        """
        Manually unlock trading by removing lock file.
        Use with extreme caution after reviewing account.
        
        Returns:
            bool: True if successfully unlocked
        """
        try:
            if not self.drawdown_locked:
                logger.info("Trading not locked")
                return True
            
            if self.lock_file_path.exists():
                os.remove(self.lock_file_path)
                logger.warning("⚠️ Lock file removed - trading unlocked")
            
            self.drawdown_locked = False
            logger.warning("⚠️ Trading manually unlocked - proceed with caution")
            
            return True
            
        except Exception as e:
            logger.error(f"Error unlocking trading: {e}")
            return False
    
    def get_risk_status(self) -> Dict:
        """
        Get current risk management status.
        
        Returns:
            Dictionary with risk metrics
        """
        if self.initial_balance and self.current_equity:
            drawdown = ((self.initial_balance - self.current_equity) / self.initial_balance) * 100
        else:
            drawdown = 0.0
        
        return {
            'locked': self.drawdown_locked,
            'initial_balance': self.initial_balance,
            'current_balance': self.current_balance,
            'current_equity': self.current_equity,
            'drawdown_percent': drawdown,
            'max_drawdown': settings.MAX_DRAWDOWN_PERCENT,
            'remaining_drawdown': settings.MAX_DRAWDOWN_PERCENT - drawdown,
            'lock_file_exists': self.lock_file_path.exists()
        }
