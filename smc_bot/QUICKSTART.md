# Quick Start Guide - SMC Trading Bot

## New Features Overview

### 1. Real-Time Dashboard 📊
- **Live BUY/SELL signal display** with color indicators
- **Account metrics** showing balance, equity, and profit
- **Risk visualization** with progress bars and color codes
- **Open positions** with current P/L
- **Trade execution alerts** that pop up when orders are filled

### 2. Trade History & Analytics 📈
- **Performance statistics**: Win rate, profit factor, total profit
- **Recent trades view**: Last 10 trades with details
- **CSV export**: Export your trade history for external analysis
- **Visual reports**: Color-coded performance metrics

### 3. Multi-Trader Support 👥
- **Multiple profiles**: Each trader has their own settings
- **Separate credentials**: Individual MT5 login per trader
- **Custom risk settings**: Each profile has unique lot size, drawdown limits
- **Individual history**: Separate trade history per trader
- **Easy switching**: Select different profiles at startup

## Getting Started

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

This installs:
- MetaTrader5 (MT5 API)
- pandas & numpy (data processing)
- colorama (colored terminal output)

### Step 2: Run the Bot
```bash
cd smc_bot
python main.py
```

### Step 3: First-Time Setup

**If no profiles exist:**
The bot will prompt you to create your first profile:
```
Enter Trader ID (e.g., trader1): myaccount
Enter Trader Name: John Smith
Enter MT5 Login: 12345678
Enter MT5 Password: your_password
Enter MT5 Server: MetaQuotes-Demo
Lot Size [0.01]: 0.01
Max Drawdown % [5.0]: 5.0
Risk Per Trade % [1.0]: 1.0
```

**If profiles exist:**
You'll see a menu:
```
[1] Select existing profile
[2] Create new profile
[3] Use default settings
```

### Step 4: Choose an Option

**Main Menu:**
```
[1] Start Trading Bot     → Run live trading with dashboard
[2] View Trade History    → See your performance statistics
[3] Exit                  → Close the application
```

## Using the Dashboard

### When Trading is Active:

The dashboard refreshes automatically and shows:

**Signal Status:**
```
📊 CURRENT SIGNAL STATUS:
🔼 BUY SIGNAL ACTIVE       (green background)
🔽 SELL SIGNAL ACTIVE      (red background)
⏸️  NO SIGNAL              (analyzing conditions)
```

**Account Info:**
```
💰 ACCOUNT INFORMATION:
Balance:  $10,000.00
Equity:   $10,150.00
Profit:   +$150.00        (green if positive, red if negative)
```

**Risk Metrics:**
```
🛡️  RISK MANAGEMENT:
Current Drawdown: 1.20% ✅ Safe
[████░░░░░░░░░░░░░] 1.20% / 5.00%
```

Color codes:
- 🟢 Green: Safe (< 50% of max drawdown)
- 🟡 Yellow: Moderate (50-80% of max)
- 🔴 Red: High risk (> 80% of max)

**Open Positions:**
```
📈 OPEN POSITIONS:
🔼 Position #1:
   Type:   BUY
   Ticket: 123456789
   Entry:  $2045.50
   SL:     $2040.00
   TP:     $2056.00
   P/L:    +$15.00
```

### Trade Execution Alert

When a trade executes, the screen clears and shows:
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

   💡 Position is now being monitored...
```

This displays for 3 seconds, then returns to the main dashboard.

## Viewing Trade Analytics

Select option [2] from the main menu to see:

### Performance Overview:
```
📊 OVERALL STATISTICS:
Total Trades:      25
Winning Trades:    16
Losing Trades:     8
Breakeven Trades:  1

🎯 WIN RATE:
64.00% (Excellent)
[████████████████████████████████░░░░░░░░░░░░░░░░░░]

💰 PROFIT ANALYSIS:
Total Profit:      +$450.00
Average Profit:    $18.00
Largest Win:       +$85.00
Largest Loss:      -$35.00

📈 PROFIT FACTOR: 2.35 (Excellent)
```

### Recent Trades:
```
Trade #25:
🔼 BUY
Entry:  2024-01-28 14:30:00
Exit:   2024-01-28 16:45:00
Price:  $2045.50
Profit: +$25.00
```

### Export to CSV:
When prompted:
```
Export to CSV? (y/n): y
Enter filename [trade_report.csv]: my_trades.csv
✅ Exported 25 trades to my_trades.csv
```

## Multi-Trader Workflow

### Scenario: Team with 3 Traders

**Initial Setup:**
```bash
python main.py
```

**Trader 1 (John) - First time:**
```
[2] Create new profile
Trader ID: john
Name: John Smith
MT5 Login: 11111111
...
```

**Trader 2 (Sarah) - Same computer:**
```bash
python main.py
```
```
[2] Create new profile
Trader ID: sarah
Name: Sarah Johnson
MT5 Login: 22222222
...
```

**Trader 3 (Mike) - Same computer:**
```bash
python main.py
```
```
[2] Create new profile
Trader ID: mike
Name: Mike Williams
MT5 Login: 33333333
...
```

### Daily Usage:

**John starts trading:**
```bash
python main.py
[1] Select existing profile
[1] John Smith (john)        ← Selects his profile
[1] Start Trading Bot        ← Runs with his settings
```

**Later, Sarah wants to check her stats:**
```bash
python main.py
[1] Select existing profile
[2] Sarah Johnson (sarah)    ← Selects her profile
[2] View Trade History       ← Sees her performance
```

Each trader's data is completely separate!

## Tips & Best Practices

### 1. Dashboard Tips:
- Keep terminal window maximized for best view
- Dashboard updates every analysis cycle (5 minutes)
- Watch the drawdown bar - stay in green zone
- Color changes indicate status (green=good, yellow=caution, red=danger)

### 2. Profile Management:
- Use descriptive trader IDs (e.g., "demo_account", "live_small")
- Keep MT5 passwords secure
- Test with demo accounts first
- Each profile can have different risk levels

### 3. Trade History:
- Review statistics regularly
- Export to CSV for detailed analysis in Excel
- Track your win rate improvements over time
- Analyze best and worst trades to improve strategy

### 4. Risk Management:
- Start with minimum lot sizes (0.001 or 0.01)
- Keep max drawdown at 5% or lower
- Monitor the risk bar on dashboard
- If hitting yellow zone, reduce lot sizes

## Troubleshooting

### Dashboard not displaying properly?
- Ensure terminal supports colors (Windows Terminal, PowerShell recommended)
- Run: `pip install --upgrade colorama`

### Trade history not saving?
- Check `data/` folder exists
- Ensure write permissions in bot directory
- Check logs for error messages

### Profile not loading?
- Verify `config/trader_profiles.json` exists
- Check JSON syntax if edited manually
- Delete file and recreate profiles if corrupted

### Colors not showing?
- Windows: Use Windows Terminal or PowerShell (not CMD)
- Linux/Mac: Most terminals support colors by default
- Run: `python -c "import colorama; colorama.init(); print('Test')"`

## Support

Check the logs for detailed information:
```
logs/trading_bot.log
```

All errors and warnings are logged there with timestamps.

## What's Next?

1. **Start with demo account** - Test all features safely
2. **Create your profile** - Set conservative risk limits
3. **Run the bot** - Watch the dashboard in action
4. **Analyze results** - Review statistics after a few trades
5. **Adjust settings** - Fine-tune based on performance
6. **Scale gradually** - Increase lot sizes carefully

Happy Trading! 🚀
