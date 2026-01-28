# System Architecture - SMC Trading Bot

## Component Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           USER INTERACTION                              │
│                                                                         │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐           │
│  │   Start Bot  │───▶│Select Profile│───▶│ Choose Mode  │           │
│  └──────────────┘    └──────────────┘    └──────────────┘           │
│                            │                     │                      │
│                            │                     ├─────▶ Trade Mode     │
│                            │                     └─────▶ Analytics Mode │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                      PROFILE MANAGEMENT LAYER                           │
│                                                                         │
│  ┌───────────────────────────────────────────────────────────────┐    │
│  │  ProfileManager (config/trader_profile.py)                    │    │
│  │  - Load profiles from JSON                                    │    │
│  │  - Create/Select/Delete profiles                              │    │
│  │  - Store MT5 credentials & risk settings                      │    │
│  │  - Manage trader-specific configurations                      │    │
│  └───────────────────────────────────────────────────────────────┘    │
│                               │                                         │
│                               ▼                                         │
│         ┌─────────────────────────────────────────┐                   │
│         │ trader_profiles.json                    │                   │
│         │ { trader1: {...}, trader2: {...} }      │                   │
│         └─────────────────────────────────────────┘                   │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         CORE TRADING ENGINE                             │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  SMCTradingBot (main.py)                                        │  │
│  │  - Orchestrates all components                                  │  │
│  │  - Main trading loop                                            │  │
│  │  - Uses trader profile settings                                 │  │
│  └─────────────────────────────────────────────────────────────────┘  │
│                               │                                         │
│              ┌────────────────┼────────────────┐                       │
│              ▼                ▼                ▼                       │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                │
│    │   Market    │  │  Strategy   │  │    Risk     │                │
│    │    Data     │  │   Engine    │  │  Manager    │                │
│    └─────────────┘  └─────────────┘  └─────────────┘                │
│           │                │                 │                         │
│           └────────────────┴─────────────────┘                         │
│                          │                                             │
│                          ▼                                             │
│               ┌─────────────────────┐                                 │
│               │   Trade Executor    │                                 │
│               │  (mt5_executor.py)  │                                 │
│               └─────────────────────┘                                 │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                     DISPLAY & ANALYTICS LAYER                           │
│                                                                         │
│  ┌───────────────────────────┐    ┌───────────────────────────────┐  │
│  │  Dashboard                │    │  Trade Analyzer                │  │
│  │  (dashboard/dashboard.py) │    │  (dashboard/trade_analyzer.py) │  │
│  │                           │    │                                 │  │
│  │  - Real-time display      │    │  - Load trade history           │  │
│  │  - Signal indicators      │    │  - Calculate statistics         │  │
│  │  - Account metrics        │    │  - Performance reports          │  │
│  │  - Risk visualization     │    │  - CSV export                   │  │
│  │  - Position monitoring    │    │                                 │  │
│  │  - Trade notifications    │    │                                 │  │
│  └───────────────────────────┘    └───────────────────────────────┘  │
│              │                                    │                     │
│              │                                    │                     │
│              ▼                                    ▼                     │
│   ┌─────────────────┐                 ┌──────────────────────┐       │
│   │ Colorful Console│                 │  trade_history.json   │       │
│   │    Display      │                 │  trades_{id}.json     │       │
│   └─────────────────┘                 └──────────────────────┘       │
└─────────────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                       EXTERNAL INTEGRATION                              │
│                                                                         │
│  ┌─────────────────────────────────────────────────────────────────┐  │
│  │  MetaTrader 5 Platform                                          │  │
│  │  - Execute orders                                               │  │
│  │  - Fetch market data                                            │  │
│  │  - Monitor positions                                            │  │
│  │  - Account management                                           │  │
│  └─────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
```

## Data Flow for Trade Execution

```
1. USER runs bot
   │
2. ProfileManager loads trader settings
   │
3. SMCTradingBot initializes with profile
   │
4. Analysis Cycle (every 5 minutes):
   │
   ├──▶ MarketDataHandler fetches MT5 data
   │    │
   │    └──▶ SMCEngine analyzes market structure
   │         │
   │         └──▶ Generates BUY/SELL signal
   │              │
   │              ├──▶ Dashboard shows signal
   │              │
   │              └──▶ RiskManager validates trade
   │                   │
   │                   └──▶ MT5Executor places order
   │                        │
   │                        ├──▶ Dashboard shows notification
   │                        │
   │                        └──▶ TradeAnalyzer saves to history
   │
5. Loop continues...
```

## Profile-Based Configuration Flow

```
┌──────────────────┐
│  Trader Profile  │
│                  │
│  - MT5 Login     │────────┐
│  - Password      │        │
│  - Server        │        │    ┌─────────────────────┐
│  - Lot Size      │────────┼───▶│  SMCTradingBot      │
│  - Max Drawdown  │        │    │  Uses these values  │
│  - Risk/Trade    │        │    └─────────────────────┘
│  - Max Trades    │        │
│  - Min R:R       │────────┘
│  - Sessions      │
│  - History File  │────────┐
└──────────────────┘        │
                            │    ┌─────────────────────┐
                            └───▶│  TradeAnalyzer      │
                                 │  Saves to custom    │
                                 │  history file       │
                                 └─────────────────────┘
```

## Dashboard Update Flow

```
Analysis Cycle Runs
      │
      ├──▶ Fetch Account Info
      │    (balance, equity, profit)
      │
      ├──▶ Get Risk Status
      │    (drawdown %, remaining buffer)
      │
      ├──▶ Get Positions Data
      │    (count, details, P/L)
      │
      ├──▶ Get Market Signal
      │    (BUY / SELL / NONE)
      │
      └──▶ Dashboard.display_full_dashboard()
           │
           ├──▶ Print Signal Status (with colors)
           ├──▶ Print Account Info (with colors)
           ├──▶ Print Risk Metrics (with progress bar)
           └──▶ Print Open Positions (with details)
```

## Multi-User Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Single Bot Installation                │
└─────────────────────────────────────────────────────────────┘
                            │
        ┌───────────────────┼───────────────────┐
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  Profile 1   │    │  Profile 2   │    │  Profile 3   │
│              │    │              │    │              │
│  Trader: A   │    │  Trader: B   │    │  Trader: C   │
│  MT5: 11111  │    │  MT5: 22222  │    │  MT5: 33333  │
│  Risk: 5%    │    │  Risk: 3%    │    │  Risk: 10%   │
│  Lots: 0.01  │    │  Lots: 0.001 │    │  Lots: 0.02  │
└──────────────┘    └──────────────┘    └──────────────┘
        │                   │                   │
        ▼                   ▼                   ▼
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│ History A    │    │ History B    │    │ History C    │
│ trades_a.json│    │ trades_b.json│    │ trades_c.json│
└──────────────┘    └──────────────┘    └──────────────┘
```

## File Dependencies

```
main.py
  ├── imports config.settings
  ├── imports config.trader_profile
  ├── imports data.market_data
  ├── imports strategy.smc_engine
  ├── imports risk.risk_manager
  ├── imports execution.mt5_executor
  ├── imports dashboard.dashboard
  └── imports dashboard.trade_analyzer

mt5_executor.py
  └── imports dashboard.dashboard (lazy load)

trader_profile.py
  └── reads/writes config/trader_profiles.json

trade_analyzer.py
  └── reads/writes data/trade_history.json
                  or data/trades_{trader_id}.json
```

## Component Responsibilities

| Component | Responsibility | Files |
|-----------|----------------|-------|
| **ProfileManager** | Manage multiple trader profiles | `config/trader_profile.py` |
| **SMCTradingBot** | Main orchestration & trading loop | `main.py` |
| **MarketDataHandler** | Fetch MT5 market data | `data/market_data.py` |
| **SMCEngine** | Analyze market & generate signals | `strategy/smc_engine.py` |
| **RiskManager** | Validate risk & protect account | `risk/risk_manager.py` |
| **MT5Executor** | Execute trades on MT5 | `execution/mt5_executor.py` |
| **Dashboard** | Display real-time status | `dashboard/dashboard.py` |
| **TradeAnalyzer** | Analyze & report performance | `dashboard/trade_analyzer.py` |

## Key Features Integration

### Real-Time Dashboard
- **Integrated in**: main.py (analysis cycle)
- **Called by**: SMCTradingBot during each cycle
- **Updates**: Account info, signals, risk, positions
- **Display**: Colorful terminal with progress bars

### Trade History
- **Saved by**: main.py after trade execution
- **Managed by**: TradeAnalyzer
- **Storage**: JSON files (default or per-trader)
- **Accessible**: Via analytics menu option

### Multi-User
- **Managed by**: ProfileManager
- **Selected at**: Bot startup
- **Applied to**: All bot components
- **Separates**: Credentials, settings, history

## Execution Flow Timeline

```
T+0s    User runs: python main.py
T+1s    ProfileManager loads profiles
T+2s    User selects profile (or creates new)
T+3s    SMCTradingBot initializes with profile settings
T+5s    Components initialize (MT5, strategy, risk, executor)
T+10s   User selects "Start Trading"
T+15s   First analysis cycle begins
T+20s   Dashboard displays with current data
T+25s   Signal detected: BUY
T+30s   Risk validated, order placed
T+31s   Dashboard shows trade notification (3 seconds)
T+34s   Trade saved to history
T+35s   Dashboard returns to main display
T+335s  Next cycle (5 minutes later)
...
```

This architecture ensures:
- ✅ Clear separation of concerns
- ✅ Easy to maintain and extend
- ✅ Multi-user support without conflicts
- ✅ Real-time feedback to users
- ✅ Comprehensive trade tracking
- ✅ Professional user experience
