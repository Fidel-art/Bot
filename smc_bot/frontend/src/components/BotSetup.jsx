import React, { useState } from 'react';
import { configAPI } from '../services/api';
import './BotSetup.css';

function BotSetup({ onComplete }) {
  const [loading, setLoading] = useState(false);
  const [formData, setFormData] = useState({
    mt5_login: '',
    mt5_server: '',
    mt5_password: '',
    symbols: ['XAUUSD'],
    timeframes: ['D1', 'H4', 'H1', 'M15']
  });

  const availableSymbols = [
    'XAUUSD', 'EURUSD', 'GBPUSD', 'USDJPY', 'AUDUSD', 
    'USDCAD', 'NZDUSD', 'USDCHF', 'BTCUSD', 'ETHUSD'
  ];

  const availableTimeframes = ['M1', 'M5', 'M15', 'M30', 'H1', 'H4', 'D1', 'W1'];

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSymbolToggle = (symbol) => {
    setFormData(prev => ({
      ...prev,
      symbols: prev.symbols.includes(symbol)
        ? prev.symbols.filter(s => s !== symbol)
        : [...prev.symbols, symbol]
    }));
  };

  const handleTimeframeToggle = (timeframe) => {
    setFormData(prev => ({
      ...prev,
      timeframes: prev.timeframes.includes(timeframe)
        ? prev.timeframes.filter(t => t !== timeframe)
        : [...prev.timeframes, timeframe]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.mt5_login || !formData.mt5_server || !formData.mt5_password) {
      alert('❌ Please fill in all MT5 credentials');
      return;
    }

    if (formData.symbols.length === 0) {
      alert('❌ Please select at least one symbol');
      return;
    }

    if (formData.timeframes.length === 0) {
      alert('❌ Please select at least one timeframe');
      return;
    }

    setLoading(true);
    try {
      const config = {
        mt5_login: parseInt(formData.mt5_login),
        mt5_server: formData.mt5_server,
        mt5_password: formData.mt5_password,
        lot_size: 0.01,
        risk_per_trade: 1.0,
        max_drawdown: 5.0,
        max_trades_per_day: 3,
        symbols: formData.symbols,
        timeframes: formData.timeframes
      };

      await configAPI.saveConfig(config);
      alert('✅ MT5 connection configured successfully!');
      
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      alert(`❌ Error: ${err.response?.data?.detail || 'Failed to save configuration'}`);
      console.error('Config error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="setup-container">
      <div className="setup-card">
        <h1>🔌 Connect Your MT5 Account</h1>
        <p className="subtitle">Enter your MetaTrader 5 credentials to start trading</p>

        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>MT5 Login Number *</label>
            <input
              type="number"
              name="mt5_login"
              value={formData.mt5_login}
              onChange={handleInputChange}
              placeholder="e.g., 454173"
              required
            />
          </div>

          <div className="form-group">
            <label>MT5 Server *</label>
            <input
              type="text"
              name="mt5_server"
              value={formData.mt5_server}
              onChange={handleInputChange}
              placeholder="e.g., FxPesa-Demo"
              required
            />
          </div>

          <div className="form-group">
            <label>MT5 Password *</label>
            <input
              type="password"
              name="mt5_password"
              value={formData.mt5_password}
              onChange={handleInputChange}
              placeholder="Enter your MT5 password"
              required
            />
          </div>

          <div className="form-group">
            <label>Trading Symbols</label>
            <div className="chip-container">
              {availableSymbols.map(symbol => (
                <div
                  key={symbol}
                  className={`chip ${formData.symbols.includes(symbol) ? 'active' : ''}`}
                  onClick={() => handleSymbolToggle(symbol)}
                >
                  {symbol}
                </div>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label>Timeframes</label>
            <div className="chip-container">
              {availableTimeframes.map(tf => (
                <div
                  key={tf}
                  className={`chip ${formData.timeframes.includes(tf) ? 'active' : ''}`}
                  onClick={() => handleTimeframeToggle(tf)}
                >
                  {tf}
                </div>
              ))}
            </div>
          </div>

          <button type="submit" className="submit-btn" disabled={loading}>
            {loading ? '⏳ Connecting...' : '✅ Connect MT5 Account'}
          </button>
        </form>

        <div className="help-text">
          <p>💡 <strong>Need help?</strong></p>
          <p>• Your MT5 credentials are encrypted and secure</p>
          <p>• Make sure your MT5 terminal is running</p>
          <p>• Use a demo account first to test the bot</p>
        </div>
      </div>
    </div>
  );
}

export default BotSetup;
