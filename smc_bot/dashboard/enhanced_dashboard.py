"""
Enhanced Real-Time Trading Dashboard for SMC Bot

NEW FEATURES:
- Auto-refresh every 5 seconds
- Live market price updates
- Enhanced visual metrics
- Trade execution timeline
- Performance charts (ASCII)
- System health monitoring
"""

import os
import sys
import time
import threading
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from colorama import Fore, Back, Style, init
import MetaTrader5 as mt5

init(autoreset=True)


class EnhancedDashboard:
    """Enhanced real-time dashboard with auto-refresh and advanced metrics."""
    
    def __init__(self, symbol: str = "XAUUSD", refresh_interval: int = 5):
        """
        Initialize enhanced dashboard.
        
        Args:
            symbol: Trading symbol
            refresh_interval: Refresh interval in seconds
        """
        self.symbol = symbol
        self.refresh_interval = refresh_interval
        self.running = False
        self.refresh_thread = None
        
        # State tracking
        self.last_signal = "NONE"
        self.last_signal_time = None
        self.positions_count = 0
        self.account_balance = 0.0
        self.account_equity = 0.0
        self.drawdown_percent = 0.0
        self.current_price = 0.0
        
        # Performance tracking
        self.trades_today = 0
        self.profit_today = 0.0
        self.win_streak = 0
        self.loss_streak = 0
        
        # System health
        self.last_update = datetime.now()
        self.api_status = "Unknown"
        self.connection_status = "Unknown"
        
        # Trade execution history (last 10)
        self.execution_history = []
        
    def clear_screen(self):
        """Clear console screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_live_price(self) -> float:
        """Get current market price from MT5."""
        try:
            tick = mt5.symbol_info_tick(self.symbol)
            if tick:
                self.current_price = tick.bid
                self.api_status = "✅ Connected"
                return tick.bid
        except:
            self.api_status = "❌ Disconnected"
        return 0.0
    
    def draw_price_chart(self, prices: List[float], height: int = 10, width: int = 60):
        """
        Draw ASCII price chart.
        
        Args:
            prices: List of price points
            height: Chart height
            width: Chart width
        """
        if not prices or len(prices) < 2:
            return
        
        min_price = min(prices)
        max_price = max(prices)
        price_range = max_price - min_price if max_price != min_price else 1
        
        # Normalize prices to chart height
        normalized = [(p - min_price) / price_range * (height - 1) for p in prices]
        
        # Draw chart
        print(Fore.YELLOW + f"\n📈 PRICE CHART (Last {len(prices)} ticks):")
        print(Fore.WHITE + "─" * 80)
        
        for y in range(height - 1, -1, -1):
            line = f"{max_price - (y / (height - 1) * price_range):8.2f} │ "
            
            for x, val in enumerate(normalized):
                if abs(val - y) < 0.5:
                    line += "█"
                elif y == 0:
                    line += "▁"
                else:
                    line += " "
            
            if y == height - 1:
                print(Fore.GREEN + line)
            elif y == 0:
                print(Fore.RED + line)
            else:
                print(Fore.CYAN + line)
        
        # X-axis
        print(Fore.WHITE + "         └" + "─" * len(normalized))
    
    def print_header_enhanced(self):
        """Print enhanced header with live price."""
        print(Fore.CYAN + Style.BRIGHT + "═" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 16 + "XAUUSD SMC/ICT TRADING BOT - LIVE DASHBOARD" + " " * 20 + "║")
        print(Fore.CYAN + Style.BRIGHT + "═" * 80)
        
        # Real-time info bar
        now = datetime.now()
        print(Fore.WHITE + f"║  🕐 {now.strftime('%Y-%m-%d %H:%M:%S')}" + " " * 20 + 
              f"💰 Live Price: ${self.current_price:,.2f}" + " " * 10 + "║")
        print(Fore.CYAN + Style.BRIGHT + "═" * 80)
    
    def print_subscription_enhanced(self, subscription_data: Dict[str, Any] = None):
        """Print enhanced subscription info with visual indicator."""
        if not subscription_data:
            return
        
        is_valid = subscription_data.get('is_valid', False)
        plan = subscription_data.get('plan', 'N/A')
        days_remaining = subscription_data.get('days_remaining', 0)
        expiry = subscription_data.get('expiry_date', 'N/A')
        
        if is_valid:
            if days_remaining <= 3:
                sub_color = Fore.RED
                icon = "⚠️"
                urgency = "URGENT"
            elif days_remaining <= 7:
                sub_color = Fore.YELLOW
                icon = "⏰"
                urgency = "EXPIRING SOON"
            else:
                sub_color = Fore.GREEN
                icon = "✅"
                urgency = "ACTIVE"
            
            # Subscription progress bar
            total_days = 30  # Assuming monthly subscription
            progress = (total_days - days_remaining) / total_days
            bar_length = 40
            filled = int(progress * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            print(sub_color + f"║  {icon} Subscription: {plan.upper()} - {urgency}")
            print(sub_color + f"║     [{bar}] {days_remaining} days left")
            print(sub_color + f"║     Expires: {expiry}")
        else:
            print(Fore.RED + "║  ❌ Subscription: EXPIRED - Bot functionality limited")
            print(Fore.RED + "║     Please renew to continue trading")
        
        print(Fore.CYAN + Style.BRIGHT + "═" * 80)
    
    def print_system_health(self):
        """Print system health indicators."""
        uptime = datetime.now() - self.last_update
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "🔧 SYSTEM HEALTH:")
        print(Fore.WHITE + "─" * 80)
        
        # API Connection
        print(f"   MT5 API:       {self.api_status}")
        
        # Connection status
        conn_color = Fore.GREEN if "Connected" in self.connection_status else Fore.RED
        print(conn_color + f"   Connection:    {self.connection_status}")
        
        # Last update
        seconds_ago = (datetime.now() - self.last_update).seconds
        update_color = Fore.GREEN if seconds_ago < 10 else Fore.YELLOW if seconds_ago < 30 else Fore.RED
        print(update_color + f"   Last Update:   {seconds_ago}s ago")
        
        # Memory/CPU (placeholder)
        print(Fore.CYAN + f"   Bot Status:    Running ✓")
    
    def print_daily_performance(self):
        """Print today's performance summary."""
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📊 TODAY'S PERFORMANCE:")
        print(Fore.WHITE + "─" * 80)
        
        # Trades count
        print(Fore.CYAN + f"   Trades Today:  {self.trades_today}")
        
        # P/L today
        profit_color = Fore.GREEN if self.profit_today >= 0 else Fore.RED
        profit_symbol = "+" if self.profit_today >= 0 else ""
        print(profit_color + Style.BRIGHT + f"   P/L Today:     {profit_symbol}${self.profit_today:.2f}")
        
        # Streak
        if self.win_streak > 0:
            print(Fore.GREEN + f"   Win Streak:    {self.win_streak} 🔥")
        elif self.loss_streak > 0:
            print(Fore.RED + f"   Loss Streak:   {self.loss_streak} ⚠️")
        else:
            print(Fore.WHITE + f"   Streak:        None")
    
    def print_signal_status_enhanced(self, signal: str = None, confidence: float = 0.0):
        """
        Print enhanced signal status with confidence meter.
        
        Args:
            signal: Current signal (BUY/SELL/NONE)
            confidence: Signal confidence (0-100)
        """
        if signal:
            self.last_signal = signal
            self.last_signal_time = datetime.now()
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📊 SIGNAL STATUS:")
        print(Fore.WHITE + "─" * 80)
        
        if self.last_signal == "BUY":
            print(Fore.GREEN + Style.BRIGHT + Back.GREEN + "   🔼 BUY SIGNAL ACTIVE   " + Style.RESET_ALL)
            color = Fore.GREEN
        elif self.last_signal == "SELL":
            print(Fore.RED + Style.BRIGHT + Back.RED + "   🔽 SELL SIGNAL ACTIVE   " + Style.RESET_ALL)
            color = Fore.RED
        else:
            print(Fore.WHITE + Style.DIM + "   ⏸️  NO SIGNAL - Scanning market...")
            color = Fore.WHITE
        
        # Signal time
        if self.last_signal_time:
            elapsed = datetime.now() - self.last_signal_time
            print(color + f"   Detected:      {self.last_signal_time.strftime('%H:%M:%S')} ({elapsed.seconds}s ago)")
        
        # Confidence meter
        if confidence > 0:
            bar_length = 40
            filled = int((confidence / 100) * bar_length)
            bar = "█" * filled + "░" * (bar_length - filled)
            
            conf_color = Fore.GREEN if confidence >= 70 else Fore.YELLOW if confidence >= 50 else Fore.RED
            print(conf_color + f"   Confidence:    [{bar}] {confidence:.1f}%")
    
    def print_execution_history(self):
        """Print recent trade executions timeline."""
        if not self.execution_history:
            return
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "⏱️  RECENT EXECUTIONS:")
        print(Fore.WHITE + "─" * 80)
        
        for execution in self.execution_history[-5:]:
            signal = execution.get('signal', 'UNKNOWN')
            time_str = execution.get('time', 'N/A')
            price = execution.get('price', 0)
            profit = execution.get('profit', None)
            
            color = Fore.GREEN if signal == 'BUY' else Fore.RED
            symbol = "🔼" if signal == 'BUY' else "🔽"
            
            status_line = f"   {symbol} {time_str} - {signal} @ ${price:.2f}"
            
            if profit is not None:
                profit_color = Fore.GREEN if profit >= 0 else Fore.RED
                profit_symbol = "+" if profit >= 0 else ""
                status_line += profit_color + f" → {profit_symbol}${profit:.2f}"
            else:
                status_line += Fore.YELLOW + " → OPEN"
            
            print(color + status_line)
    
    def add_execution(self, signal: str, price: float, profit: float = None):
        """
        Add a trade execution to history.
        
        Args:
            signal: Trade signal (BUY/SELL)
            price: Execution price
            profit: Profit if closed (None if open)
        """
        execution = {
            'signal': signal,
            'time': datetime.now().strftime('%H:%M:%S'),
            'price': price,
            'profit': profit
        }
        self.execution_history.append(execution)
        
        # Keep only last 10
        if len(self.execution_history) > 10:
            self.execution_history = self.execution_history[-10:]
    
    def display_full_enhanced(self, data: Dict[str, Any]):
        """
        Display full enhanced dashboard.
        
        Args:
            data: Complete dashboard data
        """
        self.clear_screen()
        
        # Update live price
        self.get_live_price()
        
        # Update timestamp
        self.last_update = datetime.now()
        
        # Header with live price
        self.print_header_enhanced()
        
        # Subscription
        subscription = data.get('subscription')
        if subscription:
            self.print_subscription_enhanced(subscription)
        
        # Signal status
        signal_data = data.get('signal_data', {})
        self.print_signal_status_enhanced(
            signal_data.get('signal'),
            signal_data.get('confidence', 0)
        )
        
        # Account info
        account = data.get('account', {})
        self.account_balance = account.get('balance', 0)
        self.account_equity = account.get('equity', 0)
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "💰 ACCOUNT:")
        print(Fore.WHITE + "─" * 80)
        print(Fore.CYAN + f"   Balance:       ${self.account_balance:,.2f}")
        print(Fore.CYAN + f"   Equity:        ${self.account_equity:,.2f}")
        
        profit = account.get('profit', 0)
        profit_color = Fore.GREEN if profit >= 0 else Fore.RED
        profit_symbol = "+" if profit >= 0 else ""
        print(profit_color + Style.BRIGHT + f"   Floating P/L:  {profit_symbol}${profit:.2f}")
        
        # Risk metrics
        risk = data.get('risk', {})
        drawdown = risk.get('drawdown', 0)
        max_dd = risk.get('max_drawdown', 5.0)
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "🛡️  RISK:")
        print(Fore.WHITE + "─" * 80)
        
        dd_percent = (drawdown / max_dd) * 100 if max_dd > 0 else 0
        if dd_percent < 50:
            dd_color = Fore.GREEN
            status = "Safe"
        elif dd_percent < 80:
            dd_color = Fore.YELLOW
            status = "Moderate"
        else:
            dd_color = Fore.RED
            status = "High"
        
        print(dd_color + f"   Drawdown:      {drawdown:.2f}% / {max_dd:.2f}% ({status})")
        
        # Risk bar
        bar_length = 50
        filled = int(dd_percent / 100 * bar_length) if dd_percent <= 100 else bar_length
        bar = "█" * filled + "░" * (bar_length - filled)
        print(dd_color + f"   [{bar}]")
        
        # Positions
        positions = data.get('positions', {})
        positions_count = positions.get('count', 0)
        positions_data = positions.get('data', [])
        
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📈 POSITIONS:")
        print(Fore.WHITE + "─" * 80)
        
        if positions_count == 0:
            print(Fore.WHITE + Style.DIM + "   No open positions")
        else:
            print(Fore.CYAN + f"   Open: {positions_count}")
            
            for pos in positions_data[:3]:  # Show max 3
                signal_type = pos.get('type', 'UNKNOWN')
                color = Fore.GREEN if signal_type == 'BUY' else Fore.RED
                symbol = "🔼" if signal_type == 'BUY' else "🔽"
                
                profit = pos.get('profit', 0)
                profit_color = Fore.GREEN if profit >= 0 else Fore.RED
                profit_symbol = "+" if profit >= 0 else ""
                
                print(color + f"   {symbol} {signal_type} #{pos.get('ticket', 'N/A')}: " +
                      profit_color + f"{profit_symbol}${profit:.2f}")
        
        # Daily performance
        self.trades_today = data.get('trades_today', 0)
        self.profit_today = data.get('profit_today', 0)
        self.win_streak = data.get('win_streak', 0)
        self.loss_streak = data.get('loss_streak', 0)
        self.print_daily_performance()
        
        # Execution history
        self.print_execution_history()
        
        # System health
        self.print_system_health()
        
        # Footer
        print("\n" + Fore.CYAN + Style.BRIGHT + "═" * 80)
        print(Fore.WHITE + Style.DIM + f"   Auto-refresh: {self.refresh_interval}s │ Press Ctrl+C to stop")
        print(Fore.CYAN + Style.BRIGHT + "═" * 80 + "\n")


# Singleton
_enhanced_dashboard = None

def get_enhanced_dashboard() -> EnhancedDashboard:
    """Get or create enhanced dashboard instance."""
    global _enhanced_dashboard
    if _enhanced_dashboard is None:
        _enhanced_dashboard = EnhancedDashboard()
    return _enhanced_dashboard
