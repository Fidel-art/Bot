"""
Trade History Analyzer for SMC Bot

Loads and analyzes historical trade data:
- Trade performance statistics
- Win rate and profit factor
- Best and worst trades
- Visual charts and reports
- Export capabilities
"""

import json
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional
from colorama import Fore, Style, init

init(autoreset=True)


class TradeAnalyzer:
    """Analyzes historical trade performance."""
    
    def __init__(self, trades_file: str = "data/trade_history.json"):
        """
        Initialize the trade analyzer.
        
        Args:
            trades_file: Path to the trade history JSON file
        """
        self.trades_file = Path(trades_file)
        self.trades = []
        self.load_trades()
    
    def load_trades(self):
        """Load trades from JSON file."""
        if self.trades_file.exists():
            try:
                with open(self.trades_file, 'r') as f:
                    self.trades = json.load(f)
                print(Fore.GREEN + f"✅ Loaded {len(self.trades)} trades from history")
            except Exception as e:
                print(Fore.RED + f"❌ Error loading trades: {e}")
                self.trades = []
        else:
            print(Fore.YELLOW + "⚠️  No trade history found. File will be created on first trade.")
            self.trades = []
    
    def save_trade(self, trade: Dict[str, Any]):
        """
        Save a new trade to history.
        
        Args:
            trade: Trade data dictionary
        """
        self.trades.append(trade)
        
        # Ensure directory exists
        self.trades_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Save to file
        try:
            with open(self.trades_file, 'w') as f:
                json.dump(self.trades, f, indent=2)
            print(Fore.GREEN + f"✅ Trade saved to history (Total: {len(self.trades)})")
        except Exception as e:
            print(Fore.RED + f"❌ Error saving trade: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Calculate comprehensive trade statistics.
        
        Returns:
            Dictionary with performance metrics
        """
        if not self.trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0.0,
                'total_profit': 0.0,
                'average_profit': 0.0,
                'largest_win': 0.0,
                'largest_loss': 0.0,
                'profit_factor': 0.0,
                'average_rr': 0.0
            }
        
        total_trades = len(self.trades)
        winning_trades = [t for t in self.trades if t.get('profit', 0) > 0]
        losing_trades = [t for t in self.trades if t.get('profit', 0) < 0]
        breakeven_trades = [t for t in self.trades if t.get('profit', 0) == 0]
        
        total_profit = sum(t.get('profit', 0) for t in self.trades)
        gross_profit = sum(t.get('profit', 0) for t in winning_trades)
        gross_loss = abs(sum(t.get('profit', 0) for t in losing_trades))
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        avg_profit = total_profit / total_trades if total_trades > 0 else 0
        
        largest_win = max((t.get('profit', 0) for t in self.trades), default=0)
        largest_loss = min((t.get('profit', 0) for t in self.trades), default=0)
        
        profit_factor = (gross_profit / gross_loss) if gross_loss > 0 else 0
        
        # Calculate average risk-reward
        avg_rr = 0
        if winning_trades:
            rr_values = [t.get('risk_reward', 0) for t in winning_trades if t.get('risk_reward', 0) > 0]
            avg_rr = sum(rr_values) / len(rr_values) if rr_values else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'breakeven_trades': len(breakeven_trades),
            'win_rate': win_rate,
            'total_profit': total_profit,
            'average_profit': avg_profit,
            'largest_win': largest_win,
            'largest_loss': largest_loss,
            'gross_profit': gross_profit,
            'gross_loss': gross_loss,
            'profit_factor': profit_factor,
            'average_rr': avg_rr
        }
    
    def print_statistics(self):
        """Print formatted statistics to console."""
        stats = self.get_statistics()
        
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 25 + "TRADE PERFORMANCE ANALYSIS" + " " * 28 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80)
        
        # Overall Statistics
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📊 OVERALL STATISTICS:")
        print(Fore.WHITE + "─" * 80)
        print(Fore.CYAN + f"   Total Trades:      {stats['total_trades']}")
        print(Fore.GREEN + f"   Winning Trades:    {stats['winning_trades']}")
        print(Fore.RED + f"   Losing Trades:     {stats['losing_trades']}")
        print(Fore.WHITE + f"   Breakeven Trades:  {stats['breakeven_trades']}")
        
        # Win Rate
        print("\n" + Fore.YELLOW + Style.BRIGHT + "🎯 WIN RATE:")
        print(Fore.WHITE + "─" * 80)
        
        win_rate = stats['win_rate']
        if win_rate >= 60:
            wr_color = Fore.GREEN
            wr_status = "Excellent"
        elif win_rate >= 50:
            wr_color = Fore.YELLOW
            wr_status = "Good"
        else:
            wr_color = Fore.RED
            wr_status = "Needs Improvement"
        
        print(wr_color + Style.BRIGHT + f"   {win_rate:.2f}% ({wr_status})")
        
        # Draw win rate bar
        bar_length = 50
        filled = int((win_rate / 100) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        print(wr_color + f"   [{bar}]")
        
        # Profit Statistics
        print("\n" + Fore.YELLOW + Style.BRIGHT + "💰 PROFIT ANALYSIS:")
        print(Fore.WHITE + "─" * 80)
        
        total_profit = stats['total_profit']
        profit_color = Fore.GREEN if total_profit >= 0 else Fore.RED
        profit_symbol = "+" if total_profit >= 0 else ""
        
        print(profit_color + Style.BRIGHT + f"   Total Profit:      {profit_symbol}${total_profit:.2f}")
        print(Fore.CYAN + f"   Average Profit:    ${stats['average_profit']:.2f}")
        print(Fore.GREEN + f"   Largest Win:       +${stats['largest_win']:.2f}")
        print(Fore.RED + f"   Largest Loss:      ${stats['largest_loss']:.2f}")
        print(Fore.CYAN + f"   Gross Profit:      +${stats['gross_profit']:.2f}")
        print(Fore.CYAN + f"   Gross Loss:        -${stats['gross_loss']:.2f}")
        
        # Profit Factor
        print("\n" + Fore.YELLOW + Style.BRIGHT + "📈 PROFIT FACTOR:")
        print(Fore.WHITE + "─" * 80)
        
        pf = stats['profit_factor']
        if pf >= 2.0:
            pf_color = Fore.GREEN
            pf_status = "Excellent"
        elif pf >= 1.5:
            pf_color = Fore.YELLOW
            pf_status = "Good"
        elif pf >= 1.0:
            pf_color = Fore.YELLOW
            pf_status = "Profitable"
        else:
            pf_color = Fore.RED
            pf_status = "Losing"
        
        print(pf_color + Style.BRIGHT + f"   {pf:.2f} ({pf_status})")
        print(Fore.WHITE + Style.DIM + f"   (Profit Factor = Gross Profit / Gross Loss)")
        
        # Risk-Reward
        print("\n" + Fore.YELLOW + Style.BRIGHT + "⚖️  RISK-REWARD:")
        print(Fore.WHITE + "─" * 80)
        print(Fore.CYAN + f"   Average R:R:       {stats['average_rr']:.2f}")
        
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
    
    def print_recent_trades(self, count: int = 10):
        """
        Print recent trades.
        
        Args:
            count: Number of recent trades to display
        """
        if not self.trades:
            print(Fore.YELLOW + "⚠️  No trades to display")
            return
        
        recent = self.trades[-count:]
        
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + f"║{' ' * 28}RECENT TRADES (Last {len(recent)}){' ' * 28}║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
        
        for i, trade in enumerate(reversed(recent), 1):
            signal = trade.get('signal', 'N/A')
            profit = trade.get('profit', 0)
            entry_time = trade.get('entry_time', 'N/A')
            exit_time = trade.get('exit_time', 'N/A')
            
            # Color based on signal
            signal_color = Fore.GREEN if signal == 'BUY' else Fore.RED
            symbol = "🔼" if signal == 'BUY' else "🔽"
            
            # Color based on profit
            profit_color = Fore.GREEN if profit > 0 else Fore.RED if profit < 0 else Fore.WHITE
            profit_symbol = "+" if profit > 0 else ""
            
            print(Fore.YELLOW + f"Trade #{len(self.trades) - i + 1}:")
            print(signal_color + f"   {symbol} {signal}")
            print(Fore.CYAN + f"   Entry:  {entry_time}")
            print(Fore.CYAN + f"   Exit:   {exit_time}")
            print(Fore.CYAN + f"   Price:  ${trade.get('entry_price', 0):.2f}")
            print(Fore.CYAN + f"   Lots:   {trade.get('lots', 0):.3f}")
            print(profit_color + Style.BRIGHT + f"   Profit: {profit_symbol}${profit:.2f}")
            print(Fore.WHITE + "─" * 80)
        
        print()
    
    def export_to_csv(self, filename: str = "trade_report.csv"):
        """
        Export trade history to CSV file.
        
        Args:
            filename: Output CSV filename
        """
        if not self.trades:
            print(Fore.YELLOW + "⚠️  No trades to export")
            return
        
        filepath = Path(filename)
        
        try:
            with open(filepath, 'w', newline='') as f:
                if self.trades:
                    writer = csv.DictWriter(f, fieldnames=self.trades[0].keys())
                    writer.writeheader()
                    writer.writerows(self.trades)
            
            print(Fore.GREEN + f"✅ Exported {len(self.trades)} trades to {filepath}")
        except Exception as e:
            print(Fore.RED + f"❌ Error exporting to CSV: {e}")
    
    def get_trades_by_type(self, signal_type: str) -> List[Dict]:
        """
        Get trades filtered by signal type.
        
        Args:
            signal_type: 'BUY' or 'SELL'
            
        Returns:
            List of trades matching the signal type
        """
        return [t for t in self.trades if t.get('signal') == signal_type]
    
    def get_trades_by_date_range(self, start_date: str, end_date: str) -> List[Dict]:
        """
        Get trades within a date range.
        
        Args:
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            
        Returns:
            List of trades in the date range
        """
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = datetime.strptime(end_date, '%Y-%m-%d')
        
        filtered = []
        for trade in self.trades:
            trade_date_str = trade.get('entry_time', '')
            if trade_date_str:
                try:
                    trade_date = datetime.strptime(trade_date_str, '%Y-%m-%d %H:%M:%S')
                    if start <= trade_date <= end:
                        filtered.append(trade)
                except ValueError:
                    continue
        
        return filtered


# Create singleton instance
_analyzer = None

def get_analyzer() -> TradeAnalyzer:
    """Get or create analyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = TradeAnalyzer()
    return _analyzer
