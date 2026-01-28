"""
Real-Time Trading Dashboard for SMC Bot

Provides visual display of:
- Current bot status and activity
- Live trade signals (BUY/SELL)
- Position information
- Account statistics
- Risk metrics
"""

import os
import sys
from datetime import datetime
from typing import Optional, Dict, Any
from colorama import Fore, Back, Style, init

# Initialize colorama for Windows support
init(autoreset=True)


class TradingDashboard:
    """Real-time dashboard for displaying bot status and trade activity."""
    
    def __init__(self):
        """Initialize the dashboard."""
        self.last_signal = "NONE"
        self.last_signal_time = None
        self.positions_count = 0
        self.total_profit = 0.0
        self.account_balance = 0.0
        self.account_equity = 0.0
        self.drawdown_percent = 0.0
        
    def clear_screen(self):
        """Clear the console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print the dashboard header."""
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 20 + "XAUUSD SMC/ICT TRADING BOT DASHBOARD" + " " * 22 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.WHITE + f"║  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}" + " " * 60 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
    
    def print_subscription_info(self, subscription_data: Dict[str, Any] = None):
        """
        Print subscription information in header.
        
        Args:
            subscription_data: Subscription details dictionary
        """
        if not subscription_data:
            return
        
        is_valid = subscription_data.get('is_valid', False)
        plan = subscription_data.get('plan', 'N/A')
        days_remaining = subscription_data.get('days_remaining', 0)
        
        if is_valid:
            if days_remaining <= 3:
                sub_color = Fore.RED
                icon = "⚠️"
            elif days_remaining <= 7:
                sub_color = Fore.YELLOW
                icon = "⏰"
            else:
                sub_color = Fore.GREEN
                icon = "✅"
            
            print(sub_color + f"║  {icon} Subscription: {plan.upper()} - {days_remaining} days remaining" + " " * (55 - len(plan) - len(str(days_remaining))) + "║")
        else:
            print(Fore.RED + "║  ❌ Subscription: EXPIRED - Please renew" + " " * 35 + "║")
        
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
    
    def print_signal_status(self, signal: str = None):
        """
        Print current signal status with visual indicator.
        
        Args:
            signal: Current trade signal (BUY, SELL, NONE)
        """
        if signal:
            self.last_signal = signal
            self.last_signal_time = datetime.now()
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📊 CURRENT SIGNAL STATUS:")
        print(Fore.WHITE + "─" * 80)
        
        if self.last_signal == "BUY":
            print(Fore.GREEN + Style.BRIGHT + Back.GREEN + "   🔼 BUY SIGNAL ACTIVE   " + Style.RESET_ALL)
            print(Fore.GREEN + f"   Detected at: {self.last_signal_time.strftime('%H:%M:%S') if self.last_signal_time else 'N/A'}")
        elif self.last_signal == "SELL":
            print(Fore.RED + Style.BRIGHT + Back.RED + "   🔽 SELL SIGNAL ACTIVE   " + Style.RESET_ALL)
            print(Fore.RED + f"   Detected at: {self.last_signal_time.strftime('%H:%M:%S') if self.last_signal_time else 'N/A'}")
        else:
            print(Fore.WHITE + Style.DIM + "   ⏸️  NO SIGNAL - Analyzing market conditions...")
    
    def print_account_info(self, balance: float, equity: float, profit: float):
        """
        Print account information.
        
        Args:
            balance: Account balance
            equity: Account equity
            profit: Current profit/loss
        """
        self.account_balance = balance
        self.account_equity = equity
        self.total_profit = profit
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "💰 ACCOUNT INFORMATION:")
        print(Fore.WHITE + "─" * 80)
        print(Fore.CYAN + f"   Balance:  ${balance:,.2f}")
        print(Fore.CYAN + f"   Equity:   ${equity:,.2f}")
        
        profit_color = Fore.GREEN if profit >= 0 else Fore.RED
        profit_symbol = "+" if profit >= 0 else ""
        print(profit_color + f"   Profit:   {profit_symbol}${profit:,.2f}")
    
    def print_risk_metrics(self, drawdown: float, remaining: float, max_dd: float):
        """
        Print risk management metrics.
        
        Args:
            drawdown: Current drawdown percentage
            remaining: Remaining drawdown before lock
            max_dd: Maximum allowed drawdown
        """
        self.drawdown_percent = drawdown
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "🛡️  RISK MANAGEMENT:")
        print(Fore.WHITE + "─" * 80)
        
        # Color-code drawdown based on severity
        if drawdown < max_dd * 0.5:
            dd_color = Fore.GREEN
            status = "✅ Safe"
        elif drawdown < max_dd * 0.8:
            dd_color = Fore.YELLOW
            status = "⚠️  Moderate"
        else:
            dd_color = Fore.RED
            status = "🔴 High Risk"
        
        print(dd_color + f"   Current Drawdown: {drawdown:.2f}% {status}")
        print(Fore.CYAN + f"   Remaining Buffer:  {remaining:.2f}%")
        print(Fore.WHITE + f"   Max Allowed:       {max_dd:.2f}%")
        
        # Draw risk bar
        bar_length = 40
        filled = int((drawdown / max_dd) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(dd_color + f"   [{bar}]")
    
    def print_positions(self, positions_count: int, positions_data: list = None):
        """
        Print open positions information.
        
        Args:
            positions_count: Number of open positions
            positions_data: List of position details
        """
        self.positions_count = positions_count
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📈 OPEN POSITIONS:")
        print(Fore.WHITE + "─" * 80)
        
        if positions_count == 0:
            print(Fore.WHITE + Style.DIM + "   No open positions")
        else:
            print(Fore.CYAN + f"   Total Positions: {positions_count}")
            
            if positions_data:
                for i, pos in enumerate(positions_data, 1):
                    signal_type = pos.get('type', 'UNKNOWN')
                    color = Fore.GREEN if signal_type == 'BUY' else Fore.RED
                    symbol = "🔼" if signal_type == 'BUY' else "🔽"
                    
                    print(f"\n   {symbol} Position #{i}:")
                    print(color + f"      Type:   {signal_type}")
                    print(Fore.CYAN + f"      Ticket: {pos.get('ticket', 'N/A')}")
                    print(Fore.CYAN + f"      Lots:   {pos.get('volume', 0):.2f}")
                    print(Fore.CYAN + f"      Entry:  ${pos.get('price', 0):.2f}")
                    print(Fore.CYAN + f"      SL:     ${pos.get('sl', 0):.2f}")
                    print(Fore.CYAN + f"      TP:     ${pos.get('tp', 0):.2f}")
                    
                    profit = pos.get('profit', 0)
                    profit_color = Fore.GREEN if profit >= 0 else Fore.RED
                    profit_symbol = "+" if profit >= 0 else ""
                    print(profit_color + f"      P/L:    {profit_symbol}${profit:.2f}")
    
    def print_trade_notification(self, signal: str, entry: float, sl: float, tp: float, lots: float):
        """
        Print prominent trade execution notification.
        
        Args:
            signal: Trade type (BUY/SELL)
            entry: Entry price
            sl: Stop loss price
            tp: Take profit price
            lots: Position size
        """
        self.clear_screen()
        
        if signal == "BUY":
            color = Fore.GREEN
            bg_color = Back.GREEN
            symbol = "🔼"
            text = "BUY ORDER EXECUTED"
        else:
            color = Fore.RED
            bg_color = Back.RED
            symbol = "🔽"
            text = "SELL ORDER EXECUTED"
        
        print("\n" * 2)
        print(color + Style.BRIGHT + "=" * 80)
        print(bg_color + Fore.WHITE + Style.BRIGHT + f"   {symbol} {text} {symbol}   ".center(80) + Style.RESET_ALL)
        print(color + Style.BRIGHT + "=" * 80)
        print()
        print(color + Style.BRIGHT + f"   Signal:      {signal}")
        print(Fore.CYAN + f"   Entry Price: ${entry:.2f}")
        print(Fore.CYAN + f"   Stop Loss:   ${sl:.2f}")
        print(Fore.CYAN + f"   Take Profit: ${tp:.2f}")
        print(Fore.CYAN + f"   Lot Size:    {lots:.3f}")
        print(Fore.CYAN + f"   Risk/Reward: {abs(tp - entry) / abs(sl - entry):.2f}R")
        print(color + Style.BRIGHT + "=" * 80)
        print(Fore.YELLOW + Style.BRIGHT + "\n   💡 Position is now being monitored...")
        print("\n" * 2)
    
    def print_status_update(self, message: str, status_type: str = "info"):
        """
        Print a status update message.
        
        Args:
            message: Status message
            status_type: Type of status (info, success, warning, error)
        """
        if status_type == "success":
            color = Fore.GREEN
            icon = "✅"
        elif status_type == "warning":
            color = Fore.YELLOW
            icon = "⚠️"
        elif status_type == "error":
            color = Fore.RED
            icon = "❌"
        else:
            color = Fore.CYAN
            icon = "ℹ️"
        
        print(f"\n{color}{icon}  {message}")
    
    def display_full_dashboard(self, data: Dict[str, Any]):
        """
        Display complete dashboard with all information.
        
        Args:
            data: Dictionary containing all dashboard data
        """
        self.clear_screen()
        self.print_header()
        
        # Subscription info (if available)
        subscription = data.get('subscription')
        if subscription:
            self.print_subscription_info(subscription)
        
        # Signal status
        self.print_signal_status(data.get('signal'))
        
        # Account info
        account = data.get('account', {})
        self.print_account_info(
            account.get('balance', 0),
            account.get('equity', 0),
            account.get('profit', 0)
        )
        
        # Risk metrics
        risk = data.get('risk', {})
        self.print_risk_metrics(
            risk.get('drawdown', 0),
            risk.get('remaining', 0),
            risk.get('max_drawdown', 5.0)
        )
        
        # Positions
        positions = data.get('positions', {})
        self.print_positions(
            positions.get('count', 0),
            positions.get('data', [])
        )
        
        # Footer
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.WHITE + Style.DIM + "   Press Ctrl+C to stop the bot")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
    
    def print_footer(self):
        """Print dashboard footer."""
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.WHITE + Style.DIM + "   Bot is running... Press Ctrl+C to stop")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")


# Singleton instance
_dashboard = None

def get_dashboard() -> TradingDashboard:
    """Get or create dashboard instance."""
    global _dashboard
    if _dashboard is None:
        _dashboard = TradingDashboard()
    return _dashboard
