"""
XAUUSD SMC/ICT Trading Bot - Main Entry Point

This is the main orchestration module that:
1. Initializes all system components
2. Connects to MetaTrader 5
3. Fetches multi-timeframe market data
4. Analyzes market using SMC/ICT methodology
5. Manages risk and account protection
6. Executes trades when conditions align
7. Monitors positions and drawdown

Author: SMC Trading Bot
Version: 1.0.0
"""

import MetaTrader5 as mt5
import time
import logging
from datetime import datetime
from pathlib import Path

# Import bot modules
from config import settings
from data.market_data import MarketDataHandler
from strategy.smc_engine import SMCEngine, TradeSignal
from risk.risk_manager import RiskManager
from execution.mt5_executor import MT5Executor


# Setup logging
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.LOG_FILE),
        logging.StreamHandler() if settings.ENABLE_CONSOLE_LOG else logging.NullHandler()
    ]
)
logger = logging.getLogger(__name__)


class SMCTradingBot:
    """
    Main trading bot class that orchestrates all components.
    Implements the complete trading workflow.
    """
    
    def __init__(self):
        """Initialize the trading bot."""
        self.market_data = None
        self.smc_engine = None
        self.risk_manager = None
        self.executor = None
        self.running = False
        
        logger.info("=" * 70)
        logger.info("XAUUSD SMC/ICT TRADING BOT")
        logger.info("=" * 70)
        logger.info(f"Symbol: {settings.SYMBOL}")
        logger.info(f"Timeframes: {list(settings.TIMEFRAMES.keys())}")
        logger.info(f"Max Drawdown: {settings.MAX_DRAWDOWN_PERCENT}%")
        logger.info(f"Lot Size: {settings.LOT_SIZE}")
        logger.info(f"Min Risk-Reward: {settings.MIN_RISK_REWARD}")
        logger.info("=" * 70)
    
    def initialize(self) -> bool:
        """
        Initialize all bot components.
        
        Returns:
            bool: True if all components initialized successfully
        """
        logger.info("Initializing bot components...")
        
        try:
            # Initialize Market Data Handler
            logger.info("1/4 Initializing Market Data Handler...")
            self.market_data = MarketDataHandler(settings.SYMBOL)
            
            if not self.market_data.initialize_mt5():
                logger.error("Failed to initialize MT5 connection")
                return False
            
            logger.info("✅ Market Data Handler initialized")
            
            # Initialize SMC Strategy Engine
            logger.info("2/4 Initializing SMC Strategy Engine...")
            self.smc_engine = SMCEngine()
            logger.info("✅ SMC Strategy Engine initialized")
            
            # Initialize Risk Manager
            logger.info("3/4 Initializing Risk Manager...")
            self.risk_manager = RiskManager()
            
            account_info = self.market_data.get_account_info()
            if account_info is None:
                logger.error("Failed to get account info")
                return False
            
            if not self.risk_manager.initialize(account_info):
                logger.error("Risk Manager initialization failed - TRADING LOCKED")
                return False
            
            logger.info("✅ Risk Manager initialized")
            
            # Initialize Trade Executor
            logger.info("4/4 Initializing Trade Executor...")
            self.executor = MT5Executor(settings.SYMBOL)
            
            if not self.executor.initialize():
                logger.error("Failed to initialize Trade Executor")
                return False
            
            logger.info("✅ Trade Executor initialized")
            
            logger.info("=" * 70)
            logger.info("✅ ALL COMPONENTS INITIALIZED SUCCESSFULLY")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error(f"Error during initialization: {e}")
            return False
    
    def run_analysis_cycle(self) -> None:
        """
        Execute one complete analysis and trading cycle.
        This is the main trading logic loop.
        """
        try:
            logger.info("\n" + "=" * 70)
            logger.info(f"STARTING ANALYSIS CYCLE - {datetime.now()}")
            logger.info("=" * 70)
            
            # Step 1: Update account information
            logger.info("Step 1: Updating account information...")
            account_info = self.market_data.get_account_info()
            
            if account_info is None:
                logger.error("Failed to get account info")
                return
            
            logger.info(f"  Balance: ${account_info['balance']:.2f}")
            logger.info(f"  Equity: ${account_info['equity']:.2f}")
            logger.info(f"  Profit: ${account_info['profit']:.2f}")
            
            # Step 2: Check risk status
            logger.info("\nStep 2: Checking risk status...")
            
            if not self.risk_manager.update_account(account_info):
                logger.critical("🛑 TRADING LOCKED DUE TO DRAWDOWN - STOPPING BOT")
                self.running = False
                return
            
            risk_status = self.risk_manager.get_risk_status()
            logger.info(f"  Drawdown: {risk_status['drawdown_percent']:.2f}%")
            logger.info(f"  Remaining: {risk_status['remaining_drawdown']:.2f}%")
            
            # Step 3: Check if we can open new trades
            logger.info("\nStep 3: Checking trading eligibility...")
            current_positions = self.executor.get_open_positions_count()
            logger.info(f"  Current positions: {current_positions}")
            
            can_trade, reason = self.risk_manager.can_open_trade(current_positions)
            
            if not can_trade:
                logger.warning(f"  Cannot open trade: {reason}")
                logger.info("  Skipping to next cycle...")
                return
            
            logger.info(f"  ✅ {reason}")
            
            # Step 4: Fetch multi-timeframe data
            logger.info("\nStep 4: Fetching multi-timeframe data...")
            mtf_data = self.market_data.get_multi_timeframe_data()
            
            if not mtf_data or len(mtf_data) != len(settings.TIMEFRAMES):
                logger.error("Failed to fetch complete multi-timeframe data")
                return
            
            for tf in mtf_data.keys():
                logger.info(f"  {tf}: {len(mtf_data[tf])} candles")
            
            # Step 5: Analyze market and generate signal
            logger.info("\nStep 5: Analyzing market structure (SMC/ICT)...")
            trade_signal = self.smc_engine.generate_trade_signal(mtf_data)
            
            signal = trade_signal.get('signal', TradeSignal.NONE)
            
            if signal == TradeSignal.NONE:
                logger.info("  No trade signal generated")
                logger.info("  Market conditions not aligned")
                return
            
            logger.info(f"  🎯 TRADE SIGNAL: {signal.value}")
            logger.info(f"  Entry: {trade_signal['entry_price']:.5f}")
            logger.info(f"  Stop Loss: {trade_signal['stop_loss']:.5f}")
            logger.info(f"  Take Profit: {trade_signal['take_profit']:.5f}")
            
            # Step 6: Validate risk-reward ratio
            logger.info("\nStep 6: Validating risk-reward ratio...")
            is_valid, rr_ratio = self.risk_manager.validate_risk_reward(
                trade_signal['entry_price'],
                trade_signal['stop_loss'],
                trade_signal['take_profit'],
                signal == TradeSignal.BUY
            )
            
            if not is_valid:
                logger.warning(f"  Risk-reward ratio {rr_ratio:.2f} insufficient")
                return
            
            logger.info(f"  ✅ Risk-Reward: {rr_ratio:.2f}")
            
            # Step 7: Execute trade
            logger.info("\nStep 7: Executing trade...")
            ticket = self.executor.place_market_order(
                signal=signal,
                lot_size=settings.LOT_SIZE,
                stop_loss=trade_signal['stop_loss'],
                take_profit=trade_signal['take_profit'],
                comment="SMC Bot Auto"
            )
            
            if ticket:
                logger.info(f"✅ TRADE EXECUTED - Ticket: {ticket}")
            else:
                logger.error("❌ Trade execution failed")
            
            logger.info("=" * 70)
            logger.info("CYCLE COMPLETE")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Error during analysis cycle: {e}", exc_info=True)
    
    def run(self, interval_seconds: int = 300) -> None:
        """
        Start the bot's main loop.
        
        Args:
            interval_seconds: Seconds between analysis cycles (default: 300 = 5 minutes)
        """
        self.running = True
        
        logger.info(f"\n🚀 BOT STARTED - Analysis every {interval_seconds} seconds")
        logger.info("Press Ctrl+C to stop the bot\n")
        
        try:
            while self.running:
                self.run_analysis_cycle()
                
                if self.running:
                    logger.info(f"\nWaiting {interval_seconds} seconds until next cycle...\n")
                    time.sleep(interval_seconds)
                
        except KeyboardInterrupt:
            logger.info("\n\n⚠️ KEYBOARD INTERRUPT DETECTED")
            self.shutdown()
        except Exception as e:
            logger.error(f"\n\n❌ CRITICAL ERROR: {e}", exc_info=True)
            self.shutdown()
    
    def shutdown(self) -> None:
        """Cleanly shutdown the bot and close connections."""
        logger.info("=" * 70)
        logger.info("SHUTTING DOWN BOT")
        logger.info("=" * 70)
        
        self.running = False
        
        try:
            # Display final risk status
            if self.risk_manager:
                risk_status = self.risk_manager.get_risk_status()
                logger.info("\nFinal Risk Status:")
                logger.info(f"  Initial Balance: ${risk_status['initial_balance']:.2f}")
                logger.info(f"  Current Equity: ${risk_status['current_equity']:.2f}")
                logger.info(f"  Drawdown: {risk_status['drawdown_percent']:.2f}%")
                logger.info(f"  Locked: {risk_status['locked']}")
            
            # Display open positions
            if self.executor:
                open_count = self.executor.get_open_positions_count()
                logger.info(f"\nOpen Positions: {open_count}")
            
            # Close MT5 connection
            if self.market_data:
                self.market_data.shutdown()
            
            logger.info("\n✅ Bot shutdown complete")
            logger.info("=" * 70)
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")


def main():
    """
    Main entry point for the trading bot.
    """
    # Display banner
    print("\n" + "=" * 70)
    print("XAUUSD SMC/ICT TRADING BOT")
    print("Smart Money Concepts + Inner Circle Trader")
    print("=" * 70 + "\n")
    
    # Create and initialize bot
    bot = SMCTradingBot()
    
    if not bot.initialize():
        logger.error("Bot initialization failed. Exiting...")
        return
    
    # Run the bot
    # Analysis every 5 minutes (300 seconds)
    # Adjust interval based on your trading style
    bot.run(interval_seconds=300)


if __name__ == "__main__":
    main()
