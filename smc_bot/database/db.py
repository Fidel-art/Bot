"""
Database Handler for Web Dashboard

Manages persistent storage for:
- Trader accounts
- Subscriptions
- Trade history
- Bot configurations
"""

import sqlite3
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any
from contextlib import contextmanager


class DatabaseManager:
    """Manages SQLite database for web dashboard."""
    
    def __init__(self, db_path: str = "data/bot_dashboard.db"):
        """
        Initialize database manager.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize_database()
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Return rows as dictionaries
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def initialize_database(self):
        """Create database tables if they don't exist."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Traders table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS traders (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_id TEXT UNIQUE NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP,
                    is_active BOOLEAN DEFAULT 1
                )
            ''')
            
            # Subscriptions table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_id TEXT NOT NULL,
                    plan TEXT NOT NULL,
                    start_date DATE NOT NULL,
                    expiry_date DATE NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    payment_status TEXT DEFAULT 'pending',
                    amount REAL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trader_id) REFERENCES traders (trader_id)
                )
            ''')
            
            # Bot configurations table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_configs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_id TEXT NOT NULL,
                    mt5_login INTEGER NOT NULL,
                    mt5_server TEXT NOT NULL,
                    lot_size REAL DEFAULT 0.01,
                    risk_per_trade REAL DEFAULT 1.0,
                    max_drawdown REAL DEFAULT 5.0,
                    max_trades_per_day INTEGER DEFAULT 3,
                    symbols TEXT DEFAULT '["XAUUSD"]',
                    timeframes TEXT DEFAULT '["D1","H4","H1","M15"]',
                    is_active BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (trader_id) REFERENCES traders (trader_id)
                )
            ''')
            
            # Trade history table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS trades (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_id TEXT NOT NULL,
                    ticket INTEGER,
                    signal TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    entry_price REAL NOT NULL,
                    exit_price REAL,
                    stop_loss REAL,
                    take_profit REAL,
                    lot_size REAL NOT NULL,
                    profit REAL,
                    commission REAL DEFAULT 0,
                    swap REAL DEFAULT 0,
                    entry_time TIMESTAMP NOT NULL,
                    exit_time TIMESTAMP,
                    status TEXT DEFAULT 'open',
                    risk_reward REAL,
                    notes TEXT,
                    FOREIGN KEY (trader_id) REFERENCES traders (trader_id)
                )
            ''')
            
            # Bot sessions table (track bot runs)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS bot_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    trader_id TEXT NOT NULL,
                    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    end_time TIMESTAMP,
                    status TEXT DEFAULT 'running',
                    trades_count INTEGER DEFAULT 0,
                    profit REAL DEFAULT 0,
                    errors TEXT,
                    FOREIGN KEY (trader_id) REFERENCES traders (trader_id)
                )
            ''')
            
            conn.commit()
    
    # ==================== TRADER OPERATIONS ====================
    
    def create_trader(self, trader_id: str, email: str, password_hash: str, name: str) -> bool:
        """
        Create new trader account.
        
        Args:
            trader_id: Unique trader identifier
            email: Trader email
            password_hash: Hashed password
            name: Trader name
            
        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO traders (trader_id, email, password_hash, name)
                    VALUES (?, ?, ?, ?)
                ''', (trader_id, email, password_hash, name))
            return True
        except sqlite3.IntegrityError:
            return False
    
    def get_trader(self, trader_id: str = None, email: str = None) -> Optional[Dict]:
        """
        Get trader by ID or email.
        
        Args:
            trader_id: Trader ID
            email: Trader email
            
        Returns:
            Trader dictionary or None
        """
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if trader_id:
                cursor.execute('SELECT * FROM traders WHERE trader_id = ?', (trader_id,))
            elif email:
                cursor.execute('SELECT * FROM traders WHERE email = ?', (email,))
            else:
                return None
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def update_trader_login(self, trader_id: str):
        """Update last login timestamp."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE traders SET last_login = CURRENT_TIMESTAMP
                WHERE trader_id = ?
            ''', (trader_id,))
    
    # ==================== SUBSCRIPTION OPERATIONS ====================
    
    def create_subscription(self, trader_id: str, plan: str, start_date: str, 
                          expiry_date: str, amount: float) -> bool:
        """
        Create new subscription.
        
        Args:
            trader_id: Trader ID
            plan: Subscription plan (free, monthly, quarterly, vip)
            start_date: Start date (YYYY-MM-DD)
            expiry_date: Expiry date (YYYY-MM-DD)
            amount: Subscription amount
            
        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO subscriptions (trader_id, plan, start_date, expiry_date, amount)
                    VALUES (?, ?, ?, ?, ?)
                ''', (trader_id, plan, start_date, expiry_date, amount))
            return True
        except Exception as e:
            print(f"Error creating subscription: {e}")
            return False
    
    def get_active_subscription(self, trader_id: str) -> Optional[Dict]:
        """Get active subscription for trader."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM subscriptions
                WHERE trader_id = ? AND is_active = 1
                AND expiry_date >= DATE('now')
                ORDER BY expiry_date DESC
                LIMIT 1
            ''', (trader_id,))
            
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def deactivate_expired_subscriptions(self):
        """Deactivate all expired subscriptions."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE subscriptions SET is_active = 0
                WHERE expiry_date < DATE('now') AND is_active = 1
            ''')
    
    # ==================== BOT CONFIG OPERATIONS ====================
    
    def save_bot_config(self, trader_id: str, config: Dict[str, Any]) -> bool:
        """
        Save or update bot configuration.
        
        Args:
            trader_id: Trader ID
            config: Configuration dictionary
            
        Returns:
            True if successful
        """
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Check if config exists
                cursor.execute('SELECT id FROM bot_configs WHERE trader_id = ?', (trader_id,))
                exists = cursor.fetchone()
                
                if exists:
                    # Update
                    cursor.execute('''
                        UPDATE bot_configs SET
                            mt5_login = ?, mt5_server = ?, lot_size = ?,
                            risk_per_trade = ?, max_drawdown = ?, max_trades_per_day = ?,
                            symbols = ?, timeframes = ?, updated_at = CURRENT_TIMESTAMP
                        WHERE trader_id = ?
                    ''', (
                        config.get('mt5_login'),
                        config.get('mt5_server'),
                        config.get('lot_size', 0.01),
                        config.get('risk_per_trade', 1.0),
                        config.get('max_drawdown', 5.0),
                        config.get('max_trades_per_day', 3),
                        json.dumps(config.get('symbols', ['XAUUSD'])),
                        json.dumps(config.get('timeframes', ['D1', 'H4', 'H1', 'M15'])),
                        trader_id
                    ))
                else:
                    # Insert
                    cursor.execute('''
                        INSERT INTO bot_configs 
                        (trader_id, mt5_login, mt5_server, lot_size, risk_per_trade, 
                         max_drawdown, max_trades_per_day, symbols, timeframes)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        trader_id,
                        config.get('mt5_login'),
                        config.get('mt5_server'),
                        config.get('lot_size', 0.01),
                        config.get('risk_per_trade', 1.0),
                        config.get('max_drawdown', 5.0),
                        config.get('max_trades_per_day', 3),
                        json.dumps(config.get('symbols', ['XAUUSD'])),
                        json.dumps(config.get('timeframes', ['D1', 'H4', 'H1', 'M15']))
                    ))
            return True
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
    
    def get_bot_config(self, trader_id: str) -> Optional[Dict]:
        """Get bot configuration for trader."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM bot_configs WHERE trader_id = ?', (trader_id,))
            
            row = cursor.fetchone()
            if row:
                config = dict(row)
                config['symbols'] = json.loads(config['symbols'])
                config['timeframes'] = json.loads(config['timeframes'])
                return config
            return None
    
    def set_bot_status(self, trader_id: str, is_active: bool) -> bool:
        """Set bot active/inactive status."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE bot_configs SET is_active = ?
                    WHERE trader_id = ?
                ''', (1 if is_active else 0, trader_id))
            return True
        except:
            return False
    
    # ==================== TRADE HISTORY OPERATIONS ====================
    
    def save_trade(self, trader_id: str, trade: Dict[str, Any]) -> bool:
        """Save trade to history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO trades 
                    (trader_id, ticket, signal, symbol, entry_price, exit_price, stop_loss,
                     take_profit, lot_size, profit, entry_time, exit_time, status, risk_reward)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    trader_id,
                    trade.get('ticket'),
                    trade.get('signal'),
                    trade.get('symbol', 'XAUUSD'),
                    trade.get('entry_price'),
                    trade.get('exit_price'),
                    trade.get('stop_loss'),
                    trade.get('take_profit'),
                    trade.get('lot_size'),
                    trade.get('profit'),
                    trade.get('entry_time'),
                    trade.get('exit_time'),
                    trade.get('status', 'closed'),
                    trade.get('risk_reward')
                ))
            return True
        except Exception as e:
            print(f"Error saving trade: {e}")
            return False
    
    def get_trades(self, trader_id: str, limit: int = 100) -> List[Dict]:
        """Get trade history for trader."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM trades
                WHERE trader_id = ?
                ORDER BY entry_time DESC
                LIMIT ?
            ''', (trader_id, limit))
            
            return [dict(row) for row in cursor.fetchall()]
    
    def get_performance_stats(self, trader_id: str) -> Dict[str, Any]:
        """Calculate performance statistics for trader."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Get all closed trades
            cursor.execute('''
                SELECT profit FROM trades
                WHERE trader_id = ? AND status = 'closed' AND profit IS NOT NULL
            ''', (trader_id,))
            
            trades = [row['profit'] for row in cursor.fetchall()]
            
            if not trades:
                return {
                    'total_trades': 0,
                    'win_rate': 0,
                    'total_profit': 0,
                    'average_profit': 0,
                    'best_trade': 0,
                    'worst_trade': 0
                }
            
            wins = [t for t in trades if t > 0]
            losses = [t for t in trades if t < 0]
            
            return {
                'total_trades': len(trades),
                'winning_trades': len(wins),
                'losing_trades': len(losses),
                'win_rate': (len(wins) / len(trades) * 100) if trades else 0,
                'total_profit': sum(trades),
                'average_profit': sum(trades) / len(trades),
                'best_trade': max(trades),
                'worst_trade': min(trades),
                'profit_factor': (sum(wins) / abs(sum(losses))) if losses else 0
            }


# Singleton instance
_db_manager = None

def get_db_manager() -> DatabaseManager:
    """Get or create database manager instance."""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager
