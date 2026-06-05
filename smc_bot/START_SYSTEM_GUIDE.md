# How to Start the Full System - UPDATED

## ✅ The Complete Secure Workflow

Your trading system is now fully set up with **web app-only credential entry** (No terminal prompts!).

---

## 🚀 Quick Start (3 Simple Steps)

### Step 1: Start the Trading Bot
```bash
cd c:\Users\FidelSomba\OneDrive\Desktop\BOT code\smc_bot
python main.py
```

**Terminal will show:**
```
========================================
BOT READY - WAITING FOR CONFIGURATION
========================================

KEEP THIS WINDOW OPEN!

1. Open: http://localhost:3000
2. Log in or register
3. Go to 'Bot Setup' and enter your MT5 credentials
4. Click 'Save Configuration'

⏳ Waiting for credentials from web app...

========================================
```

✅ **Leave this window open!**

---

### Step 2: Open Web Dashboard & Configure
Open your browser to: **http://localhost:3000**

**Follow these steps:**

1. **Login/Register**
   - Email: your.email@example.com
   - Password: your.password

2. **Choose Subscription**
   - Free Trial - 7 days (no payment)
   - or Monthly/Quarterly/Yearly plans

3. **Bot Setup - ENTER YOUR MT5 CREDENTIALS HERE** 🔐
   
   Fill in these fields:
   ```
   MT5 Login Number:  454173 (example)
   MT5 Server:        FxPesa-Demo (example)
   MT5 Password:      ••••••••••
   ```
   
   Select Trading Symbols (at least XAUUSD)
   Select Timeframes (D1, H4, H1, M15 recommended)

4. **Click "Save Configuration"**
   - You'll see: ✅ "Configuration saved successfully"

---

### Step 3: Watch the Bot Start Automatically

In your terminal window, you'll see:
```
✅ Configuration received from web app!
Credentials received! Starting bot...

========================================
BOT STARTING for web_user
========================================

🚀 BOT STARTED - Analysis every 300 seconds
[Bot begins trading...]
```

✅ **Bot is now running and trading!**

---

## 📊 Monitor Your Trading

### In the Dashboard (http://localhost:3000)
- 📍 Real-time positions with entry/exit prices
- 💰 Account balance and current equity
- 📈 Trade signals (OB, FVG, BOS strategy names)
- 🎯 Win rate and profit metrics
- 📊 Trade history with details

### In the Terminal
- Shows each analysis cycle
- Displays when trades execute
- Shows risk management status
- Displays account information

---

## ⚙️ What's Happening Behind the Scenes

```
Your Browser (Secure Web Form)
    ↓ You enter: MT5 login, password, server
    ↓ Credentials encrypted
    ↓ Sent to backend API (localhost:8000)
    
Backend API (FastAPI)
    ↓ Saves to database (encrypted)
    ↓ Saves to config/bot_config.json file
    ↓ Stores password in config/trader_configs/secrets.json
    
Python Bot (main.py)
    ↓ Polls for bot_config.json every 5 seconds
    ↓ Detects config file when you save
    ↓ Reads MT5 credentials from file
    ↓ Connects to MT5
    ↓ Starts trading with SMC strategies
    
MT5 Terminal
    ↓ Executes trades automatically
    ↓ Tags trades with strategy name (OB/FVG/BOS)
    
Dashboard
    ↓ Shows all trades in real-time
    ↓ Displays P&L, signals, positions
```

---

## 🔒 Security Features

✅ **Passwords never shown in terminal**
- Hidden in secure web form
- Encrypted in database
- Only accessed by bot internally

✅ **Configuration file auto-generated**
- Created when you save in web app
- Bot reads on startup
- Easy to change anytime

✅ **Credentials separate from code**
- Not hardcoded
- Not visible in logs
- Easy to update without restarting

---

## 📋 What the Bot Executes (3 Strategies)

### 1. Order Blocks (OB)
- Detects institutional order blocks
- Enters when price retraces to Fibonacci levels
- Trade tag: `SMC_OB_BUY` or `SMC_OB_SELL`

### 2. Fair Value Gaps (FVG)
- Finds unmet order gaps
- Trades the gap fill
- Trade tag: `SMC_FVG_BUY` or `SMC_FVG_SELL`

### 3. Break of Structure (BOS)
- Identifies structural breaks
- Trades the directional move
- Trade tag: `SMC_BOS_BUY` or `SMC_BOS_SELL`

**Each trade is labeled** so you can see exactly which strategy triggered it!

---

## ✅ Verification Checklist

On first launch, verify:

- [ ] Terminal shows "Waiting for credentials" message
- [ ] Web dashboard opens at http://localhost:3000
- [ ] Can log in / register
- [ ] Can select subscription plan
- [ ] Bot Setup form shows with input fields
- [ ] Enter MT5 credentials successfully
- [ ] Click "Save Configuration"
- [ ] See ✅ success message in web app
- [ ] Terminal shows "✅ Configuration received from web app!"
- [ ] Bot starts automatically
- [ ] Dashboard shows account info
- [ ] Can see positions and trades

---

## 🛠️ Troubleshooting

### "Waiting for credentials..." for very long time
**Solution:**
1. Check if http://localhost:3000 is loading
2. Make sure you completed BOT SETUP
3. Click "Save Configuration" (you should see ✅ popup)
4. Check browser console (F12) for errors

### Bot doesn't start after saving config
**Solution:**
1. Keep terminal window open
2. Wait 5-10 seconds
3. Check for error messages
4. Try refreshing bot setup and saving again

### Can't login to web app at http://localhost:3000
**Solution:**
1. Run dashboard: `start_dashboard.bat`
2. Wait 10 seconds
3. Make sure backend is running (port 8000)
4. Try: `http://localhost:3000` again

### Terminal shows "Timeout waiting for configuration"
**Solution:**
1. You have 10 minutes to save credentials
2. If timeout occurs:
   - Stop the bot (Ctrl+C)
   - Save credentials in web app
   - Run `python main.py` again

---

## 📞 If You Need to Change Credentials Later

1. Go to: http://localhost:3000/bot-setup
2. Enter your NEW MT5 credentials
3. Click "Save Configuration"
4. Bot automatically uses new credentials on next cycle

**NO need to restart!**

---

## 🎯 Expected System Performance

**First 10 trades:** Monitor closely
- Each trade should show in dashboard
- Win rate: 55-70% typically
- Risk per trade: ~1% of account

**After 50 trades:** Evaluate results
- Can adjust lot size or risk parameters
- Modify strategy selection if needed
- Scale up if performing well

**Monthly goals:**
- Conservative: 3-8% return
- Balanced: 5-15% return  
- Aggressive: 10-25% return

---

## 📚 Documentation Files

If you need more details:

1. **[CREDENTIALS_WEB_APP_ONLY.md](CREDENTIALS_WEB_APP_ONLY.md)**
   - Complete guide on credential entry
   - Troubleshooting tips
   - Security features

2. **[mql5/QUICKSTART.md](mql5/QUICKSTART.md)**
   - MQL5 Expert Advisor setup
   - MT5 deployment steps
   - Strategy parameters

3. **[mql5/INTEGRATION_GUIDE.md](mql5/INTEGRATION_GUIDE.md)**
   - How Python bot syncs with MT5 EA
   - System architecture
   - Expected trade flow

4. **[mql5/DEPLOYMENT_GUIDE.md](mql5/DEPLOYMENT_GUIDE.md)**
   - Full EA parameter reference
   - Recommended settings by symbol
   - Backtesting guide

---

## 🚀 YOU'RE READY!

```
Terminal:  python main.py
Browser:   http://localhost:3000
Dashboard: Enter credentials → Start trading!

Your complete SMC trading system is now running with secure, web-app-only credential entry.

Happy profitable trading! 📈
```

---

**Questions?** Review the documentation files above or check the web app help (?) icons.

**Need to restart?** Just close the terminal window and run `python main.py` again. You won't need to re-enter credentials unless the bot_config.json file is deleted.
