# SMC Trading Bot - Web Dashboard

Professional web-based dashboard for managing and monitoring your SMC/ICT trading bot.

## 🎯 Features

### Authentication & Security
- ✅ JWT-based authentication
- ✅ Secure password hashing (bcrypt)
- ✅ Token refresh mechanism
- ✅ Session management

### Trader Management
- ✅ Multi-trader support
- ✅ Individual profiles and configurations
- ✅ Separate trade history per trader
- ✅ Custom risk settings per account

### Subscription System
- ✅ Free trial (7 days)
- ✅ Monthly subscription
- ✅ Quarterly subscription
- ✅ VIP subscription (annual)
- ✅ Automatic expiry tracking

### Bot Control
- ✅ Start/Stop bot
- ✅ Pause/Resume trading
- ✅ Real-time status monitoring
- ✅ System health metrics

### Trading Analytics
- ✅ Trade history
- ✅ Performance statistics
- ✅ Win rate and profit factor
- ✅ Real-time P/L tracking

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MetaTrader 5

### Backend Setup

1. **Install Python dependencies:**
```powershell
cd dashboard/backend
pip install -r requirements.txt
```

Or install all dependencies at once:
```powershell
pip install -r requirements.txt
```

2. **Run the backend server:**
```powershell
cd dashboard/backend
python -m uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at: `http://localhost:8000`

API documentation at: `http://localhost:8000/docs`

### Frontend Setup

1. **Install Node dependencies:**
```powershell
cd dashboard/frontend
npm install
```

2. **Run the development server:**
```powershell
npm run dev
```

The dashboard will be available at: `http://localhost:3000`

## 📁 Project Structure

```
dashboard/
├── backend/                  # FastAPI backend
│   ├── api.py               # Main API endpoints
│   ├── auth.py              # Authentication & JWT
│   ├── bot_controller.py    # Bot lifecycle management
│   ├── db.py                # Database operations
│   └── requirements.txt     # Python dependencies
│
├── frontend/                # React frontend
│   ├── src/
│   │   ├── components/      # React components
│   │   │   ├── Login.jsx
│   │   │   ├── Register.jsx
│   │   │   ├── Dashboard.jsx
│   │   │   ├── RiskSettings.jsx
│   │   │   ├── Subscription.jsx
│   │   │   └── TradeHistory.jsx
│   │   ├── services/        # API client
│   │   │   └── api.js
│   │   ├── App.jsx          # Main app component
│   │   └── main.jsx         # Entry point
│   ├── package.json
│   └── vite.config.js
│
├── enhanced_dashboard.py    # Enhanced terminal dashboard
├── dashboard.py             # Original terminal dashboard
└── trade_analyzer.py        # Trade analytics
```

## 🔐 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new account
- `POST /api/auth/login` - Login
- `POST /api/auth/logout` - Logout
- `POST /api/auth/refresh` - Refresh access token

### Profile
- `GET /api/profile` - Get trader profile

### Subscription
- `GET /api/subscription` - Get active subscription
- `POST /api/subscription/create` - Create new subscription

### Bot Control
- `POST /api/bot/start` - Start trading bot
- `POST /api/bot/stop` - Stop trading bot
- `POST /api/bot/pause` - Pause bot
- `POST /api/bot/resume` - Resume bot
- `GET /api/bot/status` - Get bot status

### Configuration
- `GET /api/config` - Get bot configuration
- `POST /api/config/save` - Save bot configuration

### Trading Data
- `GET /api/trades/history` - Get trade history
- `GET /api/trades/statistics` - Get performance stats

### System
- `GET /api/system/health` - System health check

## 💡 Usage Examples

### Registration
```javascript
POST /api/auth/register
{
  "trader_id": "trader1",
  "email": "trader@example.com",
  "password": "securepassword",
  "name": "John Doe"
}
```

### Start Bot
```javascript
POST /api/bot/start
Headers: { Authorization: "Bearer <token>" }
{
  "mt5_login": 123456,
  "mt5_server": "FxPesa-Demo",
  "mt5_password": "password",
  "lot_size": 0.02,
  "risk_per_trade": 2.0,
  "max_drawdown": 5.0,
  "max_trades_per_day": 3,
  "symbols": ["XAUUSD"],
  "timeframes": ["D1", "H4", "H1", "M15"]
}
```

## 🎨 Enhanced Terminal Dashboard

The enhanced terminal dashboard provides:
- 📊 Live price updates every 5 seconds
- 📈 ASCII price charts
- 🎯 Signal confidence meters
- 💰 Today's performance summary
- ⏱️ Recent execution timeline
- 🔧 System health monitoring
- 🔥 Win/loss streak tracking

To use the enhanced dashboard:
```python
from dashboard.enhanced_dashboard import get_enhanced_dashboard

dashboard = get_enhanced_dashboard()
dashboard.display_full_enhanced(data)
```

## 🗄️ Database Schema

The system uses SQLite with the following tables:
- `traders` - Trader accounts
- `subscriptions` - Subscription plans and status
- `bot_configs` - Bot configurations per trader
- `trades` - Trade history
- `bot_sessions` - Bot run sessions

## 🔒 Security Features

- Passwords hashed with bcrypt
- JWT tokens with expiration
- Token refresh mechanism
- Token blacklisting on logout
- Authorization middleware
- CORS protection (configurable)

## 🌐 Deployment

### Production Backend
```powershell
uvicorn dashboard.backend.api:app --host 0.0.0.0 --port 8000 --workers 4
```

### Production Frontend
```powershell
cd dashboard/frontend
npm run build
```

Deploy the `dist` folder to your web server.

### Environment Variables
Create `.env` file:
```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///data/bot_dashboard.db
API_URL=http://your-domain.com
```

## 📊 Subscription Plans

| Plan | Duration | Price | Features |
|------|----------|-------|----------|
| Free Trial | 7 days | $0 | All features |
| Monthly | 30 days | $50 | Full access |
| Quarterly | 90 days | $135 | Save 10% |
| VIP | 365 days | $500 | Save 17% |

## 🐛 Troubleshooting

**Backend won't start:**
- Ensure all dependencies installed: `pip install -r requirements.txt`
- Check port 8000 is available

**Frontend won't start:**
- Install dependencies: `npm install`
- Check port 3000 is available
- Clear npm cache: `npm cache clean --force`

**API connection errors:**
- Check backend is running on port 8000
- Verify CORS settings in api.py
- Check firewall settings

## 📝 TODO / Future Enhancements

- [ ] WebSocket for real-time updates
- [ ] Email notifications
- [ ] Telegram bot integration
- [ ] Multi-symbol support expansion
- [ ] Advanced charting with TradingView
- [ ] Mobile app (React Native)
- [ ] Payment gateway integration
- [ ] Admin panel
- [ ] Performance analytics dashboard
- [ ] Risk heat maps

## 👥 Contributing

This is a private trading bot. For issues or feature requests, contact the development team.

## 📄 License

Proprietary - All rights reserved

---

**Built with:**
- FastAPI (Python)
- React + Vite
- SQLite
- JWT Authentication
- MetaTrader 5 API
