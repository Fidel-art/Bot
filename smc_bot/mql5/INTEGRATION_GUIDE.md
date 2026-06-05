# System Integration Guide: MQL5 EA + Python Bot

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     MetaTrader 5 Platform                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  SMC_Unified_EA_v2.mq5                             │    │
│  │  - Order Block Detection & Trading                 │    │
│  │  - Fair Value Gap Detection & Trading              │    │
│  │  - Break of Structure Detection & Trading          │    │
│  │  - Adaptive Filters (ATR, ADX, Sessions)           │    │
│  │  - Bagging System (Auto Close on Targets)          │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓ Executes Orders                  │
│  ┌────────────────────────────────────────────────────┐    │
│  │            Live Trading Execution                  │    │
│  │  - Position Management                              │    │
│  │  - Order Execution (Ask/Bid)                        │    │
│  │  - Trade Comments Tagging (OB/FVG/BOS)             │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ MT5 API
┌─────────────────────────────────────────────────────────────┐
│              Python SMC Trading Bot System                   │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  MT5 Executor (Python)                             │    │
│  │  - Connects to MT5 via MetaTrader5 library         │    │
│  │  - Reads positions and trade history               │    │
│  │  - Can place/modify/close orders                   │    │
│  │  - Logs all execution events                       │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↑ ↓                                 │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Python SMC Engine                                 │    │
│  │  - Advanced analysis & signal confirmation         │    │
│  │  - Multi-timeframe analysis                        │    │
│  │  - Risk calculations                               │    │
│  │  - Trade history analysis                          │    │
│  └────────────────────────────────────────────────────┘    │
│                          ↓                                   │
│  ┌────────────────────────────────────────────────────┐    │
│  │  FastAPI Backend (api.py)                          │    │
│  │  - REST endpoints for bot status                   │    │
│  │  - Position data API                               │    │
│  │  - Trade history API                               │    │
│  │  - Risk metrics API                                │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
                          ↓ HTTP
┌─────────────────────────────────────────────────────────────┐
│            React Web Dashboard (Frontend)                    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │  Live Dashboard (localhost:3000)                   │    │
│  │  - Real-time position monitoring                   │    │
│  │  - Trade alerts with strategy type                 │    │
│  │  - Risk metrics visualization                      │    │
│  │  - Trade history export (CSV)                      │    │
│  │  - Account performance analytics                   │    │
│  └────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

---

## How the MQL5 EA Integrates

### 1. **Primary Execution (MT5-Native)**
- **Location:** MetaTrader 5 terminal
- **Role:** Real-time market data processing and trade execution
- **Speed:** Fastest (no network latency)
- **Strategies:**
  - Order Block detection → Entry via Fib retracement
  - FVG detection → Entry on gap touch
  - BOS detection → Entry on structural break

### 2. **Trade Identification**
Every trade executed by the EA includes a **comment** tag:
```
"SMC_OB_BUY"   → Order block long entry
"SMC_OB_SELL"  → Order block short entry
"SMC_FVG_BUY"  → Fair value gap long entry
"SMC_FVG_SELL" → Fair value gap short entry
"SMC_BOS_BUY"  → Break of structure long entry
"SMC_BOS_SELL" → Break of structure short entry
```

### 3. **Python Bot Interaction**
Your Python backend:
```python
# mt5_executor.py reads all positions
positions = mt5.positions_get()

for pos in positions:
    magic = pos.magic  # Will match MagicNumber 76543
    comment = pos.comment  # "SMC_OB_BUY" etc.
    
    # Your bot can:
    # 1. Monitor for strategy confirmation
    # 2. Calculate additional hedges (future feature)
    # 3. Log to database for analytics
    # 4. Send alerts to dashboard
```

### 4. **Dashboard Integration**
The frontend displays:
- **Trade Alerts:** "OB BUY SIGNAL: XAUUSD @ 2450.50"
- **Strategy Distribution:** Chart showing % of trades from OB vs FVG vs BOS
- **Performance by Strategy:** Win rate comparison
- **Trade Tags:** Each trade shows its originating strategy

---

## Setup Workflow

### Phase 1: Deploy EA to MT5 (One-time Setup)
```bash
1. Copy SMC_Unified_EA_v2.mq5 to:
   C:\Users\<You>\AppData\Roaming\MetaQuotes\Terminal\<ID>\MQL5\Experts\

2. Open MT5 → Right-click chart → Attach Expert Advisor

3. Configure inputs (see ea_config.json for profiles)

4. Click OK → EA starts execution
```

### Phase 2: Python Bot Monitors & Enhances
```python
# Your Python bot automatically:

1. Connects to MT5 via MetaTrader5 library
2. Reads all positions created by the EA
3. Updates dashboard with real-time data
4. Analyzes trades for performance metrics
5. Can place additional orders if needed (future)
```

### Phase 3: Dashboard Shows Everything
```
Browser: http://localhost:3000
├── Real-time positions (from MT5 EA)
├── Trade history (strategy tags visible)
├── P&L by strategy
└── Risk metrics (from Python calculations)
```

---

## Configuration Priorities

### EA Parameter Settings (First Priority)
Configure in MT5 Expert Advisor properties:
```
Strategy:           STRAT_AUTO (use all three)
LotPerK:            0.03 (or adjust for risk appetite)
BagProfitPercent:   10.0 (close all at +10% equity)
BagLossPercent:     3.0 (close all at -3% equity)
```

**See `mql5/ea_config.json` for predefined profiles:**
- `conservative` - Low drawdown
- `aggressive` - High returns, higher risk
- `balanced` - Recommended defaults
- `scalper` - Frequent small trades

### Python Bot Settings (Second Priority)
Configure in `smc_bot/config/settings.py`:
```python
SYMBOL = "XAUUSD"
MAGIC_NUMBER = 76543  # MUST match EA MagicNumber
MT5_LOGIN = your_login
MT5_PASSWORD = your_password
MT5_SERVER = "your_broker_server"
```

### Risk Management (Critical)
Both EA and Python apply controls:
```
EA Level:        Bagging system (close all on profit/loss targets)
Python Level:    Position monitoring, trade analytics
Dashboard Level: Real-time alerting and visualization
```

---

## Expected Behavior During Live Trading

### Minute-by-Minute (While Market is Open)

**MT5 Terminal:**
```
10:15 AM → EA detects Order Block, waits for price
10:22 AM → Price touches 61.8% Fib retracement
10:23 AM → EA executes BUY trade (comment: "SMC_OB_BUY")
10:23 AM → Position sent to Python via MT5 API
10:23 AM → Dashboard updates: "New OB BUY at $XXXX"
```

**Python Bot (continuous monitoring):**
```
- Reads position from MT5
- Calculates unrealized P&L
- Updates backend API
- Frontend fetches and shows in real-time
```

**Dashboard (user perspective):**
```
- Position card appears with green "OB" tag
- Trade comment/alert notification
- P&L updates every tick
- Historical record saved to database
```

### On Bagging Trigger
```
If equity ≥ balance × 1.10 (10% profit):
  → EA closes ALL positions
  → Python detects position closure
  → Dashboard shows "Profit Bagging Triggered: +10%"
  → System resets for next cycle
```

---

## Common Questions

### Q: Does the Python bot need to run continuously?
**A:** Yes, keep your system running:
```bash
smc_bot/
├── main.py (trading bot loop)
├── backend/ (FastAPI server)
└── frontend/ (React dashboard, http://localhost:3000)
```

### Q: Can I modify EA parameters without restarting?
**A:** Yes! Right-click chart → Expert Advisors → Properties. Change inputs and re-init.
Parameters update on next bar (except MagicNumber, which requires restart).

### Q: What if MT5 disconnects?
**A:** 
- EA stops executing
- Python bot logs the error
- Reconnection automatic when MT5 comes back online
- Dashboard shows connection status

### Q: Can I run multiple EAs?
**A:** Yes! Use different `MagicNumber` values:
```
EA1: MagicNumber = 76543 (Order Blocks)
EA2: MagicNumber = 76544 (Different pair)
```
Each Python instance monitors its Magic Number.

### Q: How do I backtest the EA?
**A:** 
1. MT5 → View → Strategy Tester
2. Select your EA, symbol, period
3. Set date range and run
4. Review equity curve and metrics

---

## Next Steps

1. **Deploy EA:**
   ```
   Copy SMC_Unified_EA_v2.mq5 to MT5 Experts folder
   Attach to chart (e.g., XAUUSD, M15)
   Configure inputs from ea_config.json profiles
   ```

2. **Verify Python Integration:**
   ```bash
   cd smc_bot
   python main.py
   # Verify MT5 connection successful
   ```

3. **Start Dashboard:**
   ```bash
   start_dashboard.bat
   # Opens http://localhost:3000
   ```

4. **Monitor First Trades:**
   - Watch MT5 terminal for execution
   - Check dashboard for position appearance
   - Verify trade comments are recorded

5. **Optimize:**
   - Run backtest for 50+ bars
   - Adjust parameters based on results
   - Monitor performance over 1-2 weeks live

---

## Support & Troubleshooting

**EA not executing?**
- Check `UseSessionFilter` (blocks Asian hours 1-7 UTC)
- Verify spread < `MaxSpreadPoints` (120 default)
- Ensure market is open

**Python bot not seeing trades?**
- Verify `MAGIC_NUMBER` in settings.py matches EA
- Check MT5 connection in logs

**Dashboard not updating?**
- Backend running? Check `http://localhost:8000/docs`
- Frontend running? Check `http://localhost:3000`
- Browser console for JavaScript errors

---

**Ready to trade! 🚀**

For detailed parameter explanations, see: `mql5/DEPLOYMENT_GUIDE.md`
For JSON config options, see: `mql5/ea_config.json`
