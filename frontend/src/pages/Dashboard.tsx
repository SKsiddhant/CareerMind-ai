import React, { useEffect, useState } from 'react';
import { api } from '../services/api';
import { ShieldCheck, Cpu, Zap, Users, Trophy, Download, ExternalLink, Play } from 'lucide-react';

const Dashboard: React.FC = () => {
  const [status, setStatus] = useState<string>('Connecting...');
  const [userId, setUserId] = useState<number | null>(null);
  const [historyCount, setHistoryCount] = useState<number>(0);
  const [eliteLeads, setEliteLeads] = useState<any[]>([]);
  const [hunting, setHunting] = useState(false);

  useEffect(() => {
    api.getStatus()
      .then(res => setStatus(res.data.message))
      .catch(() => setStatus('Backend Offline'));
    
    const savedId = localStorage.getItem('careermind_user_id');
    if (savedId) {
      setUserId(parseInt(savedId));
      fetchHistory(parseInt(savedId));
    }
    fetchEliteLeads();
  }, []);

  const fetchHistory = async (id: number) => {
    try {
      const res = await api.getInterviewHistory(id);
      setHistoryCount(res.data.length);
    } catch (err) {
      console.error("Failed to fetch history", err);
    }
  };

  const fetchEliteLeads = async () => {
    try {
      const res = await api.getEliteLeads();
      setEliteLeads(res.data);
    } catch (err) {
      console.error("Failed to fetch elite leads", err);
    }
  };

  const startHunter = async () => {
    setHunting(true);
    try {
      await api.startHunter();
      alert("Autonomous Hunter deployed! It will scout for elite roles 24/7.");
    } catch (err) {
      alert("Hunter deployment failed.");
    } finally {
      setHunting(false);
    }
  };

  const syncProfile = async () => {
    try {
      const res = await api.createUser("Siddhant Kothiya", "siddhant@example.com", {
        skills: ["Python", "C++", "RAG", "LangChain"],
        experience: ["SDE Intern at Bluestock Fintech"]
      });
      const newId = res.data.user_id;
      setUserId(newId);
      localStorage.setItem('careermind_user_id', newId.toString());
      alert("Profile Synced to PostgreSQL Persistence Layer!");
    } catch (err) {
      alert("Sync failed. Ensure backend is running.");
    }
  };

  const stats = [
    { label: 'System Status', value: status, icon: <ShieldCheck className="text-primary" /> },
    { label: 'Active Agents', value: '5', icon: <Cpu /> },
    { label: 'Elite Leads', value: eliteLeads.length.toString(), icon: <Trophy className="text-secondary" /> },
    { label: 'Interview History', value: historyCount.toString(), icon: <Zap /> },
  ];

  return (
    <div>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <h1 style={{ fontSize: '2.5rem', fontWeight: 800 }}>
            Welcome back, <span className="text-gradient">Siddhant</span>
          </h1>
          <p style={{ color: 'var(--text-muted)' }}>CareerMind AI is optimized and patrolling for opportunities.</p>
        </div>
        <button className="btn-primary" onClick={startHunter} disabled={hunting} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', background: 'var(--secondary-color)', color: 'white' }}>
          <Play size={16} /> {hunting ? 'Deploying...' : 'Deploy Autonomous Hunter'}
        </button>
      </header>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1.5rem', marginBottom: '3rem' }}>
        {stats.map((stat, i) => (
          <div key={i} className="cyber-card" style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
            <div style={{ padding: '0.75rem', background: 'rgba(0, 242, 255, 0.1)', borderRadius: '8px', color: 'var(--primary-color)' }}>
              {stat.icon}
            </div>
            <div>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.25rem' }}>{stat.label}</p>
              <p style={{ fontSize: '1.1rem', fontWeight: 700 }}>{stat.value}</p>
            </div>
          </div>
        ))}
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: '2rem' }}>
        <section className="cyber-card">
          <h2 style={{ marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
            <Trophy className="text-secondary" /> Battle-Ready Opportunities
          </h2>
          {eliteLeads.length > 0 ? (
            <div style={{ display: 'grid', gap: '1rem' }}>
              {eliteLeads.map((lead, i) => (
                <div key={i} style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', border: '1px solid var(--border-color)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div>
                    <h3 style={{ fontSize: '1rem', marginBottom: '0.25rem' }}>{lead.title}</h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>{lead.company}</p>
                  </div>
                  <div style={{ display: 'flex', gap: '0.75rem' }}>
                    <button 
                      onClick={() => window.open(`http://127.0.0.1:8002${lead.battle_card.resume_url}`, '_blank')}
                      style={{ background: 'transparent', border: '1px solid var(--primary-color)', color: 'var(--primary-color)', padding: '0.4rem 0.8rem', borderRadius: '4px', cursor: 'pointer', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}
                    >
                      <Download size={14} /> Resume
                    </button>
                    <a href={lead.url} target="_blank" rel="noreferrer" style={{ background: 'var(--primary-color)', color: 'black', padding: '0.4rem 0.8rem', borderRadius: '4px', textDecoration: 'none', fontSize: '0.8rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      Apply <ExternalLink size={14} />
                    </a>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p style={{ color: 'var(--text-muted)', fontStyle: 'italic' }}>No elite matches found yet. Deploy the hunter to start the search.</p>
          )}
        </section>

        <section className="cyber-card" style={{ borderLeft: '4px solid var(--primary-color)' }}>
          <h2 style={{ marginBottom: '1rem' }}>Next Actions</h2>
          <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem', fontSize: '0.9rem' }}>
            Your RAG pipeline is fully synced. Sync your profile to the database to track your progress across sessions.
          </p>
          <div style={{ display: 'grid', gap: '1rem' }}>
            <button className="btn-primary" onClick={syncProfile}>
              {userId ? 'Profile Synced' : 'Sync Profile to DB'}
            </button>
            <button style={{ border: '1px solid var(--border-color)', padding: '0.75rem 1.5rem', borderRadius: '4px', background: 'transparent', color: 'white', cursor: 'pointer' }}>
              View Recent Evaluations
            </button>
          </div>
        </section>
      </div>
    </div>
  );
};

export default Dashboard;
