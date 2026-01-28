# SMC Trading Bot - Independent Architecture

## 📁 Project Structure (Independent Modules)

```
smc_bot/
├── backend/              # 🔧 Independent API Server
│   ├── api.py
│   ├── auth.py
│   ├── bot_controller.py
│   ├── requirements.txt
│   └── __init__.py
│
├── frontend/             # 💻 Independent Web Application
│   ├── src/
│   │   ├── components/
│   │   ├── services/
│   │   └── ...
│   ├── package.json
│   └── vite.config.js
│
├── database/             # 🗄️ Independent Data Layer
│   ├── db.py
│   └── __init__.py
│
├── dashboard/            # 📊 Terminal Dashboards
│   ├── dashboard.py
│   ├── enhanced_dashboard.py
│   └── trade_analyzer.py
│
├── config/               # ⚙️ Bot Configuration
├── strategy/             # 📈 Trading Strategy
├── risk/                 # 🛡️ Risk Management
├── execution/            # 🎯 Trade Execution
├── data/                 # 📂 Data Storage
└── main.py              # 🚀 Bot Core
```

## 🎯 Why Independent?

Each module can be:
- **Developed** separately by different teams
- **Deployed** independently on different servers
- **Scaled** individually based on needs
- **Tested** in isolation
- **Maintained** without affecting others

## 🔗 How They Connect

```
Frontend (Port 3000)
    ↓ HTTP REST API
Backend (Port 8000)
    ↓ Python Imports
Database Module
    ↓ SQL
SQLite File (data/bot_dashboard.db)
```

## 🚀 Running Each Module

### Backend (Independent)
```powershell
cd backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Independent)
```powershell
cd frontend
npm install  # First time
npm run dev
```

### Database (Used by Backend)
The database module is imported by the backend automatically.
Data stored in: `data/bot_dashboard.db`

### Bot Core (Independent)
```powershell
python main.py
```

## 📦 Dependencies

Each module has its own dependencies:

- **Backend**: FastAPI, JWT, bcrypt (see `backend/requirements.txt`)
- **Frontend**: React, Axios, Vite (see `frontend/package.json`)
- **Database**: SQLite3 (Python built-in)
- **Bot Core**: MT5, pandas, numpy (see root `requirements.txt`)

## 🌐 Deployment Options

### Option 1: All on One Server
- Run all modules on localhost
- Simple for development

### Option 2: Distributed
- Backend → VPS/Cloud (e.g., DigitalOcean, AWS)
- Frontend → CDN/Static Host (e.g., Netlify, Vercel)
- Database → Same server as backend
- Bot Core → VPS with MT5 installed

### Option 3: Docker Containers
Each module in its own container:
- `backend:latest`
- `frontend:latest`
- `bot-core:latest`

## ✅ Benefits

✅ **Separation of Concerns** - Each module has one job
✅ **Easy to Understand** - Clear boundaries
✅ **Flexible Deployment** - Deploy anywhere
✅ **Parallel Development** - Teams work independently
✅ **Easier Testing** - Test modules in isolation
✅ **Better Security** - Isolate sensitive components
