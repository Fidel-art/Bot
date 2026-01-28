# Complete Bot Workflow with Subscription System

## 🚀 Full User Journey

### Step-by-Step: From Installation to Trading

---

## Phase 1: Installation & Setup

```bash
# Step 1: Navigate to bot directory
cd "c:\Users\FidelSomba\OneDrive\Desktop\BOT code\smc_bot"

# Step 2: Install dependencies (if not done)
pip install -r requirements.txt

# Step 3: Ensure MT5 is installed and running
# - MetaTrader 5 application open
# - Logged into demo or live account
# - "Allow automated trading" enabled
```

---

## Phase 2: First Run - Profile Creation

```bash
# Step 4: Run the bot
python main.py
```

### What You'll See:

```
================================================================================
XAUUSD SMC/ICT TRADING BOT
Smart Money Concepts + Inner Circle Trader
================================================================================

No trader profiles found. Let's create one!

================================================================================
║                        CREATE NEW TRADER PROFILE                          ║
================================================================================

Enter Trader ID (e.g., trader1): john_demo
Enter Trader Name: John Smith
Enter MT5 Login: 12345678
Enter MT5 Password: ********
Enter MT5 Server: MetaQuotes-Demo
Lot Size [0.01]: 0.01
Max Drawdown % [5.0]: 5.0
Risk Per Trade % [1.0]: 1.0

✅ Created profile for John Smith (john_demo)
✅ Selected profile: John Smith
```

---

## Phase 3: Subscription Activation

### Bot Detects No Subscription:

```
❌ No subscription found. Please subscribe to use the bot.

You need an active subscription to use the bot.

================================================================================
SUBSCRIPTION REQUIRED
================================================================================
[1] Subscribe Now
[2] View Subscription Status
[3] I have a license key
[4] Renew Subscription
[0] Exit
```

### Choose Free Trial:

```
Choice: 1

================================================================================
║                            SUBSCRIPTION PLANS                              ║
================================================================================

[1] 3-Day Free Trial - 🎁 FREE
    Test all features risk-free
    Duration: 3 days
────────────────────────────────────────────────────────────────────────────────
[2] Weekly Plan - $29
    Perfect for short-term trading
    Duration: 7 days
────────────────────────────────────────────────────────────────────────────────
[3] Monthly Plan - $99
    Most popular choice
    Duration: 30 days
────────────────────────────────────────────────────────────────────────────────
[4] Quarterly Plan - $249
    Best value - 3 months
    Duration: 90 days
────────────────────────────────────────────────────────────────────────────────
[5] Yearly Plan - $799
    Maximum savings - 12 months
    Duration: 365 days
────────────────────────────────────────────────────────────────────────────────
[6] Lifetime Access - ⭐ PREMIUM
    One-time payment, forever access
    Duration: 36500 days
────────────────────────────────────────────────────────────────────────────────

Select a subscription plan:
[1] 3-Day Free Trial
[2] Weekly Plan - $29
[3] Monthly Plan - $99
[4] Quarterly Plan - $249
[5] Yearly Plan - $799
[6] Lifetime Access - $2499
[0] Cancel

Enter choice: 1

✅ Subscription activated successfully! Expires: 2026-01-31 14:30:00
```

---

## Phase 4: Main Menu Access

### With Valid Subscription:

```
✅ Subscription active until 2026-01-31 14:30:00

Initializing bot components...
1/4 Initializing Market Data Handler...
✅ Market Data Handler initialized

2/4 Initializing SMC Strategy Engine...
✅ SMC Strategy Engine initialized

3/4 Initializing Risk Manager...
✅ Risk Manager initialized

4/4 Initializing Trade Executor...
✅ Trade Executor initialized

================================================================================
✅ ALL COMPONENTS INITIALIZED SUCCESSFULLY
================================================================================

================================================================================
MENU OPTIONS
================================================================================
[1] Start Trading Bot
[2] View Trade History & Statistics
[3] View Subscription Status
[4] Manage Subscription
[5] Exit
================================================================================

Choice: 
```

---

## Phase 5: Start Trading

```
Choice: 1

✅ Subscription validated. Starting bot...

🚀 BOT STARTED - Analysis every 300 seconds
Press Ctrl+C to stop the bot
```

### Dashboard Appears:

```
================================================================================
║                    XAUUSD SMC/ICT TRADING BOT DASHBOARD                    ║
================================================================================
║  2026-01-28 14:35:22                                                       ║
║  ✅ Subscription: TRIAL - 3 days remaining                                 ║
================================================================================

📊 CURRENT SIGNAL STATUS:
────────────────────────────────────────────────────────────────────────────────
   ⏸️  NO SIGNAL - Analyzing market conditions...

💰 ACCOUNT INFORMATION:
────────────────────────────────────────────────────────────────────────────────
   Balance:  $10,000.00
   Equity:   $10,000.00
   Profit:   $0.00

🛡️  RISK MANAGEMENT:
────────────────────────────────────────────────────────────────────────────────
   Current Drawdown: 0.00% ✅ Safe
   Remaining Buffer:  5.00%
   Max Allowed:       5.00%
   [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

📈 OPEN POSITIONS:
────────────────────────────────────────────────────────────────────────────────
   No open positions

================================================================================
   Press Ctrl+C to stop the bot
================================================================================
```

---

## Phase 6: Signal Detected & Trade Executed

### Dashboard Updates (5 minutes later):

```
================================================================================
║                    XAUUSD SMC/ICT TRADING BOT DASHBOARD                    ║
================================================================================
║  2026-01-28 14:40:22                                                       ║
║  ✅ Subscription: TRIAL - 3 days remaining                                 ║
================================================================================

📊 CURRENT SIGNAL STATUS:
────────────────────────────────────────────────────────────────────────────────
   🔼 BUY SIGNAL ACTIVE   
   Detected at: 14:38:15

💰 ACCOUNT INFORMATION:
────────────────────────────────────────────────────────────────────────────────
   Balance:  $10,000.00
   Equity:   $10,000.00
   Profit:   $0.00

🛡️  RISK MANAGEMENT:
────────────────────────────────────────────────────────────────────────────────
   Current Drawdown: 0.00% ✅ Safe
   Remaining Buffer:  5.00%
   Max Allowed:       5.00%
   [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

📈 OPEN POSITIONS:
────────────────────────────────────────────────────────────────────────────────
   No open positions
```

### Trade Execution Notification (Screen clears):

```


================================================================================
   🔼 BUY ORDER EXECUTED 🔼   
================================================================================

   Signal:      BUY
   Entry Price: $2045.50
   Stop Loss:   $2040.00
   Take Profit: $2056.00
   Lot Size:    0.010
   Risk/Reward: 2.00R
================================================================================
   💡 Position is now being monitored...


(Displays for 3 seconds, then returns to dashboard)
```

### Dashboard with Open Position:

```
================================================================================
║                    XAUUSD SMC/ICT TRADING BOT DASHBOARD                    ║
================================================================================
║  2026-01-28 14:41:22                                                       ║
║  ✅ Subscription: TRIAL - 3 days remaining                                 ║
================================================================================

📊 CURRENT SIGNAL STATUS:
────────────────────────────────────────────────────────────────────────────────
   🔼 BUY SIGNAL ACTIVE   
   Detected at: 14:38:15

💰 ACCOUNT INFORMATION:
────────────────────────────────────────────────────────────────────────────────
   Balance:  $10,000.00
   Equity:   $10,015.00
   Profit:   +$15.00

🛡️  RISK MANAGEMENT:
────────────────────────────────────────────────────────────────────────────────
   Current Drawdown: 0.00% ✅ Safe
   Remaining Buffer:  5.00%
   Max Allowed:       5.00%
   [░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

📈 OPEN POSITIONS:
────────────────────────────────────────────────────────────────────────────────

   🔼 Position #1:
      Type:   BUY
      Ticket: 123456789
      Lots:   0.01
      Entry:  $2045.50
      SL:     $2040.00
      TP:     $2056.00
      P/L:    +$15.00

================================================================================
   Press Ctrl+C to stop the bot
================================================================================
```

---

## Phase 7: View Statistics (After Some Trades)

### Stop Bot:

```
Press Ctrl+C

⚠️ KEYBOARD INTERRUPT DETECTED
================================================================================
SHUTTING DOWN BOT
================================================================================

Final Risk Status:
  Initial Balance: $10,000.00
  Current Equity: $10,150.00
  Drawdown: 0.00%
  Locked: False

Open Positions: 1

✅ Bot shutdown complete
================================================================================
```

### Run Again and View Stats:

```bash
python main.py
```

```
Choice: 2

================================================================================
║                       TRADE PERFORMANCE ANALYSIS                           ║
================================================================================

📊 OVERALL STATISTICS:
────────────────────────────────────────────────────────────────────────────────
   Total Trades:      5
   Winning Trades:    3
   Losing Trades:     2
   Breakeven Trades:  0

🎯 WIN RATE:
────────────────────────────────────────────────────────────────────────────────
   60.00% (Good)
   [██████████████████████████████░░░░░░░░░░░░░░░░░░░░]

💰 PROFIT ANALYSIS:
────────────────────────────────────────────────────────────────────────────────
   Total Profit:      +$125.00
   Average Profit:    $25.00
   Largest Win:       +$75.00
   Largest Loss:      -$25.00
   Gross Profit:      +$200.00
   Gross Loss:        -$75.00

📈 PROFIT FACTOR:
────────────────────────────────────────────────────────────────────────────────
   2.67 (Excellent)
   (Profit Factor = Gross Profit / Gross Loss)

⚖️  RISK-REWARD:
────────────────────────────────────────────────────────────────────────────────
   Average R:R:       2.15

================================================================================

Export to CSV? (y/n): y
Enter filename [trade_report.csv]: trial_results.csv
✅ Exported 5 trades to trial_results.csv
```

---

## Phase 8: Subscription Expiring

### Day 3 of Trial (Last Day):

```bash
python main.py
```

```
⚠️ Subscription expires in 1 days!

================================================================================
MENU OPTIONS
================================================================================
[1] Start Trading Bot
[2] View Trade History & Statistics
[3] View Subscription Status              ← Check status
[4] Manage Subscription                   ← Renew here
[5] Exit
================================================================================

Choice: 3

================================================================================
║                           SUBSCRIPTION STATUS                              ║
================================================================================

   ⚠️  Status: ACTIVE
   Plan: TRIAL
   Price: FREE
   License: A7F3-9B2C-E4D1-8F6A
   Activated: 2026-01-28 14:30:00
   Expires: 2026-01-31 14:30:00
   Days Remaining: 1

   ⚠️  Subscription expires in 1 days!
================================================================================
```

---

## Phase 9: Upgrade to Paid Plan

```
Choice: 4

================================================================================
SUBSCRIPTION MANAGEMENT
================================================================================
[1] View Status
[2] Renew Subscription
[3] Change Plan
[0] Back

Choice: 2

(Shows plan selection again)

Choice: 3  (Monthly Plan)

Selected: MONTHLY - $99

Payment Options:
[1] I have a license key
[2] Generate demo key (for testing)
[0] Cancel

Choice: 2

⚠️  DEMO MODE: Generating temporary license key
For production, integrate real payment processing

✅ Subscription renewed! New expiration: 2026-03-01 14:30:00
```

---

## Phase 10: Continued Trading

### Now with Monthly Subscription:

```
================================================================================
║                    XAUUSD SMC/ICT TRADING BOT DASHBOARD                    ║
================================================================================
║  2026-02-01 09:15:22                                                       ║
║  ✅ Subscription: MONTHLY - 28 days remaining                              ║
================================================================================

📊 CURRENT SIGNAL STATUS:
   🔽 SELL SIGNAL ACTIVE   
   ...

(Bot continues trading with monthly subscription)
```

---

## Complete File Structure

```
smc_bot/
├── config/
│   ├── subscription.py           ← NEW: Subscription management
│   ├── subscriptions.json        ← AUTO: Subscription database
│   ├── trader_profile.py         ← UPDATED: Profile + subscription link
│   ├── trader_profiles.json      ← AUTO: Trader profiles
│   └── settings.py
│
├── dashboard/
│   ├── dashboard.py              ← UPDATED: Shows subscription status
│   └── trade_analyzer.py
│
├── data/
│   ├── trade_history.json        ← AUTO: Trade records
│   └── market_data.py
│
├── execution/
│   └── mt5_executor.py
│
├── risk/
│   └── risk_manager.py
│
├── strategy/
│   └── smc_engine.py
│
├── logs/
│   └── trading_bot.log
│
├── main.py                       ← UPDATED: Subscription validation
├── requirements.txt
├── README.md                     ← UPDATED: Subscription info
├── SUBSCRIPTION_GUIDE.md         ← NEW: Complete guide
├── SUBSCRIPTION_IMPLEMENTATION.md ← NEW: Technical details
└── WORKFLOW.md                   ← THIS FILE
```

---

## Quick Reference Commands

### Start Bot:
```bash
python main.py
```

### Subscribe (First Time):
```bash
python main.py
→ Select profile
→ [1] Subscribe Now
→ [1] Free Trial
```

### View Subscription:
```bash
python main.py
→ [3] View Subscription Status
```

### Renew:
```bash
python main.py
→ [4] Manage Subscription
→ [2] Renew Subscription
```

### Trade:
```bash
python main.py
→ [1] Start Trading Bot
```

### View Stats:
```bash
python main.py
→ [2] View Trade History & Statistics
```

---

## Success Indicators

✅ **Profile created** - Stored in `config/trader_profiles.json`
✅ **Subscription active** - Stored in `config/subscriptions.json`
✅ **Bot initialized** - All 4 components ready
✅ **Trading enabled** - Dashboard displays live data
✅ **Trades executed** - Saved to trade history
✅ **Statistics available** - View performance anytime

---

## Summary

The complete workflow is:

1. **Install** → Dependencies and MT5
2. **Profile** → Create trader profile
3. **Subscribe** → Activate subscription (trial or paid)
4. **Validate** → Bot checks subscription
5. **Initialize** → All components load
6. **Trade** → Bot analyzes and trades automatically
7. **Monitor** → Dashboard shows real-time status
8. **Analyze** → Review statistics and performance
9. **Renew** → Keep subscription active
10. **Repeat** → Continue profitable trading!

**Your bot is now a complete, subscription-protected trading system!** 🎉🚀💰
