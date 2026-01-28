# XAUUSD SMC/ICT Trading Bot

An automated trading bot for Gold (XAUUSD) built with Python and MetaTrader 5, implementing Smart Money Concepts (SMC) and Inner Circle Trader (ICT) methodologies.

## 🎯 Features

- **Smart Money Concepts (SMC) Analysis**
  - Market structure identification (HH, HL, LH, LL)
  - Break of Structure (BOS) detection
  - Change of Character (CHoCH) identification
  - Order block detection
  - Fair Value Gap (FVG) identification
  - Liquidity analysis and sweeps

- **Multi-Timeframe Analysis**
  - Daily (D1): Macro market bias
  - 4-Hour (H4): Institutional structure
  - 1-Hour (H1): Trade setup zones
  - 15-Minute (M15): Entry confirmation

- **Advanced Risk Management**
  - 5% maximum drawdown protection (HARD LOCK)
  - Trade-level risk validation
  - Minimum 1:2 risk-reward ratio
  - Account-level protection
  - Automatic trading lock on breach

- **Professional Execution**
  - MT5 broker integration
  - Market and pending orders
  - Automatic SL/TP management
  - Position monitoring
  - Error handling and retry logic

- **🆕 Real-Time Dashboard**
  - Live trade signal display (BUY/SELL indicators)
  - Current account status with color-coded metrics
  - Open positions monitoring
  - Risk metrics visualization
  - Visual notifications when trades execute

- **🆕 Trade History & Analytics**
  - Comprehensive trade history tracking
  - Win rate and profit factor analysis
  - Best and worst trade tracking
  - Performance statistics dashboard
  - CSV export for external analysis

- **🆕 Multi-User Support**
  - Multiple trader profiles with individual settings
  - Separate MT5 credentials per trader
  - Custom risk parameters for each user
  - Individual trade history tracking
  - Easy profile switching

- **🆕 Subscription System**
  - Weekly, Monthly, Quarterly, and Yearly plans
  - 3-Day free trial for new users
  - Automatic subscription validation
  - License key activation
  - Expiration warnings and renewal reminders
  - Subscription status in dashboard

## 📁 Project Structure

```
smc_bot/
│
├── config/
│   ├── __init__.py
│   ├── settings.py           # Global configuration
│   ├── trader_profile.py     # Multi-user profile management
│   ├── subscription.py        # Subscription management
│   ├── trader_profiles.json  # Trader profiles storage
│   └── subscriptions.json     # Subscription database
│
├── data/
│   ├── __init__.py
│   ├── market_data.py        # MT5 data handling
│   └── trade_history.json    # Trade history storage
│
├── dashboard/
│   ├── __init__.py
│   ├── dashboard.py          # Real-time display
│   └── trade_analyzer.py     # Trade history analytics
│
├── strategy/
│   ├── __init__.py
│   └── smc_engine.py         # SMC/ICT trading logic
│
├── risk/
│   ├── __init__.py
│   └── risk_manager.py       # Risk management
│
├── execution/
│   ├── __init__.py
│   └── mt5_executor.py       # Trade execution
│
├── logs/                     # Trading logs (auto-created)
├── main.py                   # Main entry point
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🚀 Installation

### Prerequisites

1. **Python 3.10 or higher**
2. **MetaTrader 5** installed and configured
3. **MT5 account** (demo or live)

### Step 1: Clone or Download

Download this project to your local machine.

### Step 2: Install Dependencies

Open a terminal in the project directory and run:

```bash
pip install -r requirements.txt
```

### Step 3: Configure MT5

1. Open MetaTrader 5
2. Login to your trading account
3. Go to Tools → Options → Expert Advisors
4. Enable "Allow automated trading"
5. Enable "Allow DLL imports"

### Step 4: Configure Bot Settings

Edit `config/settings.py` to customize:

```python
# Symbol
SYMBOL = "XAUUSD"

# Risk parameters
MAX_DRAWDOWN_PERCENT = 5.0
LOT_SIZE = 0.001
MIN_RISK_REWARD = 2.0

# Timeframes and candle counts
# ... (see file for full configuration)
```

## 🎮 Usage

### First-Time Setup

When you run the bot for the first time:

```bash
python main.py
```

You'll be prompted to:
1. **Create a trader profile** with your MT5 credentials
2. **Set your risk parameters** (lot size, max drawdown, etc.)
3. **⚠️ Activate a subscription** (required to trade)
4. **Choose to start trading** or view analytics

### 🔑 Subscription Activation

**All traders must subscribe before using the bot.**

#### Available Plans:

| Plan | Duration | Price |
|------|----------|-------|
| **Free Trial** | 3 Days | FREE |
| **Weekly** | 7 Days | $29 |
| **Monthly** | 30 Days | $99 |
| **Quarterly** | 90 Days | $249 |
| **Yearly** | 365 Days | $799 |
| **Lifetime** | Forever | $2,499 |

#### How to Subscribe:

When you first run the bot without a subscription:

```
❌ No subscription found. Please subscribe to use the bot.

SUBSCRIPTION REQUIRED
[1] Subscribe Now          ← Start here
[2] View Subscription Status
[3] I have a license key
[4] Renew Subscription
[0] Exit
```

1. Select **[1] Subscribe Now**
2. Choose your plan (start with **Free Trial** to test)
3. For trial: Activates immediately
4. For paid plans: Enter license key or generate demo key

**See [SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md) for detailed instructions.**

### Creating Trader Profiles

The bot supports multiple traders with individual settings:

```
[1] Create new profile
Enter Trader ID: trader1
Enter Trader Name: John Doe
Enter MT5 Login: 12345678
Enter MT5 Password: ********
Enter MT5 Server: MetaQuotes-Demo
Lot Size [0.01]: 0.01
Max Drawdown % [5.0]: 5.0
Risk Per Trade % [1.0]: 1.0
```

Each profile includes:
- Unique MT5 credentials
- Custom risk settings
- Separate trade history
- Individual performance tracking

### Running the Bot

After profile setup, you'll see the main menu:

```
MENU OPTIONS
[1] Start Trading Bot
[2] View Trade History & Statistics
[3] View Subscription Status              ← Check your subscription
[4] Manage Subscription                   ← Renew or change plan
[5] Exit
```

**Option 1 - Start Trading:**
- ✅ **Validates subscription first**
- Bot connects to MT5
- Displays real-time dashboard
- Shows live BUY/SELL signals
- Updates account metrics continuously
- Executes trades automatically when conditions align

**Option 2 - View Analytics:**
- Trade performance statistics
- Win rate and profit factor
- Recent trade history
- Export to CSV option

### Dashboard Display

When running, you'll see a colorful real-time dashboard:

```
================================================================================
║                    XAUUSD SMC/ICT TRADING BOT DASHBOARD                    ║
================================================================================
║  ✅ Subscription: MONTHLY - 20 days remaining                              ║
================================================================================

📊 CURRENT SIGNAL STATUS:
────────────────────────────────────────────────────────────────────────────────
   🔼 BUY SIGNAL ACTIVE
   Detected at: 14:32:15

💰 ACCOUNT INFORMATION:
────────────────────────────────────────────────────────────────────────────────
   Balance:  $10,000.00
   Equity:   $10,150.00
   Profit:   +$150.00

🛡️  RISK MANAGEMENT:
────────────────────────────────────────────────────────────────────────────────
   Current Drawdown: 0.50% ✅ Safe
   Remaining Buffer:  4.50%
   Max Allowed:       5.00%
   [████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]

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
```

### Trade Execution Notifications

When a trade executes, you'll see:

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
```

### Bot Workflow

1. **Initialization**: Connects to MT5 and validates components
2. **Analysis Cycle** (runs every 5 minutes):
   - Updates account information and displays on dashboard
   - Checks drawdown status with visual indicators
   - Fetches multi-timeframe data
   - Analyzes market structure (SMC/ICT)
   - Generates trade signals (shown in real-time)
   - Validates risk-reward
   - Executes trades with visual notification
   - Saves trade to history

3. **Continuous Monitoring**: Dashboard updates with positions and P/L

### Stopping the Bot

Press `Ctrl+C` to gracefully shutdown the bot.

## 📊 Configuration Options

### Symbol Configuration

Currently configured for XAUUSD. To add more symbols in the future:

```python
# In settings.py
SYMBOLS = ["XAUUSD", "EURUSD", "GBPUSD"]
```

### Risk Parameters

```python
MAX_DRAWDOWN_PERCENT = 5.0    # Maximum account drawdown
LOT_SIZE = 0.001              # Fixed lot size
RISK_PER_TRADE_PERCENT = 1.0  # Risk per trade
MIN_RISK_REWARD = 2.0         # Minimum RR ratio
```

### Timeframes

```python
TIMEFRAMES = {
    'D1': 'D1',      # Daily
    'H4': 'H4',      # 4-Hour
    'H1': 'H1',      # 1-Hour
    'M15': 'M15'     # 15-Minute
}
```

### Analysis Interval

In `main.py`, adjust the cycle interval:

```python
bot.run(interval_seconds=300)  # 5 minutes
```

## 🛡️ Risk Management

### Maximum Drawdown Protection

The bot enforces a **CRITICAL 5% maximum drawdown rule**:

- If account equity drops 5% below initial balance, trading is **LOCKED**
- A lock file is created: `drawdown_lock.txt`
- Bot will not resume trading until manually reviewed
- To unlock: Delete the lock file after reviewing account

### Trade-Level Protection

- Only 1 open trade at a time
- Minimum 1:2 risk-reward ratio enforced
- Stop-loss beyond key SMC levels
- Fixed lot sizing for consistency

## 📝 Logging & History

### Activity Logging

All bot activity is logged to:

- **Console**: Real-time output with color-coded dashboard
- **File**: `logs/trading_bot.log`

### Trade History

Trades are automatically saved to:
- **Default**: `data/trade_history.json`
- **Per Trader**: `data/trades_{trader_id}.json` (when using profiles)

Each trade record includes:
- Ticket number and signal type
- Entry/exit prices and times
- Stop loss and take profit levels
- Lot size and risk-reward ratio
- Profit/loss and trade status

## 📈 Trade Analytics

Access comprehensive trade analytics:

```bash
python main.py
# Select option [2] View Trade History & Statistics
```

**Available Statistics:**
- Total trades, wins, losses
- Win rate percentage with visual bar
- Total profit/loss
- Average profit per trade
- Largest win and largest loss
- Gross profit vs gross loss
- Profit factor calculation
- Average risk-reward ratio

**Export Options:**
- Export trade history to CSV
- Custom filename support
- Compatible with Excel and trading journals

## 🔄 Multi-User Features

### Managing Multiple Traders

The bot is fully portable and supports multiple traders:

**Profile Management:**
```python
# profiles are stored in config/trader_profiles.json
{
  "trader1": {
    "name": "John Doe",
    "mt5_login": 12345678,
    "mt5_server": "MetaQuotes-Demo",
    "lot_size": 0.01,
    "max_drawdown": 5.0,
    "has_subscription": true,
    ...
  },
  "trader2": {
    "name": "Sarah Smith",
    "has_subscription": false,
    ...
  }
}
```

**Each Profile Has:**
- Individual MT5 credentials
- Separate subscription status
- Unique trade history
- Custom risk settings
  },
  "trader2": {
    ...
  }
}
```

**Benefits:**
- Each trader has separate trade history
- Individual risk parameters
- Unique MT5 credentials
- Independent performance tracking
- Easy switching between profiles

**Use Cases:**
- Trading team with multiple accounts
- Personal demo and live accounts
- Different risk strategies per account
- Multiple traders sharing one computer

### Switching Profiles

1. Run the bot: `python main.py`
2. Select "Select existing profile"
3. Choose from list of profiles
4. Bot loads that trader's settings and history

Log levels:
- `INFO`: Normal operation
- `WARNING`: Important notices
- `ERROR`: Failures and issues
- `CRITICAL`: Drawdown locks and severe issues

## 🔧 Troubleshooting

### "MT5 initialization failed"

- Ensure MetaTrader 5 is running
- Check that you're logged into an account
- Verify "Allow automated trading" is enabled

### "Symbol XAUUSD not found"

- Check symbol spelling in settings.py
- Verify symbol is available in your broker
- Ensure symbol is visible in Market Watch

### "Trading locked due to drawdown"

- Check `drawdown_lock.txt` for details
- Review account performance
- Delete lock file to manually unlock (use caution)

### "No subscription found" or "Subscription expired"

- Subscribe or renew your subscription
- Check subscription status: Main menu → [3]
- Contact support if you have a valid license key
- See [SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md) for help

### "Failed to fetch data"

- Check internet connection
- Verify MT5 is connected to broker
- Ensure sufficient historical data is available

## 📈 Strategy Overview

### Entry Conditions

Trade signals are generated when:

1. **Multi-timeframe alignment**: All timeframes show same bias
2. **Market structure**: Clear HH/HL (bullish) or LH/LL (bearish)
3. **Order blocks identified**: Institutional entry zones located
4. **Risk-reward validated**: Minimum 1:2 ratio achieved
5. **Risk checks pass**: Drawdown limits not breached

### Exit Management

- **Stop-Loss**: Below/above order blocks with buffer
- **Take-Profit**: Minimum 2x risk distance
- **Automatic closure**: When SL or TP hit

## 🚨 Important Notes

### Subscription Required

⚠️ **All traders must have an active subscription to use the bot.**

- Start with a **3-day free trial**
- Choose from flexible plans (weekly to lifetime)
- Subscriptions are validated before each trading session
- See [SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md) for details

### Disclaimer

This bot is for educational and research purposes. Trading carries risk. Always test on a demo account first.

### Prop Firm Compliance

The 5% drawdown protection is designed for prop firm compatibility. Adjust as needed for your specific requirements.

### Performance

- Bot performance depends on market conditions
- No strategy wins 100% of the time
- Proper risk management is essential
- Regular monitoring recommended

## 🔄 Future Enhancements

Planned features:

- Multi-symbol trading support
- Backtesting module
- Trade notifications (Telegram/Email)
- Advanced session filters
- Correlation analysis
- Dynamic lot sizing
- Trade journal and statistics
- Payment gateway integration for subscriptions
- Mobile app for subscription management

## 📚 Documentation

- **[README.md](README.md)** - Main documentation (this file)
- **[QUICKSTART.md](QUICKSTART.md)** - Getting started guide
- **[SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md)** - Subscription system details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture
- **[SHOWCASE.md](SHOWCASE.md)** - Feature showcase
- **[CHANGES.md](CHANGES.md)** - Change log

## 📚 References

- **Smart Money Concepts (SMC)**: Market structure and institutional behavior analysis
- **Inner Circle Trader (ICT)**: Premium/discount zones and liquidity concepts
- **MetaTrader 5 API**: Official Python integration

## 📄 License

This project is provided as-is for educational purposes.

## 👨‍💻 Support

For issues or questions:

1. Check the troubleshooting section
2. Review logs in `logs/trading_bot.log`
3. Verify configuration in `config/settings.py`

## 🎯 Version

**Version**: 1.0.0  
**Last Updated**: January 2026

---

**⚠️ Risk Warning**: Trading forex and CFDs carries a high level of risk and may not be suitable for all investors. Never invest money you cannot afford to lose. Always test strategies on demo accounts before live trading.
