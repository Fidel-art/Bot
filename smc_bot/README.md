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

## 📁 Project Structure

```
smc_bot/
│
├── config/
│   ├── __init__.py
│   └── settings.py          # Configuration parameters
│
├── data/
│   ├── __init__.py
│   └── market_data.py        # MT5 data handling
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

### Running the Bot

```bash
python main.py
```

Or on Windows:

```bash
python smc_bot/main.py
```

### Bot Workflow

1. **Initialization**: Connects to MT5 and validates components
2. **Analysis Cycle** (runs every 5 minutes):
   - Updates account information
   - Checks drawdown status
   - Fetches multi-timeframe data
   - Analyzes market structure
   - Generates trade signals
   - Validates risk-reward
   - Executes trades if conditions align

3. **Continuous Monitoring**: Tracks positions and drawdown

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

## 📝 Logging

All bot activity is logged to:

- **Console**: Real-time output
- **File**: `logs/trading_bot.log`

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
