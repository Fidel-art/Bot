import React, { useState, useEffect } from 'react';
import { subscriptionAPI } from '../services/api';
import SubscriptionPlans from './SubscriptionPlans';

function Subscription() {
  const [subscription, setSubscription] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showPlans, setShowPlans] = useState(false);

  useEffect(() => {
    loadSubscription();
  }, []);

  const loadSubscription = async () => {
    try {
      const response = await subscriptionAPI.getSubscription();
      setSubscription(response.data);
    } catch (err) {
      console.error('Failed to load subscription:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div className="loading">Loading subscription...</div>;

  if (showPlans || (!subscription?.has_subscription)) {
    return <SubscriptionPlans onComplete={() => { setShowPlans(false); loadSubscription(); }} />;
  }

  const sub = subscription.subscription;

  return (
    <div className="subscription-container" style={{ padding: '40px' }}>
      <div className="subscription-header">
        <h1>📋 My Subscription</h1>
      </div>
      <div style={{
        background: 'white',
        borderRadius: '15px',
        padding: '30px',
        maxWidth: '600px',
        margin: '0 auto',
        boxShadow: '0 10px 30px rgba(0,0,0,0.2)',
      }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2 style={{ margin: 0, color: '#333' }}>{sub.plan.toUpperCase()}</h2>
          <span style={{
            padding: '5px 15px',
            borderRadius: '20px',
            fontWeight: 'bold',
            fontSize: '14px',
            background: subscription.is_valid ? '#4caf50' : '#f44336',
            color: 'white',
          }}>
            {subscription.is_valid ? 'ACTIVE' : 'EXPIRED'}
          </span>
        </div>
        <p><strong>Amount:</strong> ${sub.amount}</p>
        {sub.payment_method && <p><strong>Paid via:</strong> {sub.payment_method.toUpperCase()}</p>}
        <p><strong>Expires:</strong> {sub.expiry_date}</p>
        <p><strong>Days remaining:</strong> {subscription.days_remaining}</p>
        <button
          onClick={() => setShowPlans(true)}
          style={{
            width: '100%',
            padding: '12px',
            background: '#667eea',
            color: 'white',
            border: 'none',
            borderRadius: '8px',
            fontSize: '16px',
            fontWeight: 'bold',
            cursor: 'pointer',
            marginTop: '20px',
          }}
        >
          Change Plan / Renew
        </button>
      </div>
    </div>
  );
}

export default Subscription;
