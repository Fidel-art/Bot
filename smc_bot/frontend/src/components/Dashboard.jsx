import React, { useState, useEffect } from 'react';
import { botAPI, tradesAPI, profileAPI, subscriptionAPI, systemAPI } from '../services/api';
import './Dashboard.css';

function Dashboard() {
  const [loading, setLoading] = useState(true);
  const [botStatus, setBotStatus] = useState(null);
  const [profile, setProfile] = useState(null);
  const [subscription, setSubscription] = useState(null);
  const [trades, setTrades] = useState([]);
  const [statistics, setStatistics] = useState(null);
  const [error, setError] = useState(null);
  const [mt5Status, setMt5Status] = useState(null);

  // Fetch dashboard data
  useEffect(() => {
    fetchDashboardData();
    // Refresh data every 5 seconds
    const interval = setInterval(fetchDashboardData, 5000);
    return () => clearInterval(interval);
  }, []);

  const fetchDashboardData = async () => {
    try {
      // Fetch all data with individual error handling
      const results = await Promise.allSettled([
        botAPI.getStatus(),
        profileAPI.getProfile(),
        subscriptionAPI.getSubscription(),
        tradesAPI.getHistory(10),
        tradesAPI.getStatistics(),
        systemAPI.getMT5Status()
      ]);

      // Process results
      if (results[0].status === 'fulfilled') setBotStatus(results[0].value.data);
      if (results[1].status === 'fulfilled') setProfile(results[1].value.data);
      if (results[2].status === 'fulfilled') setSubscription(results[2].value.data);
      if (results[3].status === 'fulfilled') setTrades(results[3].value.data.trades || []);
      if (results[4].status === 'fulfilled') setStatistics(results[4].value.data);
      if (results[5].status === 'fulfilled') setMt5Status(results[5].value.data);
      
      // Check if any critical calls failed
      const criticalFailed = results.slice(0, 2).some(r => r.status === 'rejected');
      if (criticalFailed) {
        console.error('Critical API calls failed:', results);
        setError('Some data failed to load. Please refresh the page.');
      } else {
        setError(null);
      }
    } catch (err) {
      console.error('Error fetching dashboard data:', err);
      setError(err.response?.data?.detail || 'Failed to load dashboard data');
    } finally {
      setLoading(false);
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
        await botAPI.pauseBot();
        alert('⏸️ Bot paused!\n\nNo new trades will be opened. Existing trades will continue.');
      } else if (action === 'resume') {
        await botAPI.resumeBot();
        alert('▶️ Bot resumed!\n\nNow actively looking for trade opportunities.');
      }
      
      // Refresh dashboard after 1 second
      setTimeout(() => fetchDashboardData(), 1000);
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
      
      setLoading(true);
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
    } finally {
      setLoading(false);
    }

  };

  if (loading) {
    return (
      <div className="dashboard-container">
        <div className="loading">Loading dashboard...</div>
      </div>
    );
  }

  return (
    <div className="dashboard-container">
      {/* Header */}
      <header className="dashboard-header">
        <h1>🤖 SMC Trading Bot Dashboard</h1>
        <div className="header-actions">
          <span className="user-name">{profile?.trader?.name || 'Trader'}</span>
          <button onClick={handleLogout} className="btn-logout">Logout</button>
        </div>
      </header>

      {error && <div className="error-banner">{error}</div>}
      
      {/* MT5 Status Alert */}
      {mt5Status && !mt5Status.is_running && botStatus?.status === 'stopped' && (
        <div className="warning-banner">
          ⚠️ MetaTrader 5 is not running. The bot will launch MT5 automatically when you click "Start Bot".
        </div>
      )}

      {/* Bot Status Card */}
      <div className="card bot-status-card">
        <h2>Bot Status</h2>
        <div className="status-content">
          <div 
            className={`status-indicator ${botStatus?.status === 'running' ? 'clickable' : ''}`}
            onClick={botStatus?.status === 'running' ? handleOpenMT5Charts : undefined}
            title={botStatus?.status === 'running' ? 'Click to view MT5 charts' : ''}
          >
            <span className={`status-dot ${botStatus?.status || 'stopped'}`}></span>
            <span className="status-text">
              {botStatus?.status?.toUpperCase() || 'STOPPED'}
              {botStatus?.status === 'running' && ' 📊'}
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

          <div className="bot-controls">
            {botStatus?.status === 'stopped' ? (
              <button 
                onClick={() => handleBotControl('start')} 
                className="btn btn-start"
                disabled={!mt5Status?.mt5_found}
              >
                ▶️ Start Bot & {mt5Status?.is_running ? 'Connect to' : 'Launch'} MT5
              </button>
            ) : (
              <>
                <button onClick={() => handleBotControl('stop')} className="btn btn-stop">⏹️ Stop</button>
                {botStatus?.status === 'running' ? (
                  <button onClick={() => handleBotControl('pause')} className="btn btn-pause">⏸️ Pause</button>
                ) : (
                  <button onClick={() => handleBotControl('resume')} className="btn btn-resume">▶️ Resume</button>
                )}
              </>
            )}
          </div>
        </div>
      </div>

      {/* Subscription & Account Info */}
      <div className="cards-row">
        <div className="card subscription-card">
          <h3>📅 Subscription</h3>
          {subscription?.has_subscription ? (
            <>
              <p className="plan-name">{subscription.subscription?.plan?.toUpperCase()}</p>
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
          <h2>📊 Trading Statistics</h2>
          <div className="stats-grid">
            <div className="stat-item">
              <span className="stat-label">Total Trades</span>
              <span className="stat-value">{statistics.total_trades || 0}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Win Rate</span>
              <span className="stat-value">{statistics.win_rate?.toFixed(1) || 0}%</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Total P&L</span>
              <span className={`stat-value ${statistics.total_pnl >= 0 ? 'positive' : 'negative'}`}>
                ${statistics.total_pnl?.toFixed(2) || '0.00'}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Average Profit</span>
              <span className="stat-value">${statistics.avg_profit?.toFixed(2) || '0.00'}</span>
            </div>
          </div>
        </div>
      )}

      {/* Recent Trades */}
      <div className="card trades-card">
        <h2>📈 Recent Trades</h2>
        {trades.length > 0 ? (
          <table className="trades-table">
            <thead>
              <tr>
                <th>Symbol</th>
                <th>Type</th>
                <th>Entry</th>
                <th>Exit</th>
                <th>P&L</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {trades.map((trade, index) => (
                <tr key={index}>
                  <td>{trade.symbol}</td>
                  <td>{trade.type}</td>
                  <td>{trade.entry_price?.toFixed(2)}</td>
                  <td>{trade.exit_price?.toFixed(2) || '-'}</td>
                  <td className={trade.pnl >= 0 ? 'positive' : 'negative'}>
                    ${trade.pnl?.toFixed(2)}
                  </td>
                  <td>
                    <span className={`status-badge ${trade.status}`}>{trade.status}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="no-trades">No trades yet</p>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
