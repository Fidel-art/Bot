"""
Trader Profile Management for Multi-User Support

Allows multiple traders to use the bot with individual:
- MT5 account credentials
- Risk settings
- Trading preferences
- Trade history
"""

import json
from pathlib import Path
from typing import Dict, Any, Optional, List
from colorama import Fore, Style, init
from datetime import datetime

init(autoreset=True)


class TraderProfile:
    """Represents a single trader's profile."""
    
    def __init__(self, trader_id: str, data: Dict[str, Any]):
        """
        Initialize a trader profile.
        
        Args:
            trader_id: Unique trader identifier
            data: Profile data dictionary
        """
        self.trader_id = trader_id
        self.name = data.get('name', trader_id)
        self.mt5_login = data.get('mt5_login', 0)
        self.mt5_password = data.get('mt5_password', '')
        self.mt5_server = data.get('mt5_server', '')
        
        # Trading settings
        self.lot_size = data.get('lot_size', 0.01)
        self.max_drawdown = data.get('max_drawdown', 5.0)
        self.risk_per_trade = data.get('risk_per_trade', 1.0)
        self.max_open_trades = data.get('max_open_trades', 1)
        self.min_risk_reward = data.get('min_risk_reward', 2.0)
        
        # Session preferences
        self.preferred_sessions = data.get('preferred_sessions', ['LONDON', 'NEW_YORK'])
        self.enable_session_filter = data.get('enable_session_filter', True)
        
        # Profile metadata
        self.created_at = data.get('created_at', datetime.now().isoformat())
        self.last_used = data.get('last_used', datetime.now().isoformat())
        self.is_active = data.get('is_active', True)
        
        # Trade history file
        self.trade_history_file = data.get('trade_history_file', f'data/trades_{trader_id}.json')
        
        # Subscription status
        self.has_subscription = data.get('has_subscription', False)
        self.subscription_checked = data.get('subscription_checked', False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert profile to dictionary."""
        return {
            'name': self.name,
            'mt5_login': self.mt5_login,
            'mt5_password': self.mt5_password,
            'mt5_server': self.mt5_server,
            'lot_size': self.lot_size,
            'max_drawdown': self.max_drawdown,
            'risk_per_trade': self.risk_per_trade,
            'max_open_trades': self.max_open_trades,
            'min_risk_reward': self.min_risk_reward,
            'preferred_sessions': self.preferred_sessions,
            'enable_session_filter': self.enable_session_filter,
            'created_at': self.created_at,
            'last_used': self.last_used,
            'is_active': self.is_active,
            'trade_history_file': self.trade_history_file,
            'has_subscription': self.has_subscription,
            'subscription_checked': self.subscription_checked
        }
    
    def update_last_used(self):
        """Update last used timestamp."""
        self.last_used = datetime.now().isoformat()


class ProfileManager:
    """Manages multiple trader profiles."""
    
    def __init__(self, profiles_file: str = "config/trader_profiles.json"):
        """
        Initialize the profile manager.
        
        Args:
            profiles_file: Path to profiles JSON file
        """
        self.profiles_file = Path(profiles_file)
        self.profiles: Dict[str, TraderProfile] = {}
        self.current_profile: Optional[TraderProfile] = None
        self.load_profiles()
    
    def load_profiles(self):
        """Load all trader profiles from file."""
        if self.profiles_file.exists():
            try:
                with open(self.profiles_file, 'r') as f:
                    data = json.load(f)
                    for trader_id, profile_data in data.items():
                        self.profiles[trader_id] = TraderProfile(trader_id, profile_data)
                print(Fore.GREEN + f"✅ Loaded {len(self.profiles)} trader profile(s)")
            except Exception as e:
                print(Fore.RED + f"❌ Error loading profiles: {e}")
                self.profiles = {}
        else:
            print(Fore.YELLOW + "⚠️  No profiles found. Creating new profiles file.")
            self.profiles = {}
            self.save_profiles()
    
    def save_profiles(self):
        """Save all profiles to file."""
        # Ensure directory exists
        self.profiles_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert profiles to dict
        data = {tid: profile.to_dict() for tid, profile in self.profiles.items()}
        
        try:
            with open(self.profiles_file, 'w') as f:
                json.dump(data, f, indent=2)
            print(Fore.GREEN + f"✅ Saved {len(self.profiles)} profile(s)")
        except Exception as e:
            print(Fore.RED + f"❌ Error saving profiles: {e}")
    
    def create_profile(self, trader_id: str, name: str, mt5_login: int, 
                      mt5_password: str, mt5_server: str, **kwargs) -> TraderProfile:
        """
        Create a new trader profile.
        
        Args:
            trader_id: Unique identifier
            name: Trader's name
            mt5_login: MT5 account login
            mt5_password: MT5 account password
            mt5_server: MT5 server name
            **kwargs: Additional profile settings
            
        Returns:
            Created TraderProfile
        """
        if trader_id in self.profiles:
            print(Fore.YELLOW + f"⚠️  Profile '{trader_id}' already exists")
            return self.profiles[trader_id]
        
        profile_data = {
            'name': name,
            'mt5_login': mt5_login,
            'mt5_password': mt5_password,
            'mt5_server': mt5_server,
            'created_at': datetime.now().isoformat(),
            **kwargs
        }
        
        profile = TraderProfile(trader_id, profile_data)
        self.profiles[trader_id] = profile
        self.save_profiles()
        
        print(Fore.GREEN + f"✅ Created profile for {name} ({trader_id})")
        return profile
    
    def get_profile(self, trader_id: str) -> Optional[TraderProfile]:
        """Get a profile by ID."""
        return self.profiles.get(trader_id)
    
    def list_profiles(self) -> List[str]:
        """Get list of all profile IDs."""
        return list(self.profiles.keys())
    
    def select_profile(self, trader_id: str) -> bool:
        """
        Select a profile to use.
        
        Args:
            trader_id: Profile ID to select
            
        Returns:
            True if successful
        """
        if trader_id not in self.profiles:
            print(Fore.RED + f"❌ Profile '{trader_id}' not found")
            return False
        
        self.current_profile = self.profiles[trader_id]
        self.current_profile.update_last_used()
        self.save_profiles()
        
        print(Fore.GREEN + f"✅ Selected profile: {self.current_profile.name}")
        return True
    
    def delete_profile(self, trader_id: str) -> bool:
        """
        Delete a trader profile.
        
        Args:
            trader_id: Profile ID to delete
            
        Returns:
            True if successful
        """
        if trader_id not in self.profiles:
            print(Fore.RED + f"❌ Profile '{trader_id}' not found")
            return False
        
        del self.profiles[trader_id]
        self.save_profiles()
        
        print(Fore.GREEN + f"✅ Deleted profile: {trader_id}")
        return True
    
    def display_profiles(self):
        """Display all profiles in formatted output."""
        if not self.profiles:
            print(Fore.YELLOW + "⚠️  No trader profiles found")
            return
        
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 28 + "TRADER PROFILES" + " " * 36 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
        
        for i, (trader_id, profile) in enumerate(self.profiles.items(), 1):
            active_marker = "✅" if profile.is_active else "⏸️"
            current_marker = "👉" if self.current_profile and self.current_profile.trader_id == trader_id else "  "
            
            print(f"{current_marker} {Fore.YELLOW}Profile #{i}: {active_marker}")
            print(Fore.CYAN + f"   ID:          {trader_id}")
            print(Fore.CYAN + f"   Name:        {profile.name}")
            print(Fore.CYAN + f"   MT5 Login:   {profile.mt5_login}")
            print(Fore.CYAN + f"   MT5 Server:  {profile.mt5_server}")
            print(Fore.WHITE + f"   Lot Size:    {profile.lot_size}")
            print(Fore.WHITE + f"   Max DD:      {profile.max_drawdown}%")
            print(Fore.WHITE + f"   Risk/Trade:  {profile.risk_per_trade}%")
            
            # Format last used
            try:
                last_used = datetime.fromisoformat(profile.last_used)
                last_used_str = last_used.strftime('%Y-%m-%d %H:%M')
            except:
                last_used_str = "Never"
            
            print(Fore.WHITE + Style.DIM + f"   Last Used:   {last_used_str}")
            print(Fore.WHITE + "─" * 80)
        
        print()
    
    def interactive_selection(self) -> Optional[TraderProfile]:
        """
        Interactive profile selection with user input.
        
        Returns:
            Selected TraderProfile or None
        """
        if not self.profiles:
            print(Fore.YELLOW + "⚠️  No profiles available. Create one first.")
            return None
        
        self.display_profiles()
        
        print(Fore.CYAN + Style.BRIGHT + "Select a trader profile:")
        profile_list = list(self.profiles.keys())
        
        for i, trader_id in enumerate(profile_list, 1):
            profile = self.profiles[trader_id]
            print(Fore.WHITE + f"  [{i}] {profile.name} ({trader_id})")
        
        print(Fore.WHITE + f"  [0] Exit")
        
        try:
            choice = input(Fore.YELLOW + "\nEnter choice: " + Fore.WHITE)
            choice_num = int(choice)
            
            if choice_num == 0:
                return None
            
            if 1 <= choice_num <= len(profile_list):
                selected_id = profile_list[choice_num - 1]
                self.select_profile(selected_id)
                return self.current_profile
            else:
                print(Fore.RED + "❌ Invalid choice")
                return None
                
        except ValueError:
            print(Fore.RED + "❌ Invalid input")
            return None
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n⚠️  Selection cancelled")
            return None
    
    def create_profile_interactive(self) -> Optional[TraderProfile]:
        """
        Interactive profile creation with user input.
        
        Returns:
            Created TraderProfile or None
        """
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 26 + "CREATE NEW TRADER PROFILE" + " " * 28 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
        
        try:
            trader_id = input(Fore.YELLOW + "Enter Trader ID (e.g., trader1): " + Fore.WHITE).strip()
            if not trader_id:
                print(Fore.RED + "❌ Trader ID cannot be empty")
                return None
            
            if trader_id in self.profiles:
                print(Fore.RED + f"❌ Profile '{trader_id}' already exists")
                return None
            
            name = input(Fore.YELLOW + "Enter Trader Name: " + Fore.WHITE).strip()
            mt5_login = int(input(Fore.YELLOW + "Enter MT5 Login: " + Fore.WHITE))
            mt5_password = input(Fore.YELLOW + "Enter MT5 Password: " + Fore.WHITE).strip()
            mt5_server = input(Fore.YELLOW + "Enter MT5 Server: " + Fore.WHITE).strip()
            
            # Optional settings
            lot_size = float(input(Fore.YELLOW + f"Lot Size [0.01]: " + Fore.WHITE) or "0.01")
            max_dd = float(input(Fore.YELLOW + f"Max Drawdown % [5.0]: " + Fore.WHITE) or "5.0")
            risk_per_trade = float(input(Fore.YELLOW + f"Risk Per Trade % [1.0]: " + Fore.WHITE) or "1.0")
            
            profile = self.create_profile(
                trader_id=trader_id,
                name=name,
                mt5_login=mt5_login,
                mt5_password=mt5_password,
                mt5_server=mt5_server,
                lot_size=lot_size,
                max_drawdown=max_dd,
                risk_per_trade=risk_per_trade
            )
            
            return profile
            
        except ValueError as e:
            print(Fore.RED + f"❌ Invalid input: {e}")
            return None
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n⚠️  Profile creation cancelled")
            return None


# Singleton instance
_profile_manager = None

def get_profile_manager() -> ProfileManager:
    """Get or create profile manager instance."""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = ProfileManager()
    return _profile_manager
