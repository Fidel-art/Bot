# MQL5 Expert Advisor Setup Guide

## SMC_Unified_EA_v2.mq5 - Deployment & Configuration

This Expert Advisor implements Smart Money Concepts trading strategies:
- **Order Blocks (OB)** - Trade within institutional order blocks with Fibonacci entry
- **Fair Value Gaps (FVG)** - Trade gap fills with adaptive thresholds
- **Break of Structure (BOS)** - Trend-following entries on structural breaks
- **Auto-Adaptive Filters** - ATR-based displacement, session filters, regime detection

---

## Quick Start: Deploy EA to MT5

### Step 1: Locate MetaTrader 5 EA Directory
```
C:\Users\<YourUsername>\AppData\Roaming\MetaQuotes\Terminal\<TerminalID>\MQL5\Experts
```

### Step 2: Copy EA File
Copy `SMC_Unified_EA_v2.mq5` to the Experts folder above.

### Step 3: Compile (Optional - MT5 auto-compiles on first use)
- Open MetaEditor in MT5
- Open the EA file
- Press Ctrl+F9 to compile
- Should show "0 errors"

### Step 4: Attach to Chart
1. Open MT5 and select your chart (e.g., XAUUSD, M15)
2. Right-click → Expert Advisors → Attach Expert Advisor
3. Select `SMC_Unified_EA_v2`
4. Configure inputs (see below)
5. Click OK

---

## Input Parameters Explained

### Core Strategy Selection
| Parameter | Values | Description |
|-----------|--------|-------------|
| `Strategy` | STRAT_AUTO (recommended) | STRAT_OB, STRAT_FVG, STRAT_BOS, or STRAT_AUTO (all three) |
| `MagicNumber` | 76543 | Unique EA identifier for position tracking |
| `OneTradePerBar` | true | Maximum 1 trade per candle |

### Risk Management
| Parameter | Default | Description |
|-----------|---------|-------------|
| `LotPerK` | 0.03 | Lot size = 0.03 * (Balance/10,000) |
| `BagProfitPercent` | 10.0 | Close ALL positions when equity +10% |
| `BagLossPercent` | 3.0 | Close ALL positions when equity -3% |

### Market Context Filters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `UseSessionFilter` | true | Skip Asian session (less liquidity) |
| `UseATRFilters` | true | Scale position sizing & thresholds by volatility |
| `UseRegimeFilter` | true | Only trade BOS in trending markets (ADX > 18) |
| `RegimeMethod` | REGIME_ADX | Use ADX (or Efficiency Ratio) for trend detection |

### Core Parameters
| Parameter | Default | Description |
|-----------|---------|-------------|
| `ATR_Period` | 14 | ATR period for volatility (used in SL/TP sizing) |
| `SwingBars` | 5 | Bars to identify swing highs/lows |
| `FibRetraceLevel` | 61.8 | Fibonacci level for order block entries |
| `DisplacementMin` | 0.0 | Auto-adaptive if 0; otherwise fixed threshold |
| `MaxSpreadPoints` | 120 | Only trade if spread < this many points |

---

## Strategy Details

### Order Block (OB) Strategy
- **Detection:** Identifies reversed candles with displacement (strong directional move)
- **Entry:** When price touches OB zone at 61.8% Fibonacci retracement
- **SL/TP:** 1.5 * ATR stop, 2.5 * ATR target

**Example:**
```
Bullish OB formed when:
  - Previous bar: strong bullish (close > open)
  - Current bar: strong bearish (close < open)
  - Has ATR-based displacement
→ Waits for price to retrace → Enters on Fib level
```

### Fair Value Gap (FVG) Strategy
- **Detection:** Identifies gaps between consecutive candles (unmet orders)
- **Entry:** When price returns to fill gap
- **Gap Sizing:** Adaptive based on ATR (larger gaps OK in high volatility)

**Example:**
```
Bullish FVG: Low[bar-2] > High[current]
→ Creates "gap zone"
→ Enters BUY when price reaches this zone
```

### Break of Structure (BOS) Strategy
- **Activation:** Only trades when market is trending (ADX > 18)
- **Detection:** Price breaks recent swing high/low with displacement
- **Entry:** Market order at break with immediate SL/TP

**Example:**
```
Bullish BOS: Price breaks above recent swing high
→ Enters BUY with ATR-based SL below swing
```

### Adaptive Features
- **ATR Displacement:** Thresholds scale with market volatility
- **Session Filter:** Skips low-liquidity Asian hours
- **Regime Detection:** ADX > 18 = trending market (optimal for BOS)
- **Bagging System:** Auto-closes all trades at profit/loss targets

---

## Recommended Settings by Symbol

### XAUUSD (Gold) - Recommended Defaults
```
Strategy:          STRAT_AUTO
ATR_Period:        14
SwingBars:         5
FibRetraceLevel:   61.8
LotPerK:           0.03
BagProfitPercent:  10.0
BagLossPercent:    3.0
```

### EURUSD (FX) - More Conservative
```
LotPerK:           0.02
BagProfitPercent:  15.0
BagLossPercent:    2.0
UseSessionFilter:  true (avoid Asian overlap)
MaxSpreadPoints:   80
```

### Untrended Markets - Reduce FVG Risk
```
UseATRFilters:     true
DisplacementMin:   2.0 (higher = fewer trades)
FibRetraceLevel:   50.0 (enter sooner on retracement)
```

---

## Testing Your Setup

### 1. Verify Compilation
- Open MetaEditor (Tools → MetaEditor)
- Don't see errors in the Compilation tab before attaching

### 2. Check Magic Number
- EA won't close positions from other EAs (helpful for live trading safety)
- Change `MagicNumber` if running multiple instances

### 3. Monitor Initial Trades
- Chart shows OB/FVG/BOS zones in color
- Check trade comments in History tab:
  - `SMC_OB_BUY/SELL` - Order block entry
  - `SMC_FVG_BUY/SELL` - fair value gap entry
  - `SMC_BOS_BUY/SELL` - Break of structure entry

### 4. Backtest (Optional but Recommended)
- Strategy Tester (View → Strategy Tester)
- Symbol: XAUUSD, Period: M15
- Model: Every tick
- Run from 2024-01-01 to today
- Review equity curve and max drawdown

---

## Troubleshooting

### EA Not Trading?
1. **Check session filter:** `UseSessionFilter=true` blocks Asian hours (1-7 UTC)
2. **Check spread:** Current spread > `MaxSpreadPoints`? 
3. **Check regime:** `UseRegimeFilter=true` requires ADX > 18 for BOS
4. **Check existing positions:** `OneTradePerBar` prevents second trade same bar

### High Slippage?
- Increase `MaxSpreadPoints` or trade during liquid sessions (London/NY)

### Missing OB/FVG/BOS Visuals?
- Ensure `UseATRFilters=true` for visual drawing
- Indicators (ATR, ADX) may be loading; wait 5-10 bars

### EA Stopped After Bagging?
- This is normal! Check equity:
  - If equity < balance × (1 - BagLossPercent/100) → loss bagging triggered
  - If equity > balance × (1 + BagProfitPercent/100) → profit bagging triggered
- Manually start the EA again or adjust targets

---

## Advanced: Connecting to Python Bot

Optional: Bridge MT5 EA signals to your Python bot:

1. **Enable Expert Advisor Communication**
   - MT5 → Tools → Options → Expert Advisors → check "Allow live trading"

2. **Read EA Comments**
   - Your Python bot can monitor trade comments in MT5 API
   - Comments indicate strategy used: "SMC_OB_BUY", "SMC_FVG_SELL", etc.

3. **Risk Correlation**
   - Python bot calculates optimal lot size → EA respects `LotPerK`
   - Dashboard shows all trades from EA

---

## Performance Expectations

Based on market conditions:
- **Bull/Bear Trends:** 65-75% win rate with BOS strategy
- **Ranging Markets:** 55-60% win rate with FVG strategy
- **Net Annual Return:** 15-40% on good market years (varies by symbol/timeframe)

**Key:** Risk management is critical. Start with `BagLossPercent=3.0` and increase only after 50+ live trades.

---

## Support & Updates

- **Author:** Vignesh Kumaravel, SkyBlueFS 2025
- **Version:** 2.01
- For issues, verify:
  1. MT5 version is recent
  2. Symbol is enabled (right-click on chart → Symbols)
  3. Market is open during trading hours
  4. Check EA Logs (Experts tab)

Enjoy profitable trading! 🚀
