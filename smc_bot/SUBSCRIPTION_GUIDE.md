# Subscription System Guide

## Overview

The SMC Trading Bot now includes a comprehensive subscription system. Traders must have an active subscription to use the bot for trading.

---

## 📋 Subscription Plans

### Available Plans:

| Plan | Duration | Price | Best For |
|------|----------|-------|----------|
| **Free Trial** | 3 Days | FREE | Testing the bot |
| **Weekly** | 7 Days | $29 | Short-term trading |
| **Monthly** | 30 Days | $99 | Most popular choice |
| **Quarterly** | 90 Days | $249 | 3-month commitment |
| **Yearly** | 365 Days | $799 | Maximum savings |
| **Lifetime** | Forever | $2,499 | One-time payment |

---

## 🚀 How to Subscribe

### Method 1: First-Time Setup

When you run the bot for the first time without a subscription:

```bash
python main.py
```

1. **Select or create your profile**
2. **Bot detects no subscription**
3. **Subscription menu appears:**
   ```
   ❌ No subscription found. Please subscribe to use the bot.

   SUBSCRIPTION REQUIRED
   [1] Subscribe Now
   [2] View Subscription Status
   [3] I have a license key
   [4] Renew Subscription
   [0] Exit
   ```

4. **Choose [1] Subscribe Now**
5. **Select your plan:**
   ```
   [1] 3-Day Free Trial
   [2] Weekly Plan - $29
   [3] Monthly Plan - $99
   [4] Quarterly Plan - $249
   [5] Yearly Plan - $799
   [6] Lifetime Access - $2499
   ```

6. **For Free Trial:** Activates immediately
7. **For Paid Plans:** Choose payment option:
   - `[1] I have a license key` - Enter your key
   - `[2] Generate demo key` - For testing purposes

### Method 2: From Main Menu

After logging in with a valid subscription:

```
MENU OPTIONS
[1] Start Trading Bot
[2] View Trade History & Statistics
[3] View Subscription Status          ← Check your subscription
[4] Manage Subscription                ← Renew or change plan
[5] Exit
```

---

## 🔑 License Keys

### What is a License Key?

A license key is a unique code that activates your subscription:
- Format: `XXXX-XXXX-XXXX-XXXX`
- Example: `A7F3-9B2C-E4D1-8F6A`
- Each key is unique and linked to your trader profile

### Using a License Key

If you have a purchased license key:

1. Run the bot: `python main.py`
2. Select `[3] I have a license key`
3. Choose your plan type
4. Enter your license key
5. Activation confirmed!

### Demo Mode (Testing)

For testing purposes, you can generate a demo key:
- Select `[2] Generate demo key`
- System creates temporary license key
- **Note:** In production, integrate real payment processing

---

## 📊 Subscription Status

### Viewing Your Subscription

From the main menu, select `[3] View Subscription Status`:

```
================================================================================
║                           SUBSCRIPTION STATUS                              ║
================================================================================

   ✅ Status: ACTIVE
   Plan: MONTHLY
   Price: $99
   License: A7F3-9B2C-E4D1-8F6A
   Activated: 2026-01-15 10:30
   Expires: 2026-02-15 10:30
   Days Remaining: 17

   Subscription active until 2026-02-15 10:30
================================================================================
```

### Status Indicators:

- ✅ **ACTIVE** (Green) - Subscription is valid
- ⚠️ **EXPIRING SOON** (Yellow) - Less than 7 days remaining
- ❌ **EXPIRED** (Red) - Subscription has ended

---

## 🔄 Renewing Your Subscription

### Auto-Extension on Renewal

When you renew before expiration:
- New period **starts from your expiration date**
- No time lost!
- Example:
  - Current expiration: Feb 15
  - Renew Monthly on Feb 10
  - New expiration: Mar 15 (not Mar 10)

### How to Renew:

1. From main menu: `[4] Manage Subscription`
2. Choose `[2] Renew Subscription`
3. Select your new plan
4. Enter license key or generate demo key
5. Confirmation displayed

---

## 🛡️ Subscription Validation

### When is Subscription Checked?

1. **At Startup:** When you select a profile
2. **Before Trading:** When you select "Start Trading Bot"
3. **During Trading:** Subscription info shown in dashboard

### Expiration Warnings

The bot provides advance warnings:

**Dashboard Display:**
```
║  ⏰ Subscription: MONTHLY - 5 days remaining  ║
```

**Color Codes:**
- **Green (✅):** More than 7 days remaining
- **Yellow (⏰):** 4-7 days remaining
- **Red (⚠️):** 1-3 days remaining

### When Subscription Expires:

If your subscription expires:
1. Trading is **blocked**
2. You'll see: `❌ Subscription expired. Please renew.`
3. Must renew to continue trading
4. Historical data and statistics remain accessible

---

## 💡 Subscription Management

### Change Plan

Want to upgrade or downgrade?

1. Main menu → `[4] Manage Subscription`
2. Choose `[3] Change Plan`
3. Select new plan
4. New expiration calculated from current expiration

### Multiple Profiles

Each trader profile has its own subscription:

```
Profile 1: john
  ✅ Monthly subscription (20 days left)

Profile 2: sarah  
  ❌ No subscription

Profile 3: demo_trader
  ✅ Trial subscription (2 days left)
```

### Deactivation

Subscriptions automatically deactivate when:
- Expiration date is reached
- System can be manually deactivated (admin feature)

---

## 📝 Subscription Data Storage

### Where Subscriptions Are Stored

```
config/subscriptions.json
```

### Subscription Record Structure

```json
{
  "trader_id": {
    "trader_id": "demo_trader",
    "plan": "monthly",
    "license_key": "A7F3-9B2C-E4D1-8F6A",
    "activation_date": "2026-01-15T10:30:00",
    "expiration_date": "2026-02-15T10:30:00",
    "is_active": true,
    "price": "$99"
  }
}
```

---

## 🔒 Security Features

### License Key Generation

- Uses SHA-256 hashing
- Includes trader ID, plan, timestamp
- Random token for uniqueness
- Format: 16-character hexadecimal

### Validation Process

1. Check if subscription exists
2. Verify active status
3. Compare expiration date with current date
4. Return validation result

---

## 💰 Payment Integration (Production)

### Current Status: Demo Mode

The system currently operates in demo mode for testing.

### For Production Deployment:

Replace demo key generation with real payment processing:

1. **Payment Gateway Integration:**
   - Stripe
   - PayPal
   - Cryptocurrency
   - Bank transfer

2. **Workflow:**
   ```
   User selects plan
        ↓
   Payment gateway
        ↓
   Payment confirmed
        ↓
   License key generated
        ↓
   Email sent to user
        ↓
   User enters key
        ↓
   Subscription activated
   ```

3. **Modification Points:**

In `config/subscription.py`, update:

```python
elif payment_choice == "2":
    # Replace this with actual payment processing
    print("Redirecting to payment gateway...")
    payment_result = process_payment(selected_plan)
    
    if payment_result['success']:
        license_key = payment_result['license_key']
        return self.activate_subscription(trader_id, selected_plan, license_key)
    else:
        return False, "Payment failed"
```

---

## 🎯 Best Practices

### For Users:

1. **Start with Trial:** Test all features free for 3 days
2. **Renew Early:** Avoid trading interruptions
3. **Save License Key:** Keep it safe for future reference
4. **Monitor Expiration:** Check dashboard regularly

### For Administrators:

1. **Secure subscriptions.json:** Protect subscription database
2. **Regular Backups:** Backup subscription data
3. **Monitor Expirations:** Track renewal rates
4. **Customer Support:** Help users with subscription issues

---

## 📧 Support & Troubleshooting

### Common Issues:

**1. "No subscription found"**
- Solution: Subscribe using the subscription menu

**2. "Subscription expired"**
- Solution: Renew your subscription

**3. "Invalid license key"**
- Solution: Check key format (XXXX-XXXX-XXXX-XXXX)
- Contact support for new key

**4. Subscription not loading**
- Check: `config/subscriptions.json` exists
- Verify: JSON file format is valid
- Review: `logs/trading_bot.log` for errors

### Getting Help:

1. Check subscription status first
2. Review log files
3. Contact support with:
   - Trader ID
   - License key
   - Error messages
   - Screenshot of issue

---

## 🚀 Quick Reference

### Subscribe:
```bash
python main.py → [1] Subscribe Now
```

### View Status:
```bash
python main.py → [3] View Subscription Status
```

### Renew:
```bash
python main.py → [4] Manage Subscription → [2] Renew
```

### Activate Key:
```bash
python main.py → [3] I have a license key → Enter key
```

---

## 📊 Subscription Lifecycle

```
Create Profile
     ↓
No Subscription → Subscribe → Active → Expires → Renew
                     ↓                    ↓
                  Free Trial          Inactive
                     ↓
                  Upgrade
                     ↓
                Paid Plan
```

---

This subscription system ensures only authorized users can trade with the bot while providing flexible plans to suit different trading needs and budgets!
