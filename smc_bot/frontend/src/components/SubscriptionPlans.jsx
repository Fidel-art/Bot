import React, { useState } from 'react';
import { subscriptionAPI } from '../services/api';
import './SubscriptionPlans.css';

const PAYMENT_METHODS = {
  paypal: { name: 'PayPal', icon: '💳', description: 'Pay with PayPal or Credit Card' },
  mpesa: { name: 'M-Pesa', icon: '📱', description: 'Pay with M-Pesa (Kenya)' },
  card: { name: 'Credit/Debit Card', icon: '💳', description: 'Pay with Visa, Mastercard, etc.' },
};

function SubscriptionPlans({ onComplete }) {
  const [loading, setLoading] = useState(false);
  const [selectedPlan, setSelectedPlan] = useState(null);
  const [showPayment, setShowPayment] = useState(false);
  const [selectedMethod, setSelectedMethod] = useState(null);
  const [paymentForm, setPaymentForm] = useState({});
  const [paymentStep, setPaymentStep] = useState('plan'); // plan -> method -> form -> processing -> done

  const plans = [
    {
      id: 'free',
      name: 'Free Trial',
      price: '$0',
      period: '',
      duration: '7 Days',
      features: [
        '✅ 7 days full access',
        '✅ All trading features',
        '✅ Up to 3 trades per day',
        '✅ All major pairs + XAUUSD',
        '✅ Basic support',
      ],
      popular: false,
      color: '#6b7280',
    },
    {
      id: 'weekly',
      name: 'Weekly Plan',
      price: '$29',
      period: '/week',
      duration: '7 Days',
      features: [
        '✅ 7 days trading',
        '✅ All symbols supported',
        '✅ Unlimited trades',
        '✅ Email support',
        '✅ Real-time alerts',
        '✅ Multi-symbol analysis',
      ],
      popular: false,
      color: '#f59e0b',
    },
    {
      id: 'monthly',
      name: 'Monthly Plan',
      price: '$99',
      period: '/month',
      duration: '30 Days',
      features: [
        '✅ 30 days trading',
        '✅ All symbols supported',
        '✅ Unlimited trades',
        '✅ Priority support',
        '✅ Advanced analytics',
        '✅ Risk management tools',
        '✅ Multi-timeframe analysis',
      ],
      popular: true,
      color: '#10b981',
    },
    {
      id: 'quarterly',
      name: 'Quarterly Plan',
      price: '$249',
      period: '/quarter',
      duration: '90 Days',
      features: [
        '✅ 90 days trading',
        '✅ All symbols supported',
        '✅ Unlimited trades',
        '✅ VIP support',
        '✅ Advanced analytics',
        '✅ Custom strategies',
        '💰 Save $48 (16% off)',
      ],
      popular: false,
      color: '#3b82f6',
    },
    {
      id: 'yearly',
      name: 'Yearly VIP',
      price: '$799',
      period: '/year',
      duration: '365 Days',
      features: [
        '✅ Full year access',
        '✅ All symbols + Crypto',
        '✅ Unlimited everything',
        '✅ 24/7 VIP support',
        '✅ Custom strategies',
        '✅ 1-on-1 coaching session',
        '✅ API access',
        '💰 Save $389 (32% off)',
      ],
      popular: false,
      color: '#8b5cf6',
    },
    {
      id: 'lifetime',
      name: 'Lifetime Access',
      price: '$2,499',
      period: ' once',
      duration: 'Forever',
      features: [
        '✅ Lifetime access',
        '✅ All features forever',
        '✅ All symbols',
        '✅ VIP support forever',
        '✅ All future updates',
        '✅ Priority feature requests',
        '✅ 1-on-1 coaching',
        '💰 Best value - pay once',
      ],
      popular: false,
      color: '#ef4444',
    },
  ];

  const handleSelectPlan = (planId) => {
    setSelectedPlan(planId);
    setSelectedMethod(null);
    setPaymentForm({});
    
    if (planId === 'free') {
      // Free trial - activate directly
      handlePaymentComplete(planId, 'free', null);
    } else {
      setShowPayment(true);
      setPaymentStep('method');
    }
  };

  const handleMethodSelect = (method) => {
    setSelectedMethod(method);
    setPaymentStep('form');
  };

  const handleFormChange = (field, value) => {
    setPaymentForm(prev => ({ ...prev, [field]: value }));
  };

  const handleSubmitPayment = async () => {
    if (loading) return;
    setLoading(true);
    setPaymentStep('processing');
    
    try {
      const response = await subscriptionAPI.processPayment(selectedPlan, selectedMethod, JSON.stringify(paymentForm));
      
      if (response.data.success) {
        setPaymentStep('done');
        setTimeout(() => {
          if (onComplete) onComplete();
        }, 2000);
      }
    } catch (err) {
      alert(`❌ Payment failed: ${err.response?.data?.detail || 'Please try again'}`);
      setPaymentStep('form');
    } finally {
      setLoading(false);
    }
  };

  const handlePaymentComplete = async (planId, method, details) => {
    setLoading(true);
    try {
      await subscriptionAPI.createSubscription(planId, method);
      if (onComplete) onComplete();
    } catch (err) {
      alert(`❌ Error: ${err.response?.data?.detail || 'Failed to activate subscription'}`);
    } finally {
      setLoading(false);
    }
  };

  const renderPaymentForm = () => {
    const method = PAYMENT_METHODS[selectedMethod];
    if (!method) return null;

    return (
      <div className="payment-form-container">
        <button className="back-btn" onClick={() => setPaymentStep('method')}>← Back</button>
        <h2>💳 {method.name} Payment</h2>
        <p className="payment-desc">{method.description}</p>

        {selectedMethod === 'paypal' && (
          <div className="payment-form">
            <p className="payment-info">You will be redirected to PayPal to complete payment of <strong>${plans.find(p => p.id === selectedPlan)?.price}</strong>.</p>
            <label>PayPal Email</label>
            <input type="email" placeholder="your@email.com" value={paymentForm.email || ''} onChange={e => handleFormChange('email', e.target.value)} />
            <button className="pay-btn" onClick={handleSubmitPayment} disabled={loading}>
              {loading ? '⏳ Processing...' : `Pay $${plans.find(p => p.id === selectedPlan)?.price} with PayPal`}
            </button>
          </div>
        )}

        {selectedMethod === 'mpesa' && (
          <div className="payment-form">
            <p className="payment-info">Enter your M-Pesa phone number to receive a payment request of <strong>${plans.find(p => p.id === selectedPlan)?.price}</strong> (KES equivalent).</p>
            <label>M-Pesa Phone Number</label>
            <input type="tel" placeholder="254712345678" value={paymentForm.phone || ''} onChange={e => handleFormChange('phone', e.target.value)} />
            <label>M-Pesa Name</label>
            <input type="text" placeholder="Full name on M-Pesa" value={paymentForm.name || ''} onChange={e => handleFormChange('name', e.target.value)} />
            <button className="pay-btn mpesa-btn" onClick={handleSubmitPayment} disabled={loading}>
              {loading ? '⏳ Processing...' : `💰 Pay with M-Pesa`}
            </button>
          </div>
        )}

        {selectedMethod === 'card' && (
          <div className="payment-form">
            <p className="payment-info">Enter your card details to pay <strong>${plans.find(p => p.id === selectedPlan)?.price}</strong>.</p>
            <label>Card Number</label>
            <input type="text" placeholder="1234 5678 9012 3456" maxLength="19" value={paymentForm.cardNumber || ''} onChange={e => handleFormChange('cardNumber', e.target.value)} />
            <div className="card-row">
              <div>
                <label>Expiry</label>
                <input type="text" placeholder="MM/YY" maxLength="5" value={paymentForm.expiry || ''} onChange={e => handleFormChange('expiry', e.target.value)} />
              </div>
              <div>
                <label>CVV</label>
                <input type="text" placeholder="123" maxLength="4" value={paymentForm.cvv || ''} onChange={e => handleFormChange('cvv', e.target.value)} />
              </div>
            </div>
            <label>Cardholder Name</label>
            <input type="text" placeholder="John Doe" value={paymentForm.cardholderName || ''} onChange={e => handleFormChange('cardholderName', e.target.value)} />
            <button className="pay-btn card-btn" onClick={handleSubmitPayment} disabled={loading}>
              {loading ? '⏳ Processing...' : `💳 Pay $${plans.find(p => p.id === selectedPlan)?.price}`}
            </button>
          </div>
        )}
      </div>
    );
  };

  const renderPaymentMethods = () => (
    <div className="payment-methods-container">
      <button className="back-btn" onClick={() => { setShowPayment(false); setPaymentStep('plan'); }}>← Back to Plans</button>
      <h2>💳 Choose Payment Method</h2>
      <p className="payment-desc">Select how you would like to pay for the <strong>{plans.find(p => p.id === selectedPlan)?.name}</strong></p>
      <p className="payment-amount">Amount: <strong>${plans.find(p => p.id === selectedPlan)?.price}</strong></p>

      <div className="payment-methods-grid">
        {Object.entries(PAYMENT_METHODS).map(([key, method]) => (
          <div key={key} className={`payment-method-card ${selectedMethod === key ? 'selected' : ''}`} onClick={() => handleMethodSelect(key)}>
            <span className="method-icon">{method.icon}</span>
            <div>
              <h3>{method.name}</h3>
              <p>{method.description}</p>
            </div>
            <span className="select-indicator">{selectedMethod === key ? '✓' : '→'}</span>
          </div>
        ))}
      </div>
    </div>
  );

  const renderProcessing = () => (
    <div className="payment-processing">
      <div className="spinner"></div>
      <h2>⏳ Processing Payment...</h2>
      <p>Please wait while we process your payment via {PAYMENT_METHODS[selectedMethod]?.name}</p>
    </div>
  );

  const renderDone = () => (
    <div className="payment-done">
      <div className="success-icon">✅</div>
      <h2>Payment Successful!</h2>
      <p>Your {plans.find(p => p.id === selectedPlan)?.name} has been activated.</p>
      <p>Redirecting to setup...</p>
    </div>
  );

  if (showPayment) {
    if (paymentStep === 'method') return <div className="subscription-container">{renderPaymentMethods()}</div>;
    if (paymentStep === 'form') return <div className="subscription-container">{renderPaymentForm()}</div>;
    if (paymentStep === 'processing') return <div className="subscription-container">{renderProcessing()}</div>;
    if (paymentStep === 'done') return <div className="subscription-container">{renderDone()}</div>;
  }

  return (
    <div className="subscription-container">
      <div className="subscription-header">
        <h1>🎯 Choose Your Trading Plan</h1>
        <p>Select a plan that fits your trading goals. All plans include multi-symbol support.</p>
      </div>

      <div className="plans-grid">
        {plans.map((plan) => (
          <div 
            key={plan.id} 
            className={`plan-card ${plan.popular ? 'popular' : ''} ${selectedPlan === plan.id ? 'selected' : ''}`}
            style={{ '--accent': plan.color }}
          >
            {plan.popular && <div className="popular-badge">⭐ MOST POPULAR</div>}
            
            <h2>{plan.name}</h2>
            <div className="price">
              {plan.price}
              {plan.period && <span className="period">{plan.period}</span>}
            </div>
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
              {loading ? '⏳ Processing...' : plan.id === 'free' ? 'Start Free Trial' : 'Select Plan'}
            </button>
          </div>
        ))}
      </div>

      <div className="subscription-footer">
        <p>🔒 Secure payment processing via PayPal, M-Pesa, or Card</p>
        <p>📧 Email us: support@smcbot.com</p>
      </div>
    </div>
  );
}

export default SubscriptionPlans;
