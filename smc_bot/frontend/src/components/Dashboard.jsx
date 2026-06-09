import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { botAPI, tradesAPI, profileAPI, subscriptionAPI, systemAPI } from '../services/api';
import BotSetup from './BotSetup';
import RiskManagement from './RiskManagement';
import SubscriptionPlans from './SubscriptionPlans';
import './Dashboard.css';

function Dashboard() {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [botStatus, setBotStatus] = useState(null);
  const [profile, setProfile] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [trades, setTrades] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [error, setError] = useState(null);
  const [mt5Status, setMt5Status] = useState(null);
  const [activeTab, setActiveTab] = useState('dashboard');
  const [instantTrade, setInstantTrade] = useState({
    symbol: 'XAUUSD',
    risk_per_trade: 1.0,
  });
  const [instantTradeLoading, setInstantTradeLoading] = useState(false);

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData();
    const interval = setInterval(() => {
      if (!instantTradeLoading) {
        fetchDashboardData();
      }
    }, 10000);
    return () => clearInterval(interval);
  }, [instantTradeLoading]);

  const fetchDashboardData = async (force = false) => {
    if (instantTradeLoading && !force) {
      return;
    }

    try {
      // Fetch critical data first
      const [statusResult, profileResult, mt5Result] = await Promise.allSettled([
        botAPI.getStatus().catch(e => ({ data: null })),
        profileAPI.getProfile().catch(e => ({ data: null })),
        systemAPI.getMT5Status().catch(e => ({ data: null }))
      ]);

      // Safely update state
      if (statusResult.status === 'fulfilled' && statusResult.value?.data) {
        const statusData = statusResult.value.data;
        console.log('Bot Status Data:', statusData);
        // Extract just the status string if it's nested
        const actualStatus = typeof statusData.status === 'string' 
          ? statusData.status 
          : statusData.status?.status || 'stopped';
        setBotStatus({ ...statusData, status: actualStatus });
      }
      if (profileResult.status === 'fulfilled' && profileResult.value?.data) {
        setProfile(profileResult.value.data);
      }
      if (mt5Result.status === 'fulfilled' && mt5Result.value?.data) {
        setMt5Status(mt5Result.value.data);
      }

      // Fetch background data
      const backgroundResults = await Promise.allSettled([
        subscriptionAPI.getSubscription().catch(e => ({ data: null })),
        tradesAPI.getHistory(10).catch(e => ({ data: { trades: [] } })),
        tradesAPI.getStatistics().catch(e => ({ data: null }))
      ]);

      if (backgroundResults[0].status === 'fulfilled' && backgroundResults[0].value?.data) {
        setSubscription(backgroundResults[0].value.data);
      }
      if (backgroundResults[1].status === 'fulfilled' && backgroundResults[1].value?.data?.trades) {
        setTrades(backgroundResults[1].value.data.trades);
      }
      if (backgroundResults[2].status === 'fulfilled' && backgroundResults[2].value?.data?.statistics) {
        setStatistics(backgroundResults[2].value.data.statistics);
      }
      
      setError(null);
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError('Failed to load dashboard data');
    }
  };

  const handleBotControl = async (action) => {
    try {
      if (action === 'start') {
        // Check if bot config exists
        if (!profile?.bot_config) {
          alert('Please configure your bot settings first. Add MT5 credentials in settings.');
          return;
        }
        
        // Check if MT5 is running
        if (mt5Status && !mt5Status.is_running) {
          const launchMT5 = window.confirm(
            '⚠️ MetaTrader 5 is not running!\n\n' +
            'Would you like to launch MT5 now?\n\n' +
            'Click OK to launch MT5 automatically, or Cancel to launch it manually.'
          );
          
          if (launchMT5) {
            try {
              await systemAPI.launchMT5();
              alert('✅ MT5 launched successfully! Starting bot...');
              // Wait a moment for MT5 to initialize
              await new Promise(resolve => setTimeout(resolve, 3000));
            } catch (launchErr) {
              alert('❌ Failed to launch MT5 automatically.\n\nPlease launch MetaTrader 5 manually and try again.');
              return;
            }
          } else {
            alert('Please launch MetaTrader 5 manually and click "Start Bot" again.');
            return;
          }
        }
        
        // Show connecting message
        const confirmed = window.confirm(
          '🚀 Starting Bot...\n\n' +
          'The bot will:\n' +
          '✅ Connect to MetaTrader 5\n' +
          '✅ Verify your account credentials\n' +
          '✅ Begin monitoring market conditions\n' +
          '✅ Execute trades based on your risk settings\n\n' +
          'Continue?'
        );
        
        if (!confirmed) return;
        
        // Show loading state
        alert('⏳ Connecting to MT5 and starting bot...\n\nThis may take a few seconds.');
        
        await botAPI.startBot();
        alert('✅ Bot started successfully!\n\n📊 MT5 is connected and the bot is now actively trading based on your risk management settings.');
      } else if (action === 'stop') {
        const confirmed = window.confirm(
          '⏹️ Stop Bot?\n\n' +
          'This will:\n' +
          '• Stop opening new trades\n' +
          '• Close MT5 connection\n' +
          '• Keep existing positions open\n\n' +
          'Continue?'
        );
        
        if (!confirmed) return;
        
        await botAPI.stopBot();
        alert('⏹️ Bot stopped successfully!\n\nMT5 connection closed.');
      } else if (action === 'pause') {
        const confirmed = window.confirm(
          '⏸️ Pause Bot?\n\n' +
          'This will:\n' +
          '• Stop opening new trades\n' +
          '• Keep MT5 connection active\n' +
          '• Monitor existing positions\n\n' +
          'You can resume anytime.\n\n' +
          'Continue?'
        );
        
        if (!confirmed) return;
        
        await botAPI.pauseBot();
        alert('⏸️ Bot paused!\n\nNo new trades will be opened. Existing trades will continue.');
      } else if (action === 'resume') {
        // Check if bot is actually paused
        if (!botStatus || botStatus.status !== 'paused') {
          alert('⚠️ Cannot Resume\n\n' +
            'The bot needs to be running and paused first.\n\n' +
            '💡 To start trading:\n' +
            '1. Click "Start Bot" button\n' +
            '2. Wait for bot to connect to MT5\n' +
            '3. Then you can pause/resume as needed');
          return;
        }
        
        const confirmed = window.confirm(
          '▶️ Resume Trading?\n\n' +
          'The bot will:\n' +
          '✅ Resume looking for trade opportunities\n' +
          '✅ Execute trades based on your settings\n' +
          '✅ Actively monitor the market\n\n' +
          'Continue?'
        );
        
        if (!confirmed) return;
        
        await botAPI.resumeBot();
        alert('▶️ Bot resumed!\n\nNow actively looking for trade opportunities.');
      }
      
      // Refresh dashboard after 1 second
      setTimeout(() => fetchDashboardData(true), 1000);
    } catch (err) {
      const errorMsg = err.response?.data?.detail || `Failed to ${action} bot`;
      
      // Provide helpful error messages
      let helpText = '';
      if (action === 'start') {
        helpText = '\n\n💡 Troubleshooting:\n' +
          '• Ensure MT5 is installed\n' +
          '• Check your login credentials\n' +
          '• Verify your internet connection\n' +
          '• Check if you have an active subscription';
      } else if (action === 'resume') {
        helpText = '\n\n💡 To resume the bot:\n' +
          '1. First click "Start Bot" to launch\n' +
          '2. Then click "Pause" when running\n' +
          '3. Now you can use "Resume"\n\n' +
          'Resume only works for paused bots, not stopped ones.';
      }
      
      alert(`❌ Error: ${errorMsg}${helpText}`);
      console.error(`Error ${action}ing bot:`, err);
    }
  };

  const handleLogout = () => {
    localStorage.clear();
    window.location.href = '/login';
  };

  const handleOpenMT5Charts = async () => {
    if (botStatus?.status !== 'running' && botStatus?.status !== 'paused') {
      alert('ℹ️ Bot must be running or paused to view MT5 charts.');
      return;
    }

    try {
      // Get symbol and timeframe from bot config
      const symbol = profile?.bot_config?.symbol || 'EURUSD';
      const timeframe = profile?.bot_config?.timeframe || 'H1';
      
      const response = await systemAPI.openMT5Charts(symbol, timeframe);
      
      if (response.data.success) {
        alert(
          `📊 ${response.data.message}\n\n` +
          'MT5 window is now visible with your trading chart!\n\n' +
          'You can see:\n' +
          '• Active positions\n' +
          '• Open orders\n' +
          '• Price charts\n' +
          '• Trading history'
        );
      }
    } catch (err) {
      console.error('Error opening MT5 charts:', err);
      const errorMsg = err.response?.data?.detail || 'Failed to open MT5 charts';
      alert(`❌ ${errorMsg}\n\nPlease ensure MetaTrader 5 is installed and try again.`);
    }
  };

  const handleInstantTradeChange = (e) => {
    const { name, value } = e.target;
    setInstantTrade(prev => ({
      ...prev,
      [name]: name === 'risk_per_trade' ? parseFloat(value) : value
    }));
  };

  const handleInstantTrade = async (side) => {
    if (!instantTrade.symbol) {
      alert('❌ Please select a trading pair first.');
      return;
    }

    if (!instantTrade.risk_per_trade || instantTrade.risk_per_trade <= 0) {
      alert('❌ Please enter a valid risk per trade percentage.');
      return;
    }

    const confirmOrder = window.confirm(
      `Execute ${side} instantly?\n\n` +
      `Pair: ${instantTrade.symbol}\n` +
      `Risk per trade: ${instantTrade.risk_per_trade}%\n\n` +
      'This will place a live market order immediately.'
    );

    if (!confirmOrder) return;

    try {
      setInstantTradeLoading(true);
      const response = await botAPI.instantTrade({
        symbol: instantTrade.symbol,
        side,
        risk_per_trade: instantTrade.risk_per_trade,
      });

      const data = response.data;
      alert(
        `✅ ${data.side} order executed\n\n` +
        `Ticket: ${data.ticket}\n` +
        `Pair: ${data.symbol}\n` +
        `Lot: ${data.lot_size}\n` +
        `Entry: ${data.entry_price}`
      );

      setInstantTradeLoading(false);
      await fetchDashboardData(true);
    } catch (err) {
      const isTimeout = err.code === 'ECONNABORTED';
      const errorMsg = isTimeout
        ? 'Instant execution timed out after 45 seconds. MT5 may be unresponsive. Please check MT5 terminal and try again.'
        : (err.response?.data?.detail || 'Instant execution failed');
      alert(`❌ ${errorMsg}`);
      console.error('Instant trade error:', err);
    } finally {
      setInstantTradeLoading(false);
    }
  };

  // Show dashboard immediately (no loading screen)
  // Add error boundary
  if (error && !botStatus && !profile) {
    return (
      <div className="dashboard-container">
        <div className="error-banner">
          {error}
          <br />
          <button onClick={fetchDashboardData} style={{marginTop: '10px', padding: '10px 20px', cursor: 'pointer'}}>
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🤖 SMC Trading Bot Dashboard</h1>
        <div className="header-actions">
          {/* Real-time Bot Status Indicator */}
          <div className="live-status-indicator">
            <div className="status-icon-container">
              {String(botStatus?.status || '').toLowerCase() === 'running' && (
                <div className="status-icon running" title="Bot is actively trading">
                  <span className="pulse-dot"></span>
                  <span className="status-icon-text">🟢 LIVE</span>
                </div>
              )}
              {String(botStatus?.status || '').toLowerCase() === 'paused' && (
                <div className="status-icon paused" title="Bot is paused">
                  <span className="pause-icon">⏸️</span>
                  <span className="status-icon-text">PAUSED</span>
                </div>
              )}
              {(!botStatus?.status || String(botStatus?.status || '').toLowerCase() === 'stopped') && (
                <div className="status-icon stopped" title="Bot is stopped">
                  <span className="stop-icon">⏹️</span>
                  <span className="status-icon-text">OFFLINE</span>
                </div>
              )}
            </div>
          </div>
          
          {/* Connection & Session Status */}
          <div className="connection-session-info" style={{display: 'flex', gap: '20px', alignItems: 'center', marginRight: '20px'}}>
            {/* Connection Status */}
            <div style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px'}}>
              <span 
                style={{
                  display: 'inline-block',
                  width: '10px',
                  height: '10px',
                  borderRadius: '50%',
                  backgroundColor: botStatus?.is_connected ? '#4caf50' : '#999',
                  animation: botStatus?.is_connected ? 'pulse 2s infinite' : 'none'
                }}
              ></span>
              <span>{botStatus?.is_connected ? '✅ Connected' : '❌ Disconnected'}</span>
            </div>
            
            {/* Session Status */}
            <div style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px'}}>
              {botStatus?.session_status === 'active' ? (
                <>
                  <span style={{color: '#4caf50', fontSize: '16px'}}>📍</span>
                  <span style={{color: '#4caf50'}}>Session Active: {botStatus?.session_time}</span>
                </>
              ) : (
                <>
                  <span style={{color: '#ff9800', fontSize: '16px'}}>⏱️</span>
                  <span style={{color: '#999'}}>Session Inactive: {botStatus?.session_time}</span>
                </>
              )}
            </div>
            
            {/* Selected Pairs */}
            {botStatus?.selected_symbols && botStatus?.selected_symbols.length > 0 && (
              <div style={{display: 'flex', alignItems: 'center', gap: '8px', fontSize: '13px'}}>
                <span style={{color: '#2196f3', fontSize: '16px'}}>🔗</span>
                <span style={{color: '#2196f3'}}>Pairs: {botStatus?.selected_symbols.join(', ')}</span>
              </div>
            )}
          </div>
          
          <span className="user-name">{profile?.trader?.name || 'Trader'}</span>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div className="dashboard-tabs">
        <button 
          className={`tab-button ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => setActiveTab('dashboard')}
        >
          📊 Dashboard
        </button>
        <button 
          className={`tab-button ${activeTab === 'bot-setup' ? 'active' : ''}`}
          onClick={() => setActiveTab('bot-setup')}
        >
          ⚙️ Bot Setup
        </button>
        <button 
          className={`tab-button ${activeTab === 'risk' ? 'active' : ''}`}
          onClick={() => setActiveTab('risk')}
        >
          🛡️ Risk Management
        </button>
        <button 
          className={`tab-button ${activeTab === 'subscription' ? 'active' : ''}`}
          onClick={() => setActiveTab('subscription')}
        >
          💳 Subscription
        </button>
      </div>

      {error && <div className="error-banner">{error}</div>}
      
      {/* Dashboard Tab Content */}
      {activeTab === 'dashboard' && (
        <>
          {/* MT5 Status Alert */}
          {mt5Status && !mt5Status.is_running && botStatus?.status === 'stopped' && (
            <div className="warning-banner">
              ⚠️ MetaTrader 5 is not running. The bot will launch MT5 automatically when you click "Start Bot".
            </div>
          )}

          {/* Bot Control Panel - Prominent */}
          <div className="card bot-control-panel">
        <h2>⚡ Bot Control Center</h2>
        <div className="control-panel-content">
          <div className="status-display">
            <div 
              className={`status-indicator-large ${botStatus?.status || 'stopped'}`}
              onClick={botStatus?.status === 'running' ? handleOpenMT5Charts : undefined}
              title={botStatus?.status === 'running' ? 'Click to view MT5 charts' : ''}
            >
              <span className={`status-dot-large ${botStatus?.status || 'stopped'}`}></span>
              <div className="status-details">
                <span className="status-label">Bot Status:</span>
                <span className="status-value">
                  {String(botStatus?.status || 'stopped').toUpperCase()}
                  {String(botStatus?.status || '').toLowerCase() === 'running' && ' 📊'}
                </span>
              </div>
            </div>
          </div>

          <div className="quick-actions" style={{minHeight: '200px', display: 'block', visibility: 'visible'}}>            
            {(!botStatus?.status || String(botStatus?.status || '').toLowerCase() === 'stopped') ? (
              <div style={{display: 'block', visibility: 'visible', width: '100%'}}>
                <button 
                  onClick={() => handleBotControl('start')} 
                  disabled={mt5Status?.mt5_found === false}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    width: '100%',
                    padding: '20px 25px',
                    background: 'linear-gradient(135deg, #4caf50 0%, #45a049 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)',
                    marginBottom: '15px'
                  }}
                >
                  <span style={{fontSize: '40px'}}>
                    <svg width="40" height="40" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </span>
                  <span style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '2px'}}>
                    <span style={{fontSize: '18px', fontWeight: '700'}}>▶️ Start Bot</span>
                    <span style={{fontSize: '12px', opacity: '0.9', fontWeight: '400'}}>
                      {mt5Status?.is_running ? 'Connect to MT5' : 'Launch & Connect'}
                    </span>
                  </span>
                </button>
                <div style={{marginTop: '15px', padding: '15px', background: 'rgba(255,255,255,0.1)', borderRadius: '8px', fontSize: '14px', display: 'block'}}>
                  <p style={{margin: '0 0 8px 0', fontWeight: '600'}}>📝 Quick Start Guide:</p>
                  <p style={{margin: '0', lineHeight: '1.6', opacity: '0.9'}}>
                    1. Click "Start Bot" to launch MT5 and connect<br/>
                    2. Bot will begin trading automatically<br/>
                    3. Use "Pause" to temporarily stop new trades<br/>
                    4. Use "Resume" to continue after pausing
                  </p>
                </div>
              </div>
            ) : String(botStatus?.status || '').toLowerCase() === 'running' ? (
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                <button 
                  onClick={() => handleBotControl('stop')} 
                  title="Stop the trading bot"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    padding: '20px 25px',
                    background: 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                >
                  <span style={{fontSize: '32px'}}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="4" y="4" width="16" height="16" rx="2"/>
                    </svg>
                  </span>
                  <span style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '2px'}}>
                    <span style={{fontSize: '18px', fontWeight: '700'}}>⏹️ Stop Bot</span>
                    <span style={{fontSize: '12px', opacity: '0.9', fontWeight: '400'}}>Close all connections</span>
                  </span>
                </button>
                
                <button 
                  onClick={() => handleBotControl('pause')} 
                  title="Pause new trades"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    padding: '20px 25px',
                    background: 'linear-gradient(135deg, #ff9800 0%, #f57c00 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                >
                  <span style={{fontSize: '32px'}}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="6" y="4" width="4" height="16" rx="1"/>
                      <rect x="14" y="4" width="4" height="16" rx="1"/>
                    </svg>
                  </span>
                  <span style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '2px'}}>
                    <span style={{fontSize: '18px', fontWeight: '700'}}>⏸️ Pause</span>
                    <span style={{fontSize: '12px', opacity: '0.9', fontWeight: '400'}}>Stop new trades</span>
                  </span>
                </button>
              </div>
            ) : String(botStatus?.status || '').toLowerCase() === 'paused' ? (
              <div style={{display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '15px'}}>
                <button 
                  onClick={() => handleBotControl('stop')} 
                  title="Stop the trading bot"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    padding: '20px 25px',
                    background: 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                >
                  <span style={{fontSize: '32px'}}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                      <rect x="4" y="4" width="16" height="16" rx="2"/>
                    </svg>
                  </span>
                  <span style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '2px'}}>
                    <span style={{fontSize: '18px', fontWeight: '700'}}>⏹️ Stop Bot</span>
                    <span style={{fontSize: '12px', opacity: '0.9', fontWeight: '400'}}>Close all connections</span>
                  </span>
                </button>
                
                <button 
                  onClick={() => handleBotControl('resume')} 
                  title="Resume trading"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '15px',
                    padding: '20px 25px',
                    background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)',
                    color: 'white',
                    border: 'none',
                    borderRadius: '12px',
                    fontSize: '16px',
                    fontWeight: '600',
                    cursor: 'pointer',
                    boxShadow: '0 4px 12px rgba(0,0,0,0.2)'
                  }}
                >
                  <span style={{fontSize: '32px'}}>
                    <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                      <path d="M8 5v14l11-7z"/>
                    </svg>
                  </span>
                  <span style={{display: 'flex', flexDirection: 'column', alignItems: 'flex-start', gap: '2px'}}>
                    <span style={{fontSize: '18px', fontWeight: '700'}}>▶️ Resume</span>
                    <span style={{fontSize: '12px', opacity: '0.9', fontWeight: '400'}}>Continue trading</span>
                  </span>
                </button>
              </div>
            ) : null}
          </div>
        </div>
      </div>

      {/* Instant Execution */}
      <div className="card instant-execution-card">
        <h2>⚡ Instant Execution</h2>
        <div className="instant-execution-grid">
          <div className="instant-field">
            <label>Trading Pair</label>
            <select
              name="symbol"
              value={instantTrade.symbol}
              onChange={handleInstantTradeChange}
              disabled={instantTradeLoading}
            >
              {(profile?.bot_config?.symbols?.length ? profile.bot_config.symbols : ['XAUUSD']).map((symbol) => (
                <option key={symbol} value={symbol}>{symbol}</option>
              ))}
            </select>
          </div>

          <div className="instant-field">
            <label>Risk Per Trade (%)</label>
            <input
              type="number"
              name="risk_per_trade"
              min="0.1"
              max="100"
              step="0.1"
              value={instantTrade.risk_per_trade}
              onChange={handleInstantTradeChange}
              disabled={instantTradeLoading}
            />
          </div>
        </div>

        <div className="instant-buttons">
          <button
            className="btn-instant-sell"
            onClick={() => handleInstantTrade('SELL')}
            disabled={instantTradeLoading}
          >
            {instantTradeLoading ? 'Processing...' : '🔻 SELL NOW'}
          </button>
          <button
            className="btn-instant-buy"
            onClick={() => handleInstantTrade('BUY')}
            disabled={instantTradeLoading}
          >
            {instantTradeLoading ? 'Processing...' : '🔼 BUY NOW'}
          </button>
        </div>
      </div>

      {/* Bot Status Card */}
      <div className="card bot-status-card">
        <h2>Bot Status Details</h2>
        <div className="status-content">
          <div 
            className={`status-indicator ${botStatus?.status === 'running' ? 'clickable' : ''}`}
            onClick={botStatus?.status === 'running' ? handleOpenMT5Charts : undefined}
            title={botStatus?.status === 'running' ? 'Click to view MT5 charts' : ''}
          >
            <span className={`status-dot ${botStatus?.status || 'stopped'}`}></span>
            <span className="status-text">
              {String(botStatus?.status || 'stopped').toUpperCase()}
              {String(botStatus?.status || '').toLowerCase() === 'running' && ' 📊'}
            </span>
          </div>
          
          {botStatus?.status === 'running' && (
            <div className="bot-info">
              <p>🔌 MT5: <span className="status-connected">Connected</span></p>
              <p>⏱️ Uptime: {botStatus.uptime || 'N/A'}</p>
              <p>📊 Active Trades: {botStatus.active_trades || 0}</p>
              <p>💰 Daily P&L: ${botStatus.daily_pnl?.toFixed(2) || '0.00'}</p>
              <p className="trading-status">✅ Actively Trading</p>
              <button 
                onClick={handleOpenMT5Charts} 
                className="btn btn-chart"
                style={{marginTop: '10px', width: '100%'}}
              >
                📈 View MT5 Charts
              </button>
            </div>
          )}
          
          {botStatus?.status === 'paused' && (
            <div className="bot-info">
              <p>🔌 MT5: <span className="status-connected">Connected</span></p>
              <p>⏸️ Status: Paused</p>
              <p>ℹ️ Monitoring only - No new trades</p>
              <button 
                onClick={handleOpenMT5Charts} 
                className="btn btn-chart"
                style={{marginTop: '10px', width: '100%'}}
              >
                📈 View MT5 Charts
              </button>
            </div>
          )}
          
          {botStatus?.status === 'stopped' && (
            <div className="bot-info">
              <p>🔌 MT5: <span className="status-disconnected">{mt5Status?.is_running ? 'Ready' : 'Not Running'}</span></p>
              <p>ℹ️ {mt5Status?.is_running ? 'Click "Start Bot" to connect and begin trading' : 'MT5 will launch automatically when you start the bot'}</p>
              {!mt5Status?.mt5_found && (
                <p className="error-text">❌ MT5 not found on system. Please install MetaTrader 5.</p>
              )}
            </div>
          )}
        </div>
      </div>

      {/* Subscription & Account Info */}
      <div className="cards-row">
        <div className="card subscription-card">
          <h3>📅 Subscription</h3>
          {subscription?.has_subscription ? (
            <>
              <p className="plan-name">{String(subscription?.subscription?.plan || '').toUpperCase()}</p>
              <p>Expires: {subscription.subscription?.expiry_date}</p>
              <p className={subscription.days_remaining < 7 ? 'text-warning' : ''}>
                {subscription.days_remaining} days remaining
              </p>
            </>
          ) : (
            <p className="no-subscription">No active subscription</p>
          )}
        </div>

        <div className="card account-card">
          <h3>💼 Account Info</h3>
          {profile?.bot_config ? (
            <>
              <p>MT5 Login: {profile.bot_config.mt5_login}</p>
              <p>Server: {profile.bot_config.mt5_server}</p>
              <p>Balance: ${profile.bot_config.balance?.toFixed(2) || '0.00'}</p>
            </>
          ) : (
            <p className="no-config">No bot configuration</p>
          )}
        </div>
      </div>

      {/* Statistics */}
      {statistics && (
        <div className="card statistics-card">
          <div className="stats-header">
            <h2>📊 Trading Statistics</h2>
            <span className="stats-source">Source: {String(statistics.source || 'MT5').toUpperCase()}</span>
          </div>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Trades</span>
              <span className="stat-value">{statistics.total_trades || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Open Trades</span>
              <span className="stat-value">{statistics.open_trades || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Closed Trades</span>
              <span className="stat-value">{statistics.closed_trades || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Win Rate</span>
              <span className="stat-value">{statistics.win_rate?.toFixed(1) || 0}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total P&L</span>
              <span className={`stat-value ${(statistics.total_profit ?? statistics.total_pnl ?? 0) >= 0 ? 'positive' : 'negative'}`}>
                {(statistics.total_profit ?? statistics.total_pnl ?? 0) >= 0 ? '+' : ''}${(statistics.total_profit ?? statistics.total_pnl ?? 0).toFixed(2)}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Avg Profit/Trade</span>
              <span className="stat-value">${(statistics.average_profit ?? statistics.avg_profit ?? 0).toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Best Trade</span>
              <span className="stat-value positive">+${(statistics.best_trade || 0).toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Worst Trade</span>
              <span className="stat-value negative">${(statistics.worst_trade || 0).toFixed(2)}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Winning Trades</span>
              <span className="stat-value positive">{statistics.winning_trades || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Losing Trades</span>
              <span className="stat-value negative">{statistics.losing_trades || 0}</span>
            </div>
          </div>
        </div>
      )}

      {/* Recent Trades */}
      <div className="card trades-card">
        <div className="trades-header">
          <h2>📈 Recent Trades</h2>
          <span className="trades-count">Total: {trades.length}</span>
        </div>
        {trades.length > 0 ? (
          <div className="trades-table-wrapper">
            <table className="trades-table">
              <thead>
                <tr>
                  <th>#</th>
                  <th>Ticket</th>
                  <th>Symbol</th>
                  <th>Type</th>
                  <th>Lot Size</th>
                  <th>Entry</th>
                  <th>Exit</th>
                  <th>SL</th>
                  <th>TP</th>
                  <th>P&L</th>
                  <th>Commission</th>
                  <th>Swap</th>
                  <th>Entry Time</th>
                  <th>Exit Time</th>
                  <th>Status</th>
                  <th>Exit Reason</th>
                </tr>
              </thead>
              <tbody>
                {trades.map((trade, index) => {
                  const pnl = trade.pnl ?? trade.profit ?? 0;
                  const entryTime = trade.entry_time ? new Date(trade.entry_time + (trade.entry_time.includes('T') ? '' : 'T00:00:00')).toLocaleString() : '-';
                  const exitTime = trade.exit_time ? new Date(trade.exit_time + (trade.exit_time.includes('T') ? '' : 'T00:00:00')).toLocaleString() : '-';
                  const exitReason = trade.notes || '-';
                  const lotSize = trade.lot_size ?? trade.lots ?? 0;
                  return (
                    <tr key={index}>
                      <td>{index + 1}</td>
                      <td style={{fontSize: '11px', color: '#888'}}>{trade.ticket || '-'}</td>
                      <td><span className="symbol-badge">{trade.symbol || '-'}</span></td>
                      <td className={`signal-${(trade.type || trade.signal || '').toLowerCase()}`}>{trade.type || trade.signal || '-'}</td>
                      <td>{lotSize}</td>
                      <td>{trade.entry_price != null ? trade.entry_price.toFixed(trade.symbol === 'XAUUSD' ? 2 : 5) : '-'}</td>
                      <td>{trade.exit_price != null ? trade.exit_price.toFixed(trade.symbol === 'XAUUSD' ? 2 : 5) : '-'}</td>
                      <td>{trade.stop_loss != null && trade.stop_loss > 0 ? trade.stop_loss.toFixed(trade.symbol === 'XAUUSD' ? 2 : 5) : '-'}</td>
                      <td>{trade.take_profit != null && trade.take_profit > 0 ? trade.take_profit.toFixed(trade.symbol === 'XAUUSD' ? 2 : 5) : '-'}</td>
                      <td className={pnl >= 0 ? 'positive' : 'negative'}>
                        <span className={pnl >= 0 ? 'profit-positive' : 'profit-negative'}>
                          {pnl >= 0 ? '+' : ''}${pnl.toFixed(2)}
                        </span>
                      </td>
                      <td style={{fontSize: '12px', color: '#888'}}>{(trade.commission || 0).toFixed(2)}</td>
                      <td style={{fontSize: '12px', color: '#888'}}>{(trade.swap || 0).toFixed(2)}</td>
                      <td className="time-cell">{entryTime}</td>
                      <td className="time-cell">{exitTime}</td>
                      <td>
                        <span className={`status-badge ${trade.status}`}>
                          {trade.status === 'open' ? '🟢 Open' : trade.status === 'closed' ? '🔴 Closed' : trade.status || '-'}
                        </span>
                      </td>
                      <td>
                        <span className={`reason-badge ${exitReason.toLowerCase().replace(' ', '-')}`}>
                          {exitReason}
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        ) : (
          <div className="no-trades">
            <p>📭 No trades yet</p>
            <p className="no-trades-hint">Trades will appear here once the bot executes them or when MT5 history is synced.</p>
          </div>
        )}
      </div>
        </>
      )}

      {/* Bot Setup Tab */}
      {activeTab === 'bot-setup' && (
        <BotSetup onComplete={() => setActiveTab('dashboard')} />
      )}

      {/* Risk Management Tab */}
      {activeTab === 'risk' && (
        <RiskManagement />
      )}

      {/* Subscription Tab */}
      {activeTab === 'subscription' && (
        <SubscriptionPlans />
      )}
    </div>
  );
}

export default Dashboard;
