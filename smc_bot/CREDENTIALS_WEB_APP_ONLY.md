# Credentials Setup - Web App Only (No Terminal Input)

## ✅ Updated Workflow

Your trading system has been updated so that **ALL credentials are entered through the web app**, not the terminal.

### The New Flow:

```
🌐 Browser (localhost:3000)
    ↓
1. Login/Register
    ↓
2. Select Subscription Plan (free trial or paid)
    ↓
3. Go to "Bot Setup" 
    ↓
4. Enter MT5 Credentials:
   - MT5 Login Number
   - MT5 Server
   - MT5 Password
    ↓
5. Click "Save Configuration"
    ↓
6. Configure Risk Management
    ↓
7. View Dashboard with live trading
```

---

## 📝 Step-by-Step Instructions

### Step 1: Start The System

Run the bot (credentials will NOT be prompted):

```bash
cd c:\Users\FidelSomba\OneDrive\Desktop\BOT code\smc_bot
python main.py
```

**Expected output in terminal:**
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

### Step 2: Open Web Dashboard

In your browser, go to: **http://localhost:3000**

### Step 3: Login / Register

```
📧 Email: your.email@example.com
🔑 Password: your.password
```

→ Click **Login** or go to **Register** if new user

### Step 4: Select Subscription

Choose your plan:
- **Free Trial** - 7 days free
- **Weekly** - $15
- **Monthly** - $50 (popular)
- **Quarterly** - $135
- **Yearly** - $500 (best value)

→ Click **Subscribe**

### Step 5: Bot Setup (Enter MT5 Credentials HERE)

You'll see the **"Connect Your MT5 Account"** form:

| Field | Example | Where to Find |
|-------|---------|---------------|
| **MT5 Login Number** | `454173` | MT5 Account Manager |
| **MT5 Server** | `FxPesa-Demo` | MT5 Login Box |
| **MT5 Password** | `••••••••` | Your MT5 password |
| **Symbols** | XAUUSD selected | Choose which assets to trade |
| **Timeframes** | D1, H4, H1, M15 | Choose candle periods |

→ Click **Save Configuration**

✅ **Your credentials are now saved!**

### Step 6: Configure Risk Management

Set your risk parameters:
- Lot Size
- Max Drawdown %
- Risk Per Trade %
- Max Trades Per Day

→ Click **Start Trading Bot**

### Step 7: Monitor Dashboard

You'll see:
- 📊 Real-time positions
- 💰 Account balance & equity
- 📈 Trade history
- 🎯 Strategy signals (OB/FVG/BOS)

---

## ⚠️ Important Notes

### The Terminal Window
- **DO NOT CLOSE IT** - It runs the bot in the background
- Message shows: "⏳ Waiting for credentials from web app..."
- Once you save credentials, it automatically starts trading
- Will show: "✅ Configuration received from web app!"

### Credentials Are Stored
- **Web app:** Saves encrypted in database
- **Bot file:** Saved to `config/bot_config.json` when you click Save
- **Password:** Stored in `config/trader_configs/secrets.json`
- **NOT in terminal prompts** ❌ (Old way - no longer used)

### Security
- Passwords are NEVER shown in terminal
- NEVER typed in console/terminal
- Only entered in secure web form
- Stored encrypted in database

---

## 🔧 If Something Goes Wrong

### "Waiting for configuration..." stays forever
**Solution:** 
1. Check browser at http://localhost:3000
2. Make sure you completed Bot Setup
3. Verify "Save Configuration" was clicked (you should see ✅ popup)
4. Check for any error messages in web app

### Bot doesn't start after saving credentials
**Solution:**
1. Keep terminal window open
2. Wait 5-10 seconds
3. Should see: "✅ Configuration received from web app!"
4. Then: "🚀 Starting bot for trader..."

### "No configuration found" error
**Solution:**
1. Delete `config/bot_config.json` if it exists
2. Go back to web app Bot Setup
3. Re-enter all credentials
4. Click Save again

### Can't see Web Dashboard at localhost:3000
**Solution:**
1. Run: `cd smc_bot && start_dashboard.bat`
2. Wait 10 seconds for startup
3. Try: http://localhost:3000
4. Check for error messages

---

## 📋 Checklist on First Launch

- [ ] Terminal window running `python main.py`
- [ ] Browser open to http://localhost:3000
- [ ] Logged in to web app
- [ ] Subscription plan selected
- [ ] Completed Bot Setup with MT5 credentials
- [ ] Clicked "Save Configuration"
- [ ] Saw ✅ success message
- [ ] Terminal shows "✅ Configuration received"
- [ ] Dashboard loads with account info

---

## 🎯 Key Differences From Before

| Before | Now |
|--------|-----|
| ❌ Credentials in terminal prompts | ✅ Credentials in web form only |
| ❌ Terminal asks questions | ✅ Terminal just waits silently |
| ❌ Manual profile selection | ✅ Auto-load from web config |
| ❌ Can be seen in history | ✅ Never visible in terminal |
| ❌ Hard to change | ✅ Easy to update in web app |

---

## 📞 Need to Change Credentials Later?

1. Go to http://localhost:3000/bot-setup
2. Enter new MT5 credentials
3. Click Save
4. System uses new credentials on next analysis cycle

No need to restart the bot!

---

**That's it! 🚀 Your credentials are now safely entered through the secure web app interface!**
