import React, { useState } from 'react';
import { api } from '../services/api';
import { DollarSign, Briefcase, TrendingUp, HelpCircle } from 'lucide-react';

const SalaryNegotiator: React.FC = () => {
  const [formData, setFormData] = useState({ company: '', role: '', match_score: 85 });
  const [strategy, setStrategy] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await api.negotiateSalary(formData.company, formData.role, formData.match_score);
      setStrategy(res.data.strategy);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Salary <span className="text-gradient">Negotiator</span></h1>
        <p style={{ color: 'var(--text-muted)' }}>Market-aware compensation strategy and psychological scripts.</p>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.5fr', gap: '2rem' }}>
        <section>
          <div className="cyber-card">
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
               Offer Details
            </h2>
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.25rem' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Company Name</label>
                <input 
                  type="text" 
                  placeholder="e.g. Google" 
                  value={formData.company}
                  onChange={(e) => setFormData({...formData, company: e.target.value})}
                  style={{ width: '100%' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Role</label>
                <input 
                  type="text" 
                  placeholder="e.g. SDE-3" 
                  value={formData.role}
                  onChange={(e) => setFormData({...formData, role: e.target.value})}
                  style={{ width: '100%' }}
                />
              </div>
              <div>
                <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Confidence/Match Score (0-100)</label>
                <input 
                  type="number" 
                  value={formData.match_score}
                  onChange={(e) => setFormData({...formData, match_score: parseInt(e.target.value)})}
                  style={{ width: '100%' }}
                />
              </div>
              <button type="submit" className="btn-primary" disabled={loading}>
                {loading ? 'Calculating...' : 'Generate Negotiation Strategy'}
              </button>
            </form>
          </div>
        </section>

        <section>
          {strategy ? (
            <div className="cyber-card" style={{ borderLeft: '4px solid var(--secondary-color)' }}>
              <div style={{ marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>Elite Strategy for {formData.company}</h2>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Target Range</p>
                    <p style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--primary-color)' }}>{strategy.market_range.min} - {strategy.market_range.max}</p>
                    <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Currency: {strategy.market_range.currency}</p>
                  </div>
                  <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
                    <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Psychological Stance</p>
                    <p style={{ fontSize: '1.1rem', fontWeight: 700 }}>{strategy.stance}</p>
                  </div>
                </div>
              </div>

              <div style={{ display: 'grid', gap: '1.5rem' }}>
                <div>
                  <h3 style={{ fontSize: '0.9rem', color: 'var(--primary-color)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <TrendingUp size={14} /> Leverage Points
                  </h3>
                  <ul style={{ listStyle: 'none', display: 'grid', gap: '0.5rem' }}>
                    {strategy.leverage_points.map((p: string, i: number) => (
                      <li key={i} style={{ fontSize: '0.9rem', display: 'flex', gap: '0.5rem' }}>
                        <span style={{ color: 'var(--primary-color)' }}>•</span> {p}
                      </li>
                    ))}
                  </ul>
                </div>

                <div>
                  <h3 style={{ fontSize: '0.9rem', color: 'var(--secondary-color)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <Briefcase size={14} /> Negotiation Script
                  </h3>
                  <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderLeft: '2px solid var(--secondary-color)', fontStyle: 'italic', fontSize: '0.9rem', lineHeight: 1.6 }}>
                    "{strategy.script}"
                  </div>
                </div>

                <div style={{ padding: '1rem', background: 'rgba(0, 242, 255, 0.05)', borderRadius: '8px' }}>
                  <h3 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                    <HelpCircle size={14} /> Potential Objection Handler
                  </h3>
                  <p style={{ fontSize: '0.9rem' }}><strong>Objection:</strong> {strategy.counter_objections[0].objection}</p>
                  <p style={{ fontSize: '0.9rem', marginTop: '0.5rem', color: 'var(--text-muted)' }}><strong>Response:</strong> {strategy.counter_objections[0].response}</p>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', border: '2px dashed var(--border-color)', borderRadius: '8px' }}>
              <DollarSign size={48} style={{ marginBottom: '1rem', opacity: 0.1 }} />
              <p>Calculate your unfair advantage in compensation.</p>
            </div>
          )}
        </section>
      </div>
    </div>
  );
};

export default SalaryNegotiator;
