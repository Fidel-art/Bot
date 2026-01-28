# SMC Trading Bot - Dashboard Structure

The dashboard is organized into three main modules:

## 📁 Structure

```
dashboard/
├── backend/              # FastAPI Backend Server
│   ├── __init__.py
│   ├── api.py           # REST API endpoints
│   ├── auth.py          # Authentication & JWT
│   ├── bot_controller.py # Bot lifecycle management
│   └── requirements.txt
│
├── frontend/            # React Frontend Application
│   ├── src/
│   │   ├── components/  # React components
│   │   ├── services/    # API client
│   │   ├── App.jsx
│   │   └── main.jsx
│   ├── package.json
│   └── vite.config.js
│
├── database/            # Database Layer
│   ├── __init__.py
│   └── db.py           # SQLite database manager
│
├── enhanced_dashboard.py # Enhanced terminal UI
├── dashboard.py         # Original terminal UI
├── trade_analyzer.py    # Trade analytics
└── README.md
```

## 🔧 Backend (API Server)
- **Location**: `dashboard/backend/`
- **Tech**: FastAPI, Python
- **Purpose**: REST API for bot management, authentication, and data access
- **Port**: 8000

## 💻 Frontend (User Interface)
- **Location**: `dashboard/frontend/`
- **Tech**: React, Vite, Axios
- **Purpose**: Web-based dashboard for traders
- **Port**: 3000

## 🗄️ Database (Data Persistence)
- **Location**: `dashboard/database/`
- **Tech**: SQLite, Python
- **Purpose**: Store traders, subscriptions, configs, trades, and sessions
- **File**: `data/bot_dashboard.db` (auto-created)

## 🚀 How They Work Together

```
Frontend (React)
    ↓ HTTP/REST
Backend (FastAPI)
    ↓ Python
Database (SQLite)
    ↓ SQL
Persistent Storage
```

Each layer is independent and can be developed/tested separately!
