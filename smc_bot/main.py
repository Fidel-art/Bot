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
from colorama import Fore, Style, init

# Initialize colorama for colored terminal output
init(autoreset=True)

# Import bot modules
from config import settings
from config.trader_profile import get_profile_manager
from config.subscription import get_subscription_manager
from data.market_data import MarketDataHandler
from strategy.smc_engine import SMCEngine, TradeSignal
from risk.risk_manager import RiskManager
from execution.mt5_executor import MT5Executor
from dashboard.dashboard import get_dashboard
from dashboard.trade_analyzer import get_analyzer


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
    
    def __init__(self, trader_profile=None):
        """Initialize the trading bot with optional trader profile."""
        self.market_data = None
        self.smc_engine = None
        self.risk_manager = None
        self.executor = None
        self.running = False
        self.dashboard = get_dashboard()
        self.analyzer = get_analyzer()
        self.trader_profile = trader_profile
        
        # Use profile settings if available
        if trader_profile:
            self.lot_size = trader_profile.lot_size
            self.max_drawdown = trader_profile.max_drawdown
            self.risk_per_trade = trader_profile.risk_per_trade
            self.max_open_trades = trader_profile.max_open_trades
            self.min_risk_reward = trader_profile.min_risk_reward
        else:
            self.lot_size = settings.LOT_SIZE
            self.max_drawdown = settings.MAX_DRAWDOWN_PERCENT
            self.risk_per_trade = settings.RISK_PER_TRADE_PERCENT
            self.max_open_trades = settings.MAX_OPEN_TRADES
            self.min_risk_reward = settings.MIN_RISK_REWARD
        
        logger.info("=" * 70)
        logger.info("XAUUSD SMC/ICT TRADING BOT")
        logger.info("=" * 70)
        if trader_profile:
            logger.info(f"Trader: {trader_profile.name} ({trader_profile.trader_id})")
        logger.info(f"Symbol: {settings.SYMBOL}")
        logger.info(f"Timeframes: {list(settings.TIMEFRAMES.keys())}")
        logger.info(f"Max Drawdown: {self.max_drawdown}%")
        logger.info(f"Lot Size: {self.lot_size}")
        logger.info(f"Min Risk-Reward: {self.min_risk_reward}")
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
            # Step 1: Update account information
            account_info = self.market_data.get_account_info()
            
            if account_info is None:
                logger.error("Failed to get account info")
                return
            
            # Step 2: Check risk status
            if not self.risk_manager.update_account(account_info):
                logger.critical("🛑 TRADING LOCKED DUE TO DRAWDOWN - STOPPING BOT")
                self.dashboard.print_status_update("TRADING LOCKED - Maximum drawdown reached!", "error")
                self.running = False
                return
            
            risk_status = self.risk_manager.get_risk_status()
            
            # Step 3: Check if we can open new trades
            current_positions = self.executor.get_open_positions_count()
            positions_data = self.executor.get_all_positions_data()
            
            can_trade, reason = self.risk_manager.can_open_trade(current_positions)
            
            # Step 4: Fetch multi-timeframe data
            mtf_data = self.market_data.get_multi_timeframe_data()
            
            if not mtf_data or len(mtf_data) != len(settings.TIMEFRAMES):
                logger.error("Failed to fetch complete multi-timeframe data")
                return
            
            # Step 5: Analyze market and generate signal
            trade_signal = self.smc_engine.generate_trade_signal(mtf_data)
            signal = trade_signal.get('signal', TradeSignal.NONE)
            
            # Update dashboard with current status
            dashboard_data = {
                'signal': signal.value if signal != TradeSignal.NONE else 'NONE',
                'account': {
                    'balance': account_info['balance'],
                    'equity': account_info['equity'],
                    'profit': account_info['profit']
                },
                'risk': {
                    'drawdown': risk_status['drawdown_percent'],
                    'remaining': risk_status['remaining_drawdown'],
                    'max_drawdown': self.max_drawdown
                },
                'positions': {
                    'count': current_positions,
                    'data': positions_data
                }
            }
            
            # Add subscription info if available
            if self.trader_profile:
                from config.subscription import get_subscription_manager
                sub_manager = get_subscription_manager()
                sub_info = sub_manager.get_subscription_info(self.trader_profile.trader_id)
                if sub_info:
                    try:
                        from datetime import datetime
                        expiration = datetime.fromisoformat(sub_info['expiration_date'])
                        days_remaining = (expiration - datetime.now()).days
                        dashboard_data['subscription'] = {
                            'is_valid': sub_info.get('is_active', False),
                            'plan': sub_info.get('plan', 'N/A'),
                            'days_remaining': max(0, days_remaining)
                        }
                    except:
                        pass
            
            self.dashboard.display_full_dashboard(dashboard_data)
            
            # If no signal or can't trade, wait for next cycle
            if signal == TradeSignal.NONE:
                logger.info("No trade signal - waiting for market conditions")
                return
            
            if not can_trade:
                logger.warning(f"Cannot open trade: {reason}")
                self.dashboard.print_status_update(f"Cannot trade: {reason}", "warning")
                return
            
            logger.info(f"🎯 TRADE SIGNAL: {signal.value}")
            logger.info(f"  Entry: {trade_signal['entry_price']:.5f}")
            logger.info(f"  Stop Loss: {trade_signal['stop_loss']:.5f}")
            logger.info(f"  Take Profit: {trade_signal['take_profit']:.5f}")
            
            # Step 6: Validate risk-reward ratio
            is_valid, rr_ratio = self.risk_manager.validate_risk_reward(
                trade_signal['entry_price'],
                trade_signal['stop_loss'],
                trade_signal['take_profit'],
                signal == TradeSignal.BUY
            )
            
            if not is_valid:
                logger.warning(f"Risk-reward ratio {rr_ratio:.2f} insufficient")
                self.dashboard.print_status_update(f"Risk-reward {rr_ratio:.2f} too low", "warning")
                return
            
            logger.info(f"✅ Risk-Reward: {rr_ratio:.2f}")
            
            # Step 7: Execute trade
            logger.info("Executing trade...")
            ticket = self.executor.place_market_order(
                signal=signal,
                lot_size=self.lot_size,
                stop_loss=trade_signal['stop_loss'],
                take_profit=trade_signal['take_profit'],
                comment="SMC Bot Auto"
            )
            
            if ticket:
                logger.info(f"✅ TRADE EXECUTED - Ticket: {ticket}")
                self.dashboard.print_status_update(f"Trade executed! Ticket: {ticket}", "success")
                
                # Save trade to history
                trade_record = {
                    'ticket': ticket,
                    'signal': signal.value,
                    'entry_price': trade_signal['entry_price'],
                    'stop_loss': trade_signal['stop_loss'],
                    'take_profit': trade_signal['take_profit'],
                    'lots': self.lot_size,
                    'risk_reward': rr_ratio,
                    'entry_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'exit_time': None,
                    'profit': 0.0,
                    'status': 'open'
                }
                
                if self.trader_profile:
                    # Save to trader-specific history
                    from dashboard.trade_analyzer import TradeAnalyzer
                    trader_analyzer = TradeAnalyzer(self.trader_profile.trade_history_file)
                    trader_analyzer.save_trade(trade_record)
                else:
                    self.analyzer.save_trade(trade_record)
            else:
                logger.error("❌ Trade execution failed")
                self.dashboard.print_status_update("Trade execution failed!", "error")
            
        except Exception as e:
            logger.error(f"Error during analysis cycle: {e}", exc_info=True)
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
    
    # Initialize MT5 early to ensure connection is established
    print("Initializing MetaTrader 5 connection...")
    if not mt5.initialize():
        error_code, error_msg = mt5.last_error()
        print(f"❌ Failed to initialize MT5: ({error_code}, '{error_msg}')")
        
        # Try to launch MT5 if it's not running
        import subprocess
        import os
        
        # Common MT5 installation paths
        mt5_paths = [
            r"C:\Program Files\MetaTrader 5\terminal64.exe",
            r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
            os.path.expanduser(r"~\AppData\Roaming\MetaQuotes\Terminal\terminal64.exe")
        ]
        
        mt5_found = False
        for path in mt5_paths:
            if os.path.exists(path):
                print(f"\n🚀 Launching MetaTrader 5 from: {path}")
                try:
                    subprocess.Popen([path])
                    mt5_found = True
                    print("⏳ Waiting for MT5 to start (10 seconds)...")
                    time.sleep(10)
                    
                    # Try to initialize again
                    if mt5.initialize():
                        print("✅ MT5 connection established\n")
                        break
                    else:
                        print("❌ MT5 started but connection failed. Please log in to MT5 and run the bot again.")
                        return
                except Exception as e:
                    print(f"Failed to launch MT5: {e}")
                break
        
        if not mt5_found:
            print("Please ensure MetaTrader 5 is installed and logged in, then try again.")
            return
    else:
        print("✅ MT5 connection established\n")
    
    # Initialize managers
    profile_manager = get_profile_manager()
    subscription_manager = get_subscription_manager()
    
    # Check if profiles exist
    if len(profile_manager.list_profiles()) == 0:
        print("No trader profiles found. Let's create one!\n")
        profile = profile_manager.create_profile_interactive()
        if not profile:
            print("Profile creation cancelled. Exiting...")
            return
        profile_manager.select_profile(profile.trader_id)
    else:
        # Show available profiles and let user select
        print("Available trader profiles:\n")
        profile_manager.display_profiles()
        
        choice = input("\n[1] Select existing profile\n[2] Create new profile\n[3] Use default settings\n\nChoice: ")
        
        if choice == "1":
            profile = profile_manager.interactive_selection()
            if not profile:
                print("No profile selected. Using default settings...")
                profile = None
        elif choice == "2":
            profile = profile_manager.create_profile_interactive()
            if profile:
                profile_manager.select_profile(profile.trader_id)
        else:
            print("Using default settings from config...")
            profile = None
    
    # Get current profile (if any)
    current_profile = profile_manager.current_profile
    
    # Check subscription if profile exists
    if current_profile:
        # Check if subscription is valid
        is_valid, message = subscription_manager.validate_subscription(current_profile.trader_id)
        
        if not is_valid:
            print(f"\n{Fore.RED}❌ {message}")
            print(f"{Fore.YELLOW}\nYou need an active subscription to use the bot.")
            
            # Show subscription menu
            print("\n" + "=" * 70)
            print("SUBSCRIPTION REQUIRED")
            print("=" * 70)
            print("[1] Subscribe Now")
            print("[2] View Subscription Status")
            print("[3] I have a license key")
            print("[4] Renew Subscription")
            print("[0] Exit")
            
            sub_choice = input("\nChoice: ")
            
            if sub_choice == "1":
                success, msg = subscription_manager.interactive_subscription(current_profile.trader_id)
                if success:
                    print(f"\n{Fore.GREEN}✅ {msg}")
                    current_profile.has_subscription = True
                    current_profile.subscription_checked = True
                    profile_manager.save_profiles()
                else:
                    print(f"\n{Fore.RED}❌ {msg}")
                    print("Cannot proceed without subscription. Exiting...")
                    return
            
            elif sub_choice == "2":
                subscription_manager.display_subscription_status(current_profile.trader_id)
                return
            
            elif sub_choice == "3":
                from config.subscription import SubscriptionPlan
                print("\nWhich plan does your license key activate?")
                print("[1] Weekly")
                print("[2] Monthly")
                print("[3] Quarterly")
                print("[4] Yearly")
                print("[5] Lifetime")
                
                plan_choice = input("\nChoice: ")
                plan_map = {
                    "1": SubscriptionPlan.WEEKLY,
                    "2": SubscriptionPlan.MONTHLY,
                    "3": SubscriptionPlan.QUARTERLY,
                    "4": SubscriptionPlan.YEARLY,
                    "5": SubscriptionPlan.LIFETIME
                }
                
                if plan_choice in plan_map:
                    license_key = input("Enter your license key: ").strip()
                    success, msg = subscription_manager.activate_subscription(
                        current_profile.trader_id, 
                        plan_map[plan_choice], 
                        license_key
                    )
                    if success:
                        print(f"\n{Fore.GREEN}✅ {msg}")
                        current_profile.has_subscription = True
                        profile_manager.save_profiles()
                    else:
                        print(f"\n{Fore.RED}❌ {msg}")
                        return
                else:
                    print("Invalid choice. Exiting...")
                    return
            
            elif sub_choice == "4":
                success, msg = subscription_manager.interactive_subscription(current_profile.trader_id)
                if success:
                    print(f"\n{Fore.GREEN}✅ {msg}")
                    current_profile.has_subscription = True
                    profile_manager.save_profiles()
                else:
                    print(f"\n{Fore.RED}❌ {msg}")
                    return
            else:
                print("Exiting...")
                return
        else:
            # Subscription is valid
            print(f"\n{Fore.GREEN}✅ {message}")
            current_profile.has_subscription = True
            current_profile.subscription_checked = True
            profile_manager.save_profiles()
    
    # Create and initialize bot
    bot = SMCTradingBot(trader_profile=current_profile)
    
    if not bot.initialize():
        logger.error("Bot initialization failed. Exiting...")
        return
    
    # Show menu options
    print("\n" + "=" * 70)
    print("MENU OPTIONS")
    print("=" * 70)
    print("[1] Start Trading Bot")
    print("[2] View Trade History & Statistics")
    print("[3] View Subscription Status")
    print("[4] Manage Subscription")
    print("[5] Exit")
    print("=" * 70)
    
    menu_choice = input("\nChoice: ")
    
    if menu_choice == "1":
        # Final subscription check before trading
        if current_profile:
            is_valid, msg = subscription_manager.validate_subscription(current_profile.trader_id)
            if not is_valid:
                print(f"\n{Fore.RED}❌ Cannot start trading: {msg}")
                return
            print(f"\n{Fore.GREEN}✅ Subscription validated. Starting bot...")
        
        # Run the bot - Analysis every 5 minutes (300 seconds)
        bot.run(interval_seconds=300)
    
    elif menu_choice == "2":
        # Show trade analysis
        if current_profile:
            from dashboard.trade_analyzer import TradeAnalyzer
            analyzer = TradeAnalyzer(current_profile.trade_history_file)
        else:
            analyzer = bot.analyzer
        
        analyzer.print_statistics()
        analyzer.print_recent_trades(10)
        
        # Ask if user wants to export
        export = input("\nExport to CSV? (y/n): ")
        if export.lower() == 'y':
            filename = input("Enter filename [trade_report.csv]: ") or "trade_report.csv"
            analyzer.export_to_csv(filename)
    
    elif menu_choice == "3":
        # View subscription status
        if current_profile:
            subscription_manager.display_subscription_status(current_profile.trader_id)
        else:
            print(f"\n{Fore.YELLOW}No profile selected. Subscription features require a trader profile.")
    
    elif menu_choice == "4":
        # Manage subscription
        if current_profile:
            print("\n" + "=" * 70)
            print("SUBSCRIPTION MANAGEMENT")
            print("=" * 70)
            print("[1] View Status")
            print("[2] Renew Subscription")
            print("[3] Change Plan")
            print("[0] Back")
            
            sub_mgmt = input("\nChoice: ")
            
            if sub_mgmt == "1":
                subscription_manager.display_subscription_status(current_profile.trader_id)
            elif sub_mgmt in ["2", "3"]:
                success, msg = subscription_manager.interactive_subscription(current_profile.trader_id)
                print(f"\n{Fore.GREEN if success else Fore.RED}{'✅' if success else '❌'} {msg}")
        else:
            print(f"\n{Fore.YELLOW}No profile selected. Subscription features require a trader profile.")
    
    else:
        print("Exiting...")


if __name__ == "__main__":
    main()
