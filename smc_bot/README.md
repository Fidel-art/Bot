# XAUUSD SMC/ICT Trading Bot

An automated trading bot for Gold (XAUUSD) built with Python and MetaTrader 5, implementing **Smart Money Concepts (SMC)** and **Inner Circle Trader (ICT)** methodologies. It ships with a full web dashboard for bot control, live trading statistics (sourced from real MT5 data), subscription management, and multi-user support.

## Architecture

The system is split across the **Windows host** and **Docker containers**:

```
┌────────────────────────────── WINDOWS HOST ───────────────────────────────┐
│  MetaTrader 5 terminal  +  MT5 Bridge (FastAPI/uvicorn, port 8765)         │
│  └── mt5_bridge/server.py  exposes MT5 over REST for the containers        │
└──────────────────────────────────▲────────────────────────────────────────┘
                                   │ http://host.docker.internal:8765
┌──────────────────────────────────┴──────────── DOCKER ────────────────────┐
│  frontend  (React/Vite, port 3000)   — web dashboard                      │
│  backend   (FastAPI, port 8000)      — REST API + bot control             │
│  bot       (main.py / bot_run.py)    — trading engine                     │
│  database  (SQLite volume holder)    — trades, users, subscriptions        │
│                                                                           │
│  All MT5 calls go through mt5_proxy, which shadows MetaTrader5 and         │
│  routes every call over HTTP to the bridge on the Windows host.            │
└────────────────────────────────────────────────────────────────────────────┘
```

- **MT5 Bridge** (`mt5_bridge/`) runs on the Windows host and wraps `MetaTrader5`.
- **MT5 Proxy** (`mt5_proxy/`) shadows the real (Windows-only) `MetaTrader5` package inside containers, so the same code works in Docker.
- `docker-compose.yml` wires everything with `MT5_BRIDGE_URL=http://host.docker.internal:8765`.

## Prerequisites

1. **Windows PC** (required for MetaTrader 5)
2. **Python 3.10+** on the host (for the MT5 Bridge)
3. **Docker Desktop** (with WSL2 backend)
4. **MetaTrader 5** installed, logged into a trading account, with "Allow automated trading" enabled (Tools → Options → Expert Advisors)

## Quick Start

### 1. Run everything in one command

```bat
start_dashboard.bat
```

This sets up the Python venv, starts the MT5 Bridge in a terminal window, builds/starts the Docker containers, and health-checks all services.

### 2. Manual startup (equivalent steps)

```bat
:: Terminal 1 — start the MT5 Bridge on the Windows host
start_bridge.bat
```

```bat
:: Terminal 2 — start the Docker stack
docker-compose up -d
```

### 3. Open the dashboard

| Service      | URL                          |
|--------------|------------------------------|
| Web Dashboard| http://localhost:3000        |
| Backend API  | http://localhost:8000        |
| API Docs     | http://localhost:8000/docs   |
| MT5 Bridge   | http://localhost:8765/health |

## How the Bot Starts

1. The **MT5 Bridge** must be running on the Windows host (port 8765).
2. In the dashboard → **Bot Setup** tab, enter your MT5 credentials and click **Start Bot**.
3. The backend saves a config to `config/trader_configs/<trader>_config.json`.
4. The **bot** container's runner (`bot_run.py`) watches that directory and launches `main.py` with the trader's settings.
5. `main.py` connects to MT5 through the proxy → bridge, analyzes the market, and trades automatically.

## Features

### SMC / ICT Strategy
- Market structure (HH, HL, LH, LL), Break of Structure (BOS), Change of Character (CHoCH)
- Order blocks, Fair Value Gaps (FVG), liquidity sweeps
- Multi-timeframe analysis: D1 (bias), H4 (structure), H1 (zones), M15 (entry)

### Web Dashboard
- **Dashboard** — bot control, live MT5 status, real trading statistics
- **Bot Setup** — per-trader MT5 credentials and bot configuration
- **Risk Management** — risk-per-trade, lot sizing, max drawdown
- **Subscription** — plan management and activation

### Trading Statistics (from real MT5 data)
Statistics are computed directly from `mt5.history_deals_get()` and `mt5.positions_get()`, not guesses:
- Total / open / closed trades
- **Winning trades** and **losing trades**
- **Win rate** = winning / (winning + losing) trades
- Total P&L, average profit/trade, best & worst trade
- Profit factor

### Risk Management
- Maximum drawdown protection (default 5%, HARD LOCK — creates `drawdown_lock.txt`)
- Trade-level risk validation and minimum 1:2 risk-reward
- Automatic SL/TP management

### Multi-User & Subscription
- Separate trader profiles with individual MT5 credentials and risk settings
- Weekly / Monthly / Quarterly / Yearly / Lifetime plans (+ 3-day free trial)
- License key activation and expiry enforcement

## Project Structure

```
smc_bot/
│
├── backend/               # FastAPI REST API (runs in Docker, port 8000)
│   ├── api.py             #   all API routes (auth, bot control, stats, MT5 status)
│   ├── bot_controller.py  #   bot lifecycle + bridge launch/health
│   └── Dockerfile
│
├── frontend/              # React + Vite web dashboard (port 3000)
│   └── src/components/    #   Dashboard, BotSetup, RiskManagement, SubscriptionPlans
│
├── mt5_bridge/            # Windows-host REST wrapper for MetaTrader5 (port 8765)
│   └── server.py
│
├── mt5_proxy/             # MetaTrader5 drop-in shadow that routes to the bridge
│   └── MetaTrader5/__init__.py
│
├── database/              # SQLite schema + manager (trades, users, subscriptions)
├── dashboard/             # Console dashboard + trade analyzer
├── data/                  # Trade history, DB files (volume-mounted)
├── config/                # Settings, trader profiles, subscriptions, trader_configs/
├── execution/             # MT5 trade executor
├── strategy/              # SMC/ICT engine
├── risk/                  # Risk manager
│
├── bot_run.py             # Docker entry for the bot container (config watcher)
├── main.py                # Trading engine entry point
├── backend/requirements.txt, requirements.txt
│
├── start_bridge.bat       # Starts MT5 Bridge on the Windows host
├── start_dashboard.bat    # Full-system launcher (bridge + docker-compose)
├── run_bot.bat            # Local bot launcher
├── install.bat            # One-time dependency setup
│
├── docker-compose.yml     # frontend + backend + database + bot
├── Dockerfile.bot         # Bot container image
└── .env                   # Environment overrides (copy from .env.example)
```

## Configuration

### `.env`
Copy `.env.example` to `.env` and fill in your values:

```env
SECRET_KEY=change-this-to-a-secure-random-string
DATABASE_PATH=/app/data/bot_dashboard.db
MT5_LOGIN=your_mt5_login
MT5_PASSWORD=your_mt5_password
MT5_SERVER=your_mt5_server
```

- Inside Docker, `MT5_BRIDGE_URL` is set to `http://host.docker.internal:8765`.
- For a backend running directly on Windows, the containers use `host-gateway` so `host.docker.internal` resolves to the host.

### Risk Parameters (`config/settings.py`)

```python
MAX_DRAWDOWN_PERCENT = 5.0    # Maximum account drawdown
LOT_SIZE = 0.001              # Fixed lot size
RISK_PER_TRADE_PERCENT = 1.0  # Risk per trade
MIN_RISK_REWARD = 2.0         # Minimum RR ratio
```

## Troubleshooting

### ⚠️ "MT5 Bridge is not running"
The bridge must run on the **Windows host** (containers cannot reach the `MetaTrader5` terminal directly):

1. Open a terminal in the `smc_bot` directory
2. Run `start_bridge.bat` (or `python -m uvicorn mt5_bridge.server:app --host 0.0.0.0 --port 8765`)
3. Verify it at `http://127.0.0.1:8765/health` → `{"status": "ok", ...}`
4. On the dashboard, click **Recheck Status**

The dashboard "Start Bridge" button auto-launches the bridge in a new terminal when the backend runs natively, and shows the instructions above when the backend runs in Docker.

### Dashboard shows 0 win rate / no trades
- Confirm the MT5 Bridge is running (see above)
- The statistics come from real MT5 deals — a new/demo account with no closed positions will show zeros
- Win rate = winning / (winning + losing) trades; breakeven trades are excluded

### "MT5 initialization failed"
- Ensure MetaTrader 5 is running and logged in
- Verify "Allow automated trading" is enabled
- Check that only one MT5 terminal instance is bound to port 8765

### Docker can't reach the bridge
- `host.docker.internal` is configured via `extra_hosts` in `docker-compose.yml`
- Ensure the Windows firewall allows inbound connections to port 8765

## Documentation

- **[DOCKER_GUIDE.md](DOCKER_GUIDE.md)** — Docker deployment guide
- **[START_SYSTEM_GUIDE.md](START_SYSTEM_GUIDE.md)** — step-by-step startup
- **[ARCHITECTURE.md](ARCHITECTURE.md)** & **[INDEPENDENT_ARCHITECTURE.md](INDEPENDENT_ARCHITECTURE.md)** — system design
- **[QUICKSTART.md](QUICKSTART.md)** — getting started
- **[SUBSCRIPTION_GUIDE.md](SUBSCRIPTION_GUIDE.md)** — subscription system
- **[CHANGES.md](CHANGES.md)** — change log

## Logging

- `logs/trading_bot.log` — bot activity (auto-created)
- `docker-compose` container logs — `docker logs smc_bot_backend`, `docker logs smc_bot_core`
- MT5 Bridge — output in its terminal window

## Disclaimer

This bot is for educational and research purposes. Trading forex and CFDs carries a high level of risk and may not be suitable for all investors. Never invest money you cannot afford to lose. Always test strategies on a demo account before live trading.

## License

Provided as-is for educational purposes.