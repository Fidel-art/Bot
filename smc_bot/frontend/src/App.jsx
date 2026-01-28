import React, { useState, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useNavigate } from 'react-router-dom';
import Login from './components/Login';
import Register from './components/Register';
import Dashboard from './components/Dashboard';
import SubscriptionPlans from './components/SubscriptionPlans';
import BotSetup from './components/BotSetup';
import RiskManagement from './components/RiskManagement';
import './App.css';

// Protected Route that checks authentication and setup status
function ProtectedRoute({ children, requiresSubscription = false, requiresConfig = false }) {
  const navigate = useNavigate();
  const [isChecking, setIsChecking] = useState(true);
  const [profile, setProfile] = useState(null);

  useEffect(() => {
    const checkAccess = async () => {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        navigate('/login');
        return;
      }

      // Fetch user profile to check setup status
      try {
        const response = await fetch('http://localhost:8001/api/profile', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        if (response.ok) {
          const data = await response.json();
          setProfile(data);
          
          // Redirect based on setup status
          if (requiresSubscription && !data.subscription) {
            navigate('/subscription-plans');
            return;
          }
          
          if (requiresConfig && !data.bot_config) {
            navigate('/bot-setup');
            return;
          }
        } else {
          navigate('/login');
          return;
        }
      } catch (err) {
        console.error('Error checking access:', err);
      }
      
      setIsChecking(false);
    };

    checkAccess();
  }, [navigate, requiresSubscription, requiresConfig]);

  if (isChecking) {
    return <div className="loading">Loading...</div>;
  }

  return children;
}

function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Check if user has valid token
    const token = localStorage.getItem('access_token');
    if (token) {
      setIsAuthenticated(true);
    }
    setLoading(false);
  }, []);

  if (loading) {
    return <div className="loading">Loading...</div>;
  }

  return (
    <Router>
      <div className="App">
        <Routes>
          <Route 
            path="/login" 
            element={
              isAuthenticated ? <Navigate to="/subscription-plans" /> : <Login setAuth={setIsAuthenticated} />
            } 
          />
          <Route 
            path="/register" 
            element={
              isAuthenticated ? <Navigate to="/subscription-plans" /> : <Register />
            } 
          />
          <Route 
            path="/subscription-plans" 
            element={
              <ProtectedRoute>
                <OnboardingFlow step="subscription" />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/bot-setup" 
            element={
              <ProtectedRoute requiresSubscription={true}>
                <OnboardingFlow step="bot-setup" />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/risk-management" 
            element={
              <ProtectedRoute requiresSubscription={true} requiresConfig={true}>
                <OnboardingFlow step="risk-management" />
              </ProtectedRoute>
            } 
          />
          <Route 
            path="/dashboard" 
            element={
              <ProtectedRoute requiresSubscription={true} requiresConfig={true}>
                <Dashboard setAuth={setIsAuthenticated} />
              </ProtectedRoute>
            } 
          />
          <Route path="/" element={<Navigate to="/subscription-plans" />} />
        </Routes>
      </div>
    </Router>
  );
}

// Onboarding Flow Component
function OnboardingFlow({ step }) {
  const navigate = useNavigate();

  const handleSubscriptionComplete = () => {
    navigate('/bot-setup');
  };

  const handleBotSetupComplete = () => {
    navigate('/risk-management');
  };

  const handleRiskManagementComplete = () => {
    navigate('/dashboard');
  };

  if (step === 'subscription') {
    return <SubscriptionPlans onComplete={handleSubscriptionComplete} />;
  }

  if (step === 'bot-setup') {
    return <BotSetup onComplete={handleBotSetupComplete} />;
  }

  if (step === 'risk-management') {
    return <RiskManagement onComplete={handleRiskManagementComplete} />;
  }

  return <div>Invalid step</div>;
}

export default App;
