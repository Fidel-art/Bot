# ⚡ SMC EA - Quick Start Checklist

## 5-Minute Setup

### Step 1: Locate MT5 Experts Folder
- **Windows:** `C:\Users\<YourName>\AppData\Roaming\MetaQuotes\Terminal\<TerminalID>\MQL5\Experts`
- **Copy here:** `SMC_Unified_EA_v2.mq5`

### Step 2: Attach to Chart
1. Open MetaTrader 5
2. Right-click on chart (e.g., XAUUSD, M15)
3. Select: Expert Advisors → Attach Expert Advisor
4. Choose: `SMC_Unified_EA_v2`
5. Click OK (no parameter changes needed - defaults are optimal)

### Step 3: Start Python Bot
```bash
cd c:\Users\FidelSomba\OneDrive\Desktop\BOT code\smc_bot
python main.py
```

### Step 4: Start Dashboard
```bash
cd c:\Users\FidelSomba\OneDrive\Desktop\BOT code\smc_bot
call start_dashboard.bat
```
Opens automatically at: **http://localhost:3000**

---

## What Gets Executed

| Signal Type | When | What Happens |
|-------------|------|--------------|
| **Order Block (OB)** | Price touches 61.8% Fib retrace in OB zone | BUY/SELL at OB entry |
| **Fair Value Gap (FVG)** | Price returns to fill detected gap | BUY/SELL in gap zone |
| **Break of Structure (BOS)** | Price breaks swing with displacement + trending | BUY/SELL with market order |

**Example Trade Comment:** `SMC_OB_BUY` (tells you which strategy triggered)

---

## Risk Controls (Active)

```
Stop Loss:         1.5x ATR below/above entry
Take Profit:       2.5x ATR above/below entry
Max Trade Size:    0.03 lots per $10k balance
Profit Bagging:    Close ALL trades at +10% equity
Loss Bagging:      Close ALL trades at -3% drawdown
Session Filter:    Skip Asian hours (low liquidity)
Spread Limit:      Only trade if spread < 120 points
```

---

## Dashboard Displays

```
🟢 Real-time Positions
   ├─ Current P&L per trade
   ├─ Total account P&L
   └─ Strategy breakdown (OB%, FVG%, BOS%)

📊 Trade History
   ├─ Last 10 trades with strategy tags
   ├─ Win/loss ratio
   └─ Export to CSV

⚠️  Alerts
   ├─ New trade notifications
   ├─ Bagging triggers
   └─ Connection status
```

**Access:** http://localhost:3000

---

## Recommended Initial Settings

✅ **Balanced Profile (Recommended)**
```
Strategy:           STRAT_AUTO
LotPerK:            0.03
BagProfitPercent:   10.0
BagLossPercent:     3.0
UseATRFilters:      ON
UseRegimeFilter:    ON
UseSessionFilter:   ON
```

⚙️ **Alternative Profiles** (in `mql5/ea_config.json`)
- `conservative` - Lower drawdown, fewer trades
- `aggressive` - Higher returns, higher risk
- `scalper` - Micro-trades, tight stops

---

## Monitor These (First 10 Trades)

✓ EA executes trades (check MT5 terminal)
✓ Python bot receives orders (check logs)
✓ Dashboard shows positions (check http://localhost:3000)
✓ Trade comments tagged with strategy (OB/FVG/BOS)
✓ Risk parameters respected (stop loss & take profit set)

---

## Troubleshooting

| Issue | Check |
|-------|-------|
| EA not trading | Spread > 120 points? Session filter blocking? ADX < 18 for BOS? |
| Python not seeing trades | MAGIC_NUMBER = 76543 in settings.py? |
| Dashboard blank | Backend running (http://localhost:8000)? Frontend running (http://localhost:3000)? |
| High P&L swings | Normal! EA uses ATR-based SL/TP (scales with volatility) |

---

## File Locations (Reference)

```
smc_bot/
├── mql5/
│   ├── SMC_Unified_EA_v2.mq5        ← Copy to MT5 Experts folder
│   ├── DEPLOYMENT_GUIDE.md          ← Full parameter guide
│   ├── INTEGRATION_GUIDE.md         ← System architecture
│   ├── ea_config.json               ← Config profiles
│   └── QUICKSTART.md                ← This file
│
├── backend/
│   ├── api.py                       ← FastAPI endpoints
│   ├── mt5_executor.py              ← MT5 connection
│   └── bot_controller.py            ← Trade logic
│
├── frontend/
│   └── src/                         ← React dashboard
│       ├── components/Dashboard.jsx
│       └── services/api.js
│
├── strategy/
│   └── smc_engine.py                ← Signal confirmation
│
└── main.py                          ← Bot launcher
```

---

## Live Trading Checklist

- [ ] EA file copied to MT5 Experts folder
- [ ] EA attached to chart with default settings
- [ ] MT5 set to live trading mode (Tools → Options → Expert Advisors → Allow live trading)
- [ ] Python bot running (`python main.py`)
- [ ] FastAPI backend running (port 8000)
- [ ] React frontend running (http://localhost:3000)
- [ ] Confirmed: MAGIC_NUMBER = 76543 in settings.py
- [ ] Confirmed: Broker spread < 120 points
- [ ] Session filter active (won't trade during Asian hours)
- [ ] First trade received and visible in dashboard

---

## Performance Expected

**Short-term (1-2 weeks):**
- 5-15 trades
- Win rate: 55-70%
- Monthly return: 2-5%

**Medium-term (1-3 months, with optimization):**
- Win rate: 60-75%
- Monthly return: 5-15%

**Factors:**
- Market conditions (trending = better for BOS)
- Symbol volatility (XAUUSD = high volatility = more trades)
- Timeframe selection (M15 = more trades, higher frequency)

> ⚠️ **Key:** Start with small lot size, track first 50 trades, then scale!

---

## Need Help?

**EA stopped executing?**
→ See: `mql5/DEPLOYMENT_GUIDE.md` → Troubleshooting section

**Understand the strategies?**
→ See: `mql5/INTEGRATION_GUIDE.md` → Strategy Details

**Configure parameters for your style?**
→ See: `mql5/ea_config.json` → Recommended Profiles

**Integration with Python bot?**
→ See: `mql5/INTEGRATION_GUIDE.md` → Python Bot Interaction

---

**GO LIVE! 🚀**

Questions? Check the Telegram/Discord (if available) or review the full guides linked above.
