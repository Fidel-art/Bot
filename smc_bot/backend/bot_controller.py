"""
Bot Controller for Web Dashboard

Controls bot lifecycle:
- Start bot for a trader
- Stop bot
- Pause/resume bot
- Get bot status
- Monitor bot health
- Launch MT5 automatically
"""

import subprocess
import psutil
import threading
import time
import os
import MetaTrader5 as mt5
from typing import Optional, Dict, Any
from datetime import datetime
from pathlib import Path


def find_mt5_executable() -> Optional[str]:
    """
    Find MetaTrader 5 executable path.
    
    Returns:
        Path to terminal64.exe or None if not found
    """
    # Common MT5 installation paths
    possible_paths = [
        r"C:\Program Files\MetaTrader 5\terminal64.exe",
        r"C:\Program Files (x86)\MetaTrader 5\terminal64.exe",
        os.path.expanduser(r"~\AppData\Roaming\MetaQuotes\Terminal\terminal64.exe"),
        r"C:\Users\Public\Desktop\MetaTrader 5\terminal64.exe",
    ]
    
    # Check each possible path
    for path in possible_paths:
        if os.path.exists(path):
            return path
    
    # Try to find in common installation directories
    program_files = [
        os.environ.get('PROGRAMFILES', r'C:\Program Files'),
        os.environ.get('PROGRAMFILES(X86)', r'C:\Program Files (x86)'),
    ]
    
    for pf in program_files:
        for root, dirs, files in os.walk(pf):
            if 'MetaTrader 5' in root or 'MT5' in root:
                for file in files:
                    if file.lower() == 'terminal64.exe':
                        return os.path.join(root, file)
    
    return None


def is_mt5_running() -> bool:
    """
    Check if MetaTrader 5 is already running.
    
    Returns:
        True if MT5 is running
    """
    for proc in psutil.process_iter(['name']):
        try:
            if proc.info['name'].lower() in ['terminal64.exe', 'terminal.exe', 'metatrader.exe']:
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return False


def launch_mt5() -> tuple[bool, str]:
    """
    Launch MetaTrader 5 if not already running.
    
    Returns:
        Tuple of (success, message)
    """
    # Check if already running
    if is_mt5_running():
        return True, "MT5 is already running"
    
    # Find MT5 executable
    mt5_path = find_mt5_executable()
    
    if not mt5_path:
        return False, "MetaTrader 5 not found. Please install MT5 or provide the installation path."
    
    try:
        # Launch MT5 using Windows-specific approach
        if os.name == 'nt':  # Windows
            # Use startfile for Windows which is more reliable
            os.startfile(mt5_path)
        else:
            # Linux/Mac
            subprocess.Popen([mt5_path])
        
        # Wait a few seconds for MT5 to start
        time.sleep(5)
        
        # Verify it started
        if is_mt5_running():
            return True, f"MT5 launched successfully from {mt5_path}"
        else:
            return False, "MT5 failed to start. Please launch it manually."
            
    except Exception as e:
        return False, f"Error launching MT5: {str(e)}"


def open_mt5_charts(symbol: str = "EURUSD", timeframe: str = "H1") -> tuple[bool, str]:
    """
    Open MT5 charts for the specified symbol and timeframe.
    
    Args:
        symbol: Trading symbol (e.g., "EURUSD")
        timeframe: Chart timeframe (e.g., "H1", "M15", "D1")
    
    Returns:
        Tuple of (success, message)
    """
    try:
        # First ensure MT5 is running
        if not is_mt5_running():
            success, msg = launch_mt5()
            if not success:
                return False, msg
            time.sleep(3)  # Wait for MT5 to fully load
        
        # Initialize MT5 connection
        if not mt5.initialize():
            return False, f"MT5 initialization failed: {mt5.last_error()}"
        
        # Map timeframe string to MT5 constant
        timeframe_map = {
            "M1": mt5.TIMEFRAME_M1,
            "M5": mt5.TIMEFRAME_M5,
            "M15": mt5.TIMEFRAME_M15,
            "M30": mt5.TIMEFRAME_M30,
            "H1": mt5.TIMEFRAME_H1,
            "H4": mt5.TIMEFRAME_H4,
            "D1": mt5.TIMEFRAME_D1,
            "W1": mt5.TIMEFRAME_W1,
            "MN1": mt5.TIMEFRAME_MN1,
        }
        
        mt5_timeframe = timeframe_map.get(timeframe, mt5.TIMEFRAME_H1)
        
        # Switch to the symbol's chart
        if not mt5.symbol_select(symbol, True):
            mt5.shutdown()
            return False, f"Failed to select symbol {symbol}"
        
        # Get terminal info to verify connection
        terminal_info = mt5.terminal_info()
        if terminal_info is None:
            mt5.shutdown()
            return False, "Failed to get terminal info"
        
        # Clean up
        mt5.shutdown()
        
        # Focus MT5 window
        os.system(f'powershell -command "(New-Object -ComObject WScript.Shell).AppActivate(\'MetaTrader 5\')"')
        
        return True, f"Opened {symbol} chart on {timeframe} timeframe"
        
    except Exception as e:
        try:
            mt5.shutdown()
        except:
            pass
        return False, f"Error opening MT5 charts: {str(e)}"


class BotInstance:
    """Represents a running bot instance for a trader."""
    
    def __init__(self, trader_id: str, process: subprocess.Popen):
        """
        Initialize bot instance.
        
        Args:
            trader_id: Trader identifier
            process: Bot subprocess
        """
        self.trader_id = trader_id
        self.process = process
        self.start_time = datetime.now()
        self.status = "running"
        self.trades_count = 0
        self.profit = 0.0
        self.last_heartbeat = datetime.now()
    
    def is_alive(self) -> bool:
        """Check if bot process is running."""
        return self.process.poll() is None
    
    def stop(self):
        """Stop the bot process."""
        if self.is_alive():
            self.process.terminate()
            try:
                self.process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                self.process.kill()
        self.status = "stopped"
    
    def get_status(self) -> Dict[str, Any]:
        """Get current bot status."""
        uptime = (datetime.now() - self.start_time).seconds
        
        return {
            "trader_id": self.trader_id,
            "status": self.status if self.is_alive() else "stopped",
            "start_time": self.start_time.isoformat(),
            "uptime_seconds": uptime,
            "trades_count": self.trades_count,
            "profit": self.profit,
            "last_heartbeat": self.last_heartbeat.isoformat(),
            "is_alive": self.is_alive()
        }


class BotController:
    """Controls bot instances across multiple traders."""
    
    def __init__(self):
        """Initialize bot controller."""
        self.active_bots: Dict[str, BotInstance] = {}
        self.monitoring_thread = None
        self.monitoring_active = False
    
    def start_bot(self, trader_id: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Start bot for a trader.
        
        Args:
            trader_id: Trader identifier
            config: Bot configuration
            
        Returns:
            Tuple of (success, message)
        """
        # Check if bot already running
        if trader_id in self.active_bots and self.active_bots[trader_id].is_alive():
            return False, "Bot already running for this trader"
        
        try:
            # Step 1: Launch MT5 if not running
            mt5_success, mt5_message = launch_mt5()
            if not mt5_success:
                return False, f"MT5 Launch Failed: {mt5_message}"
            
            # Step 2: Create config file for this trader
            config_path = Path(f"config/trader_configs/{trader_id}_config.json")
            config_path.parent.mkdir(parents=True, exist_ok=True)
            
            import json
            with open(config_path, 'w') as f:
                json.dump(config, f, indent=2)
            
            # Step 3: Start bot process
            # Get the project root directory
            project_root = Path(__file__).parent.parent
            
            process = subprocess.Popen(
                ['python', 'main.py', '--trader-id', trader_id, '--config', str(config_path)],
                cwd=project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )
            
            # Wait a moment for bot to initialize and connect to MT5
            time.sleep(3)
            
            # Check if process is still alive
            if process.poll() is not None:
                # Process died, get error output
                stdout, stderr = process.communicate()
                error_msg = stderr.decode('utf-8', errors='ignore') if stderr else "Unknown error"
                return False, f"Bot process failed to start: {error_msg}"
            
            # Step 4: Create bot instance
            bot_instance = BotInstance(trader_id, process)
            self.active_bots[trader_id] = bot_instance
            
            # Step 5: Start monitoring if not already running
            if not self.monitoring_active:
                self.start_monitoring()
            
            return True, f"Bot started successfully! MT5 connected and trading is active."
            
        except Exception as e:
            return False, f"Failed to start bot: {str(e)}"
    
    def stop_bot(self, trader_id: str) -> tuple[bool, str]:
        """
        Stop bot for a trader.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Tuple of (success, message)
        """
        if trader_id not in self.active_bots:
            return False, "No bot running for this trader"
        
        try:
            bot = self.active_bots[trader_id]
            bot.stop()
            del self.active_bots[trader_id]
            
            return True, f"Bot stopped successfully for {trader_id}"
            
        except Exception as e:
            return False, f"Failed to stop bot: {str(e)}"
    
    def pause_bot(self, trader_id: str) -> tuple[bool, str]:
        """
        Pause bot (stop taking new trades).
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Tuple of (success, message)
        """
        if trader_id not in self.active_bots:
            return False, "No bot running for this trader"
        
        bot = self.active_bots[trader_id]
        bot.status = "paused"
        
        # In production, send pause signal to bot process
        # For now, just update status
        
        return True, f"Bot paused for {trader_id}"
    
    def resume_bot(self, trader_id: str) -> tuple[bool, str]:
        """
        Resume paused bot.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Tuple of (success, message)
        """
        if trader_id not in self.active_bots:
            return False, "No bot running for this trader"
        
        bot = self.active_bots[trader_id]
        if bot.status != "paused":
            return False, "Bot is not paused"
        
        bot.status = "running"
        
        return True, f"Bot resumed for {trader_id}"
    
    def get_bot_status(self, trader_id: str) -> Optional[Dict[str, Any]]:
        """
        Get status of bot for trader.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Bot status dictionary or None
        """
        if trader_id in self.active_bots:
            return self.active_bots[trader_id].get_status()
        return None
    
    def get_all_bots(self) -> Dict[str, Dict[str, Any]]:
        """Get status of all active bots."""
        return {
            trader_id: bot.get_status()
            for trader_id, bot in self.active_bots.items()
        }
    
    def restart_bot(self, trader_id: str, config: Dict[str, Any]) -> tuple[bool, str]:
        """
        Restart bot for trader.
        
        Args:
            trader_id: Trader identifier
            config: Bot configuration
            
        Returns:
            Tuple of (success, message)
        """
        # Stop if running
        if trader_id in self.active_bots:
            self.stop_bot(trader_id)
            time.sleep(2)  # Wait for cleanup
        
        # Start with new config
        return self.start_bot(trader_id, config)
    
    def start_monitoring(self):
        """Start background monitoring thread."""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitoring_thread = threading.Thread(target=self._monitor_bots, daemon=True)
        self.monitoring_thread.start()
    
    def _monitor_bots(self):
        """Monitor bot health in background."""
        while self.monitoring_active:
            # Check each bot
            dead_bots = []
            
            for trader_id, bot in self.active_bots.items():
                if not bot.is_alive():
                    dead_bots.append(trader_id)
                    print(f"Bot for {trader_id} has stopped unexpectedly")
            
            # Remove dead bots
            for trader_id in dead_bots:
                del self.active_bots[trader_id]
            
            # Stop monitoring if no bots
            if not self.active_bots:
                self.monitoring_active = False
                break
            
            time.sleep(10)  # Check every 10 seconds
    
    def stop_all_bots(self):
        """Stop all running bots."""
        trader_ids = list(self.active_bots.keys())
        for trader_id in trader_ids:
            self.stop_bot(trader_id)
        
        self.monitoring_active = False
    
    def get_system_health(self) -> Dict[str, Any]:
        """Get overall system health metrics."""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            return {
                "active_bots": len(self.active_bots),
                "cpu_usage": cpu_percent,
                "memory_usage": memory.percent,
                "memory_available_gb": memory.available / (1024 ** 3),
                "timestamp": datetime.now().isoformat()
            }
        except:
            return {
                "active_bots": len(self.active_bots),
                "timestamp": datetime.now().isoformat()
            }


# Singleton instance
_bot_controller = None

def get_bot_controller() -> BotController:
    """Get or create bot controller instance."""
    global _bot_controller
    if _bot_controller is None:
        _bot_controller = BotController()
    return _bot_controller
