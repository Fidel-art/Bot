import React, { useState } from 'react';
import { configAPI, botAPI, systemAPI } from '../services/api';
import './RiskManagement.css';

function RiskManagement({ onComplete }) {
  const [loading, setLoading] = useState(false);
  const [riskSettings, setRiskSettings] = useState({
    lot_size: 0.01,
    risk_per_trade: 1.0,
    max_drawdown: 5.0,
    max_trades_per_day: 3,
    stop_loss_pips: 50,
    take_profit_pips: 100
  });

  const riskProfiles = {
    conservative: {
      label: '🛡️ Conservative',
      lot_size: 0.01,
      risk_per_trade: 0.5,
      max_drawdown: 3.0,
      max_trades_per_day: 2,
      stop_loss_pips: 30,
      take_profit_pips: 60
    },
    moderate: {
      label: '⚖️ Moderate',
      lot_size: 0.01,
      risk_per_trade: 1.0,
      max_drawdown: 5.0,
      max_trades_per_day: 3,
      stop_loss_pips: 50,
      take_profit_pips: 100
    },
    aggressive: {
      label: '🚀 Aggressive',
      lot_size: 0.02,
      risk_per_trade: 2.0,
      max_drawdown: 10.0,
      max_trades_per_day: 5,
      stop_loss_pips: 80,
      take_profit_pips: 160
    }
  };

  const handleProfileSelect = (profile) => {
    setRiskSettings(riskProfiles[profile]);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setRiskSettings(prev => ({
      ...prev,
      [name]: parseFloat(value)
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    setLoading(true);
    try {
      // Step 1: Get existing config and merge with risk settings
      console.log('Fetching existing config...');
      
      const configRes = await configAPI.getConfig();
      console.log('Config response:', configRes.data);
      
      if (!configRes.data.has_config) {
        alert('❌ MT5 configuration not found!\n\nPlease complete the MT5 setup step first.');
        if (onComplete) {
          onComplete();
        }
        setLoading(false);
        return;
      }
      
      const existingConfig = configRes.data.config;

      // Merge risk settings with existing config
      const updatedConfig = {
        mt5_login: existingConfig.mt5_login,
        mt5_server: existingConfig.mt5_server,
        mt5_password: existingConfig.mt5_password || 'password123', // Placeholder if not stored
        symbols: existingConfig.symbols || ['XAUUSD'],
        timeframes: existingConfig.timeframes || ['D1', 'H4', 'H1', 'M15'],
        ...riskSettings
      };

      console.log('Saving config:', updatedConfig);
      
      // Step 2: Save risk settings
      await configAPI.saveConfig(updatedConfig);
      console.log('Config saved successfully');
      
      // Step 3: Check MT5 status
      console.log('Checking MT5 status...');
      const mt5StatusRes = await systemAPI.getMT5Status();
      const mt5Status = mt5StatusRes.data;
      console.log('MT5 Status:', mt5Status);
      
      if (!mt5Status.mt5_found) {
        alert('❌ MetaTrader 5 not found on your system.\n\nPlease install MT5 from: https://www.metatrader5.com/\n\nSettings have been saved.');
        if (onComplete) {
          onComplete();
        }
        return;
      }
      
      // Step 4: Confirm to launch MT5 and start bot
      const startTrading = window.confirm(
        '✅ Risk Management Settings Saved!\n\n' +
        '🚀 Ready to Start Trading?\n\n' +
        'The system will:\n' +
        `• ${mt5Status.is_running ? 'Connect to' : 'Launch'} MetaTrader 5\n` +
        '• Apply your risk management rules\n' +
        '• Start monitoring for trade opportunities\n' +
        '• Execute trades automatically\n\n' +
        'Click OK to start trading now, or Cancel to start manually later.'
      );
      
      if (startTrading) {
        try {
          // Step 5: Launch MT5 if not running
          if (!mt5Status.is_running) {
            alert('⏳ Launching MetaTrader 5...\n\nPlease wait a moment.');
            console.log('Launching MT5...');
            
            try {
              await systemAPI.launchMT5();
              console.log('MT5 launch request sent');
              // Wait for MT5 to fully initialize
              await new Promise(resolve => setTimeout(resolve, 5000));
            } catch (launchErr) {
              console.error('MT5 launch error:', launchErr);
              throw new Error('Failed to launch MT5. Please open MetaTrader 5 manually and try again from the dashboard.');
            }
          }
          
          // Step 6: Start the bot
          alert('⏳ Starting trading bot and connecting to MT5...\n\nThis may take a few seconds.');
          console.log('Starting bot...');
          
          await botAPI.startBot();
          console.log('Bot started successfully');
          
          alert(
            '✅ Success! Trading bot is now active!\n\n' +
            '📊 MT5 is connected\n' +
            '⚙️ Risk settings applied\n' +
            '🎯 Bot is monitoring markets\n\n' +
            'Redirecting to dashboard...'
          );
          
          // Wait a moment before redirecting
          setTimeout(() => {
            if (onComplete) {
              onComplete();
            }
          }, 2000);
          
        } catch (startErr) {
          const errorMsg = startErr.response?.data?.detail || startErr.message || String(startErr);
          console.error('Bot start error:', startErr);
          alert(
            `⚠️ Settings saved, but bot start failed:\n\n${errorMsg}\n\n` +
            'Possible issues:\n' +
            '• MT5 credentials incorrect\n' +
            '• No active subscription\n' +
            '• MT5 not responding\n\n' +
            'You can start the bot manually from the dashboard.'
          );
          
          if (onComplete) {
            onComplete();
          }
        }
      } else {
        // User chose not to start bot
        alert('✅ Settings saved successfully!\n\nYou can start the bot from the dashboard when ready.');
        if (onComplete) {
          onComplete();
        }
      }
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || JSON.stringify(err) || 'Failed to save settings';
      console.error('Risk settings error:', err);
      alert(`❌ Error: ${errorMessage}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="risk-container">
      <div className="risk-card">
        <h1>⚙️ Risk Management Settings</h1>
        <p className="subtitle">Configure your trading risk parameters</p>

        <div className="profile-selector">
          <h3>Quick Profiles</h3>
          <div className="profile-buttons">
            {Object.entries(riskProfiles).map(([key, profile]) => (
              <button
                key={key}
                className="profile-btn"
                onClick={() => handleProfileSelect(key)}
              >
                {profile.label}
              </button>
            ))}
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <div className="settings-grid">
            <div className="setting-group">
              <label>
                <span className="label-icon">💰</span>
                Lot Size
              </label>
              <input
                type="number"
                name="lot_size"
                value={riskSettings.lot_size}
                onChange={handleInputChange}
                step="0.01"
                min="0.01"
                max="100"
              />
              <span className="help">Standard trading volume per position</span>
            </div>

            <div className="setting-group">
              <label>
                <span className="label-icon">📊</span>
                Risk Per Trade (%)
              </label>
              <input
                type="number"
                name="risk_per_trade"
                value={riskSettings.risk_per_trade}
                onChange={handleInputChange}
                step="0.1"
                min="0.1"
                max="10"
              />
              <span className="help">Percentage of balance to risk per trade</span>
            </div>

            <div className="setting-group">
              <label>
                <span className="label-icon">🛑</span>
                Max Drawdown (%)
              </label>
              <input
                type="number"
                name="max_drawdown"
                value={riskSettings.max_drawdown}
                onChange={handleInputChange}
                step="0.5"
                min="1"
                max="50"
              />
              <span className="help">Bot stops if drawdown exceeds this</span>
            </div>

            <div className="setting-group">
              <label>
                <span className="label-icon">📈</span>
                Max Trades Per Day
              </label>
              <input
                type="number"
                name="max_trades_per_day"
                value={riskSettings.max_trades_per_day}
                onChange={handleInputChange}
                min="1"
                max="50"
              />
              <span className="help">Maximum number of trades per day</span>
            </div>

            <div className="setting-group">
              <label>
                <span className="label-icon">🔻</span>
                Stop Loss (Pips)
              </label>
              <input
                type="number"
                name="stop_loss_pips"
                value={riskSettings.stop_loss_pips}
                onChange={handleInputChange}
                min="10"
                max="500"
              />
              <span className="help">Default stop loss distance</span>
            </div>

            <div className="setting-group">
              <label>
                <span className="label-icon">🎯</span>
                Take Profit (Pips)
              </label>
              <input
                type="number"
                name="take_profit_pips"
                value={riskSettings.take_profit_pips}
                onChange={handleInputChange}
                min="10"
                max="1000"
              />
              <span className="help">Default take profit distance</span>
            </div>
          </div>

          <div className="risk-summary">
            <h4>📋 Summary</h4>
            <div className="summary-grid">
              <div>Risk/Reward Ratio: <strong>{(riskSettings.take_profit_pips / riskSettings.stop_loss_pips).toFixed(2)}:1</strong></div>
              <div>Daily Risk Cap: <strong>{(riskSettings.risk_per_trade * riskSettings.max_trades_per_day).toFixed(1)}%</strong></div>
              <div>Protection Level: <strong>{riskSettings.max_drawdown}% Max DD</strong></div>
            </div>
          </div>

          <button type="submit" className="save-btn" disabled={loading}>
            {loading ? '⏳ Saving & Starting...' : '✅ Save & Start Trading'}
          </button>
        </form>

        <div className="warning-box">
          <p>⚠️ <strong>Important:</strong> Start with conservative settings if you're new to automated trading.</p>
        </div>
      </div>
    </div>
  );
}

export default RiskManagement;
