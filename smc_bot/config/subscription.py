"""
Subscription Management System for SMC Trading Bot

Handles subscription plans, activation, validation, and expiration.
Supports weekly, monthly, quarterly, and yearly subscriptions.
"""

import json
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from enum import Enum
from colorama import Fore, Style, init

init(autoreset=True)


class SubscriptionPlan(Enum):
    """Subscription plan types."""
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    TRIAL = "trial"
    LIFETIME = "lifetime"


class SubscriptionManager:
    """Manages bot subscriptions and license validation."""
    
    # Plan durations in days
    PLAN_DURATIONS = {
        SubscriptionPlan.WEEKLY: 7,
        SubscriptionPlan.MONTHLY: 30,
        SubscriptionPlan.QUARTERLY: 90,
        SubscriptionPlan.YEARLY: 365,
        SubscriptionPlan.TRIAL: 3,
        SubscriptionPlan.LIFETIME: 36500  # 100 years
    }
    
    # Plan prices (for display/reference)
    PLAN_PRICES = {
        SubscriptionPlan.WEEKLY: "$29",
        SubscriptionPlan.MONTHLY: "$99",
        SubscriptionPlan.QUARTERLY: "$249",
        SubscriptionPlan.YEARLY: "$799",
        SubscriptionPlan.TRIAL: "FREE",
        SubscriptionPlan.LIFETIME: "$2499"
    }
    
    def __init__(self, subscriptions_file: str = "config/subscriptions.json"):
        """
        Initialize the subscription manager.
        
        Args:
            subscriptions_file: Path to subscriptions database
        """
        self.subscriptions_file = Path(subscriptions_file)
        self.subscriptions: Dict[str, Dict] = {}
        self.load_subscriptions()
    
    def load_subscriptions(self):
        """Load all subscriptions from file."""
        if self.subscriptions_file.exists():
            try:
                with open(self.subscriptions_file, 'r') as f:
                    self.subscriptions = json.load(f)
            except Exception as e:
                print(Fore.RED + f"❌ Error loading subscriptions: {e}")
                self.subscriptions = {}
        else:
            self.subscriptions = {}
            self.save_subscriptions()
    
    def save_subscriptions(self):
        """Save all subscriptions to file."""
        self.subscriptions_file.parent.mkdir(parents=True, exist_ok=True)
        
        try:
            with open(self.subscriptions_file, 'w') as f:
                json.dump(self.subscriptions, f, indent=2)
        except Exception as e:
            print(Fore.RED + f"❌ Error saving subscriptions: {e}")
    
    def generate_license_key(self, trader_id: str, plan: SubscriptionPlan) -> str:
        """
        Generate a unique license key for a subscription.
        
        Args:
            trader_id: Trader identifier
            plan: Subscription plan
            
        Returns:
            License key string
        """
        # Create a unique string combining trader_id, plan, and random data
        unique_string = f"{trader_id}-{plan.value}-{secrets.token_hex(8)}-{datetime.now().isoformat()}"
        
        # Generate hash
        hash_object = hashlib.sha256(unique_string.encode())
        hash_hex = hash_object.hexdigest()
        
        # Format as license key (XXXX-XXXX-XXXX-XXXX)
        key_parts = [hash_hex[i:i+4].upper() for i in range(0, 16, 4)]
        license_key = "-".join(key_parts)
        
        return license_key
    
    def activate_subscription(self, trader_id: str, plan: SubscriptionPlan, 
                            license_key: Optional[str] = None) -> Tuple[bool, str]:
        """
        Activate a subscription for a trader.
        
        Args:
            trader_id: Trader identifier
            plan: Subscription plan
            license_key: Optional existing license key
            
        Returns:
            Tuple of (success, message)
        """
        try:
            # Generate license key if not provided
            if not license_key:
                license_key = self.generate_license_key(trader_id, plan)
            
            # Calculate expiration date
            duration_days = self.PLAN_DURATIONS[plan]
            activation_date = datetime.now()
            expiration_date = activation_date + timedelta(days=duration_days)
            
            # Create subscription record
            subscription = {
                'trader_id': trader_id,
                'plan': plan.value,
                'license_key': license_key,
                'activation_date': activation_date.isoformat(),
                'expiration_date': expiration_date.isoformat(),
                'is_active': True,
                'price': self.PLAN_PRICES[plan]
            }
            
            # Save subscription
            self.subscriptions[trader_id] = subscription
            self.save_subscriptions()
            
            return True, f"Subscription activated successfully! Expires: {expiration_date.strftime('%Y-%m-%d')}"
            
        except Exception as e:
            return False, f"Activation failed: {str(e)}"
    
    def validate_subscription(self, trader_id: str) -> Tuple[bool, str]:
        """
        Validate if a trader has an active subscription.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Tuple of (is_valid, message)
        """
        if trader_id not in self.subscriptions:
            return False, "No subscription found. Please subscribe to use the bot."
        
        subscription = self.subscriptions[trader_id]
        
        if not subscription.get('is_active', False):
            return False, "Subscription is inactive. Please renew your subscription."
        
        # Check expiration
        expiration_str = subscription.get('expiration_date')
        if not expiration_str:
            return False, "Invalid subscription data. Please contact support."
        
        try:
            expiration_date = datetime.fromisoformat(expiration_str)
            current_date = datetime.now()
            
            if current_date > expiration_date:
                # Subscription expired
                subscription['is_active'] = False
                self.save_subscriptions()
                return False, f"Subscription expired on {expiration_date.strftime('%Y-%m-%d')}. Please renew."
            
            # Calculate days remaining
            days_remaining = (expiration_date - current_date).days
            
            # Warning if expiring soon
            if days_remaining <= 7:
                return True, f"⚠️  Subscription expires in {days_remaining} days!"
            
            return True, f"Subscription active until {expiration_date.strftime('%Y-%m-%d')}"
            
        except Exception as e:
            return False, f"Error validating subscription: {str(e)}"
    
    def get_subscription_info(self, trader_id: str) -> Optional[Dict]:
        """
        Get detailed subscription information.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Subscription dictionary or None
        """
        return self.subscriptions.get(trader_id)
    
    def renew_subscription(self, trader_id: str, plan: SubscriptionPlan) -> Tuple[bool, str]:
        """
        Renew an existing subscription.
        
        Args:
            trader_id: Trader identifier
            plan: New subscription plan
            
        Returns:
            Tuple of (success, message)
        """
        if trader_id not in self.subscriptions:
            return self.activate_subscription(trader_id, plan)
        
        old_subscription = self.subscriptions[trader_id]
        
        # Get current expiration or now
        try:
            old_expiration = datetime.fromisoformat(old_subscription['expiration_date'])
            # If not expired yet, extend from expiration date
            if datetime.now() < old_expiration:
                start_date = old_expiration
            else:
                start_date = datetime.now()
        except:
            start_date = datetime.now()
        
        # Calculate new expiration
        duration_days = self.PLAN_DURATIONS[plan]
        new_expiration = start_date + timedelta(days=duration_days)
        
        # Update subscription
        old_subscription['plan'] = plan.value
        old_subscription['expiration_date'] = new_expiration.isoformat()
        old_subscription['is_active'] = True
        old_subscription['renewal_date'] = datetime.now().isoformat()
        old_subscription['price'] = self.PLAN_PRICES[plan]
        
        self.save_subscriptions()
        
        return True, f"Subscription renewed! New expiration: {new_expiration.strftime('%Y-%m-%d')}"
    
    def deactivate_subscription(self, trader_id: str) -> bool:
        """
        Deactivate a subscription.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            True if successful
        """
        if trader_id in self.subscriptions:
            self.subscriptions[trader_id]['is_active'] = False
            self.save_subscriptions()
            return True
        return False
    
    def display_plans(self):
        """Display available subscription plans."""
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 25 + "SUBSCRIPTION PLANS" + " " * 36 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
        
        plans = [
            (SubscriptionPlan.TRIAL, "3-Day Free Trial", "Test all features risk-free"),
            (SubscriptionPlan.WEEKLY, "Weekly Plan", "Perfect for short-term trading"),
            (SubscriptionPlan.MONTHLY, "Monthly Plan", "Most popular choice"),
            (SubscriptionPlan.QUARTERLY, "Quarterly Plan", "Best value - 3 months"),
            (SubscriptionPlan.YEARLY, "Yearly Plan", "Maximum savings - 12 months"),
            (SubscriptionPlan.LIFETIME, "Lifetime Access", "One-time payment, forever access")
        ]
        
        for i, (plan, name, description) in enumerate(plans, 1):
            price = self.PLAN_PRICES[plan]
            duration = self.PLAN_DURATIONS[plan]
            
            if plan == SubscriptionPlan.TRIAL:
                color = Fore.GREEN
                badge = "🎁 FREE"
            elif plan == SubscriptionPlan.LIFETIME:
                color = Fore.MAGENTA
                badge = "⭐ PREMIUM"
            else:
                color = Fore.YELLOW
                badge = price
            
            print(color + f"[{i}] {name} - {badge}")
            print(Fore.WHITE + f"    {description}")
            print(Fore.WHITE + Style.DIM + f"    Duration: {duration} days")
            print(Fore.WHITE + "─" * 80)
        
        print()
    
    def interactive_subscription(self, trader_id: str) -> Tuple[bool, str]:
        """
        Interactive subscription activation.
        
        Args:
            trader_id: Trader identifier
            
        Returns:
            Tuple of (success, message)
        """
        self.display_plans()
        
        print(Fore.CYAN + Style.BRIGHT + "Select a subscription plan:")
        print(Fore.WHITE + "[1] 3-Day Free Trial")
        print(Fore.WHITE + "[2] Weekly Plan - $29")
        print(Fore.WHITE + "[3] Monthly Plan - $99")
        print(Fore.WHITE + "[4] Quarterly Plan - $249")
        print(Fore.WHITE + "[5] Yearly Plan - $799")
        print(Fore.WHITE + "[6] Lifetime Access - $2499")
        print(Fore.WHITE + "[0] Cancel")
        
        try:
            choice = input(Fore.YELLOW + "\nEnter choice: " + Fore.WHITE)
            choice_num = int(choice)
            
            plan_map = {
                1: SubscriptionPlan.TRIAL,
                2: SubscriptionPlan.WEEKLY,
                3: SubscriptionPlan.MONTHLY,
                4: SubscriptionPlan.QUARTERLY,
                5: SubscriptionPlan.YEARLY,
                6: SubscriptionPlan.LIFETIME
            }
            
            if choice_num == 0:
                return False, "Subscription cancelled"
            
            if choice_num not in plan_map:
                return False, "Invalid choice"
            
            selected_plan = plan_map[choice_num]
            
            # For trial, activate immediately
            if selected_plan == SubscriptionPlan.TRIAL:
                return self.activate_subscription(trader_id, selected_plan)
            
            # For paid plans, ask for license key or payment confirmation
            print(f"\n{Fore.YELLOW}Selected: {selected_plan.value.upper()} - {self.PLAN_PRICES[selected_plan]}")
            print(Fore.WHITE + "\nPayment Options:")
            print(Fore.WHITE + "[1] I have a license key")
            print(Fore.WHITE + "[2] Generate demo key (for testing)")
            print(Fore.WHITE + "[0] Cancel")
            
            payment_choice = input(Fore.YELLOW + "\nChoice: " + Fore.WHITE)
            
            if payment_choice == "1":
                license_key = input(Fore.YELLOW + "Enter your license key: " + Fore.WHITE).strip()
                if len(license_key) < 10:
                    return False, "Invalid license key format"
                return self.activate_subscription(trader_id, selected_plan, license_key)
            
            elif payment_choice == "2":
                print(Fore.YELLOW + "\n⚠️  DEMO MODE: Generating temporary license key")
                print(Fore.WHITE + "For production, integrate real payment processing\n")
                return self.activate_subscription(trader_id, selected_plan)
            
            else:
                return False, "Subscription cancelled"
                
        except ValueError:
            return False, "Invalid input"
        except KeyboardInterrupt:
            return False, "\nSubscription cancelled"
    
    def display_subscription_status(self, trader_id: str):
        """Display subscription status for a trader."""
        if trader_id not in self.subscriptions:
            print(Fore.RED + "\n❌ No active subscription")
            print(Fore.YELLOW + "Please subscribe to use the bot\n")
            return
        
        sub = self.subscriptions[trader_id]
        
        print("\n" + Fore.CYAN + Style.BRIGHT + "=" * 80)
        print(Fore.CYAN + Style.BRIGHT + "║" + " " * 27 + "SUBSCRIPTION STATUS" + " " * 33 + "║")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")
        
        is_valid, message = self.validate_subscription(trader_id)
        
        if is_valid:
            status_color = Fore.GREEN
            status_icon = "✅"
            status_text = "ACTIVE"
        else:
            status_color = Fore.RED
            status_icon = "❌"
            status_text = "INACTIVE"
        
        print(status_color + Style.BRIGHT + f"   {status_icon} Status: {status_text}")
        print(Fore.CYAN + f"   Plan: {sub.get('plan', 'N/A').upper()}")
        print(Fore.CYAN + f"   Price: {sub.get('price', 'N/A')}")
        print(Fore.CYAN + f"   License: {sub.get('license_key', 'N/A')}")
        
        try:
            activation = datetime.fromisoformat(sub['activation_date'])
            expiration = datetime.fromisoformat(sub['expiration_date'])
            print(Fore.WHITE + f"   Activated: {activation.strftime('%Y-%m-%d %H:%M')}")
            print(Fore.WHITE + f"   Expires: {expiration.strftime('%Y-%m-%d %H:%M')}")
            
            days_remaining = (expiration - datetime.now()).days
            if days_remaining > 0:
                print(Fore.YELLOW + f"   Days Remaining: {days_remaining}")
            else:
                print(Fore.RED + f"   Expired: {abs(days_remaining)} days ago")
        except:
            pass
        
        print(Fore.WHITE + f"\n   {message}")
        print(Fore.CYAN + Style.BRIGHT + "=" * 80 + "\n")


# Singleton instance
_subscription_manager = None

def get_subscription_manager() -> SubscriptionManager:
    """Get or create subscription manager instance."""
    global _subscription_manager
    if _subscription_manager is None:
        _subscription_manager = SubscriptionManager()
    return _subscription_manager
