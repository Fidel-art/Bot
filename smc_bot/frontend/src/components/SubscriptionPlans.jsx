import React, { useState } from 'react';
import { subscriptionAPI } from '../services/api';
import './SubscriptionPlans.css';

function SubscriptionPlans({ onComplete }) {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);

  const plans = [
    {
      id: 'free',
      name: 'Free Trial',
      price: '$0',
      duration: '7 Days',
      features: [
        '✅ 7 days full access',
        '✅ All trading features',
        '✅ Up to 3 trades per day',
        '✅ Basic support',
        '⚠️ Limited to XAUUSD only'
      ],
      popular: false
    },
    {
      id: 'weekly',
      name: 'Weekly Plan',
      price: '$15',
      duration: '7 Days',
      features: [
        '✅ 7 days trading',
        '✅ All symbols supported',
        '✅ Unlimited trades',
        '✅ Email support',
        '✅ Real-time alerts'
      ],
      popular: false
    },
    {
      id: 'monthly',
      name: 'Monthly Plan',
      price: '$50',
      duration: '30 Days',
      features: [
        '✅ 30 days trading',
        '✅ All symbols supported',
        '✅ Unlimited trades',
        '✅ Priority support',
        '✅ Advanced analytics',
        '✅ Risk management tools'
      ],
      popular: true
    },
    {
      id: 'quarterly',
      name: 'Quarterly Plan',
      price: '$135',
      duration: '90 Days',
      features: [
        '✅ 90 days trading',
        '✅ All symbols supported',
        '✅ Unlimited trades',
        '✅ VIP support',
        '✅ Advanced analytics',
        '✅ Custom strategies',
        '💰 Save $15 (10% off)'
      ],
      popular: false
    },
    {
      id: 'yearly',
      name: 'Yearly VIP',
      price: '$500',
      duration: '365 Days',
      features: [
        '✅ Full year access',
        '✅ All symbols + Crypto',
        '✅ Unlimited everything',
        '✅ 24/7 VIP support',
        '✅ Custom strategies',
        '✅ 1-on-1 coaching session',
        '✅ API access',
        '💰 Save $100 (17% off)'
      ],
      popular: false
    }
  ];

  const handleSelectPlan = async (planId) => {
    if (loading) return;
    
    setLoading(true);
    try {
      await subscriptionAPI.createSubscription(planId, 'free'); // In production, integrate payment gateway
      alert(`✅ ${plans.find(p => p.id === planId).name} activated successfully!`);
      
      // Call onComplete to move to next step
      if (onComplete) {
        onComplete();
      }
    } catch (err) {
      alert(`❌ Error: ${err.response?.data?.detail || 'Failed to activate subscription'}`);
      console.error('Subscription error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="subscription-container">
      <div className="subscription-header">
        <h1>🎯 Choose Your Trading Plan</h1>
        <p>Select a plan that fits your trading goals</p>
      </div>

      <div className="plans-grid">
        {plans.map((plan) => (
          <div 
            key={plan.id} 
            className={`plan-card ${plan.popular ? 'popular' : ''} ${selectedPlan === plan.id ? 'selected' : ''}`}
          >
            {plan.popular && <div className="popular-badge">⭐ MOST POPULAR</div>}
            
            <h2>{plan.name}</h2>
            <div className="price">{plan.price}</div>
            <div className="duration">{plan.duration}</div>
            
            <ul className="features">
              {plan.features.map((feature, index) => (
                <li key={index}>{feature}</li>
              ))}
            </ul>
            
            <button 
              className={`select-btn ${selectedPlan === plan.id ? 'selected' : ''}`}
              onClick={() => handleSelectPlan(plan.id)}
              disabled={loading}
            >
              {loading ? '⏳ Processing...' : 'Select Plan'}
            </button>
          </div>
        ))}
      </div>

      <div className="subscription-footer">
        <p>💳 Secure payment processing</p>
        <p>🔒 Cancel anytime, no questions asked</p>
        <p>📧 Email us: support@smcbot.com</p>
      </div>
    </div>
  );
}

export default SubscriptionPlans;
