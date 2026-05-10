import React, { useState } from 'react';
import { api } from '../services/api';
import { FileCode, Target, Sparkles, FileText, CheckCircle2, AlertTriangle, RefreshCw, Upload, ShieldAlert, Hammer, GraduationCap, Briefcase } from 'lucide-react';

const ResumeTailor: React.FC = () => {
  const [query, setQuery] = useState('');
  const [strategies, setStrategies] = useState<any[]>([]);
  const [analysis, setAnalysis] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isAuditMode, setIsAuditMode] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    setAnalysis(null);
    try {
      const res = await api.generateStrategy(query);
      setStrategies(res.data.strategies);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setLoading(true);
    setStrategies([]);
    try {
      const res = await api.analyzeResume(file);
      setAnalysis(res.data);
    } catch (err) {
      console.error(err);
      alert("Resume analysis failed.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Resume <span className="text-gradient">Tailor</span></h1>
          <p style={{ color: 'var(--text-muted)' }}>Ultra-precision resume engineering and ruthless auditing.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '8px' }}>
          <button 
            onClick={() => setIsAuditMode(false)}
            className={!isAuditMode ? 'btn-primary' : ''}
            style={{ padding: '0.4rem 1rem', fontSize: '0.8rem', borderRadius: '4px', border: 'none', cursor: 'pointer', background: !isAuditMode ? '' : 'transparent' }}
          >
            Tailor Mode
          </button>
          <button 
            onClick={() => setIsAuditMode(true)}
            className={isAuditMode ? 'btn-primary' : ''}
            style={{ padding: '0.4rem 1rem', fontSize: '0.8rem', borderRadius: '4px', border: 'none', cursor: 'pointer', background: isAuditMode ? '' : 'transparent' }}
          >
            Ruthless Audit
          </button>
        </div>
      </header>

      <div className="cyber-card" style={{ marginBottom: '2rem' }}>
        {!isAuditMode ? (
          <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '1rem' }}>
            <input 
              type="text" 
              placeholder="Target role or company (e.g., AI Engineer at OpenAI)..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ flex: 1 }}
            />
            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? 'Analyzing...' : 'Generate Elite Strategy'}
            </button>
          </form>
        ) : (
          <div style={{ textAlign: 'center', padding: '1rem' }}>
            <label style={{ cursor: 'pointer', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1rem' }}>
              <div style={{ padding: '2rem', border: '2px dashed var(--border-color)', borderRadius: '8px', width: '100%', transition: 'all 0.3s ease' }}>
                <Upload size={48} style={{ opacity: 0.5, marginBottom: '0.5rem' }} />
                <p style={{ fontWeight: 600 }}>{loading ? 'RUNNING RUTHLESS AUDIT...' : 'Upload Resume PDF for Instant Feedback'}</p>
                <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)' }}>Our Head of Talent agent will audit your profile ruthlessly.</p>
              </div>
              <input type="file" accept=".pdf" onChange={handleFileUpload} style={{ display: 'none' }} disabled={loading} />
            </label>
          </div>
        )}
      </div>

      <div style={{ display: 'grid', gap: '2rem' }}>
        {/* Audit Results */}
        {analysis && (
          <div className="cyber-card" style={{ borderLeft: '4px solid var(--secondary-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', marginBottom: '0.25rem' }}>Audit Result</h2>
                <p style={{ color: 'var(--text-muted)' }}>Perspective: Head of Talent (Tier-1 AI Lab)</p>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1.5rem' }}>
                {analysis.reconstructed_resume_url && (
                  <button 
                    onClick={() => window.open(`http://127.0.0.1:8002${analysis.reconstructed_resume_url}`, '_blank')}
                    className="btn-primary" 
                    style={{ background: '#00ff7f', color: 'black', display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.75rem 1.5rem' }}
                  >
                    <Download size={20} /> Download AI-Edited Resume
                  </button>
                )}
                <div style={{ textAlign: 'right' }}>
                  <p style={{ fontSize: '0.75rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Profile Strength</p>
                  <div style={{ fontSize: '2rem', fontWeight: 900, color: 'var(--secondary-color)' }}>{analysis.overall_score}/10</div>
                </div>
              </div>
            </div>

            <div style={{ padding: '1.5rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '8px', marginBottom: '2rem', border: '1px solid var(--border-color)' }}>
              <h3 style={{ fontSize: '0.9rem', color: 'var(--primary-color)', marginBottom: '0.75rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <ShieldAlert size={16} /> Executive Summary
              </h3>
              <p style={{ fontSize: '1rem', lineHeight: 1.6, fontStyle: 'italic' }}>"{analysis.summary}"</p>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
              <section>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--error-color, #ff4d4d)', marginBottom: '1rem', textTransform: 'uppercase', fontWeight: 800 }}>
                   Anti-Patterns & Mistakes
                </h3>
                <ul style={{ listStyle: 'none', display: 'grid', gap: '1rem' }}>
                  {analysis.anti_patterns && analysis.anti_patterns.map((item: string, i: number) => (
                    <li key={i} style={{ display: 'flex', gap: '0.75rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.8)' }}>
                      <AlertTriangle size={16} style={{ color: 'var(--error-color, #ff4d4d)', flexShrink: 0 }} /> {item}
                    </li>
                  ))}
                  {analysis.mistakes && analysis.mistakes.map((item: string, i: number) => (
                    <li key={i} style={{ display: 'flex', gap: '0.75rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.8)' }}>
                      <AlertTriangle size={16} style={{ color: 'var(--error-color, #ff4d4d)', flexShrink: 0 }} /> {item}
                    </li>
                  ))}
                </ul>
              </section>
              <section>
                <h3 style={{ fontSize: '0.9rem', color: '#ffcc00', marginBottom: '1rem', textTransform: 'uppercase', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                   <Hammer size={16} /> Critical Edits
                </h3>
                <ul style={{ listStyle: 'none', display: 'grid', gap: '0.75rem' }}>
                  {analysis.critical_edits && analysis.critical_edits.map((item: string, i: number) => (
                    <li key={i} style={{ display: 'flex', gap: '0.75rem', fontSize: '0.9rem', color: 'rgba(255,255,255,0.9)' }}>
                      <div style={{ minWidth: '4px', height: '4px', borderRadius: '50%', background: '#ffcc00', marginTop: '0.5rem' }}></div>
                      {item}
                    </li>
                  ))}
                </ul>
              </section>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem', marginBottom: '2rem' }}>
              <section className="cyber-card" style={{ background: 'rgba(0, 242, 255, 0.02)' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--primary-color)', marginBottom: '1rem', textTransform: 'uppercase', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                   <GraduationCap size={16} /> Learning Roadmap
                </h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {analysis.learning_roadmap && analysis.learning_roadmap.map((item: any, i: number) => (
                    <div key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.75rem' }}>
                      <p style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.25rem' }}>{item.topic}</p>
                      <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{item.resources}</p>
                    </div>
                  ))}
                </div>
              </section>
              <section className="cyber-card" style={{ background: 'rgba(255, 0, 255, 0.02)' }}>
                <h3 style={{ fontSize: '0.9rem', color: 'var(--secondary-color)', marginBottom: '1rem', textTransform: 'uppercase', fontWeight: 800, display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                   <Briefcase size={16} /> Recommended Projects
                </h3>
                <div style={{ display: 'grid', gap: '1rem' }}>
                  {analysis.recommended_projects && analysis.recommended_projects.map((item: any, i: number) => (
                    <div key={i} style={{ borderBottom: '1px solid rgba(255,255,255,0.05)', paddingBottom: '0.75rem' }}>
                      <p style={{ fontSize: '0.9rem', fontWeight: 700, marginBottom: '0.25rem' }}>{item.name}</p>
                      <p style={{ fontSize: '0.8rem', opacity: 0.8, marginBottom: '0.25rem' }}>{item.description}</p>
                      <p style={{ fontSize: '0.75rem', fontStyle: 'italic', color: 'var(--secondary-color)' }}>Why: {item.reasoning}</p>
                    </div>
                  ))}
                </div>
              </section>
            </div>

            <section>
              <h3 style={{ fontSize: '0.9rem', color: 'var(--primary-color)', marginBottom: '1.25rem', textTransform: 'uppercase', fontWeight: 800 }}>
                <RefreshCw size={16} style={{ verticalAlign: 'middle', marginRight: '0.5rem' }} /> Elite Rewrites
              </h3>
              <div style={{ display: 'grid', gap: '1rem' }}>
                {analysis.elite_rewrites && analysis.elite_rewrites.map((item: any, i: number) => (
                  <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', padding: '1.25rem', background: 'rgba(255,255,255,0.02)', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
                    <div>
                      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.5rem', textTransform: 'uppercase' }}>Original</p>
                      <p style={{ fontSize: '0.85rem', opacity: 0.6 }}>{item.original}</p>
                    </div>
                    <div>
                      <p style={{ fontSize: '0.7rem', color: 'var(--secondary-color)', marginBottom: '0.5rem', textTransform: 'uppercase', fontWeight: 800 }}>Elite Version</p>
                      <p style={{ fontSize: '0.9rem', fontWeight: 500 }}>{item.rewrite}</p>
                    </div>
                  </div>
                ))}
              </div>
            </section>
          </div>
        )}

        {/* Strategy Results */}
        {strategies.map((strat, i) => (
          <div key={i} className="cyber-card" style={{ position: 'relative', overflow: 'hidden' }}>
            <div style={{ position: 'absolute', top: 0, right: 0, padding: '1rem', background: 'rgba(255, 0, 255, 0.1)', color: 'var(--secondary-color)', fontWeight: 800 }}>
              {strat.match_score}% MATCH
            </div>

            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1.5rem' }}>
              <h2 style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                <Target className="text-primary" /> {strat.role} at {strat.company}
              </h2>
              {strat.resume_url && (
                <button 
                  onClick={() => window.open(`http://127.0.0.1:8002${strat.resume_url}`, '_blank')}
                  className="btn-primary" 
                  style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem 1rem', fontSize: '0.85rem' }}
                >
                  <FileText size={16} /> Download Tailored Resume
                </button>
              )}
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '2rem' }}>
              <section>
                <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--primary-color)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                   Gap Analysis
                </h3>
                <ul style={{ listStyle: 'none', display: 'grid', gap: '0.75rem' }}>
                  {strat.gap_analysis.map((gap: string, j: number) => (
                    <li key={j} style={{ display: 'flex', alignItems: 'flex-start', gap: '0.75rem', fontSize: '0.9rem' }}>
                      <CheckCircle2 size={16} style={{ marginTop: '0.2rem', color: 'var(--text-muted)' }} />
                      {gap}
                    </li>
                  ))}
                </ul>
              </section>

              <section>
                <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--secondary-color)', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                   Outreach Hook
                </h3>
                <div style={{ padding: '1rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '4px', fontStyle: 'italic', borderLeft: '2px solid var(--secondary-color)' }}>
                  "{strat.outreach_hook}"
                </div>
              </section>
            </div>

            <div style={{ marginTop: '2rem' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '1rem', color: 'var(--primary-color)', textTransform: 'uppercase' }}>
                <Sparkles size={16} /> Optimized Bullets
              </h3>
              <div style={{ display: 'grid', gap: '1rem' }}>
                {strat.optimized_bullets.map((bullet: string, j: number) => (
                  <div key={j} className="cyber-card" style={{ background: 'rgba(0, 242, 255, 0.02)', fontSize: '0.9rem' }}>
                    {bullet}
                  </div>
                ))}
              </div>
            </div>

            <div style={{ marginTop: '2rem', padding: '1.5rem', background: 'rgba(255, 255, 255, 0.05)', borderRadius: '8px' }}>
              <h3 style={{ fontSize: '1rem', marginBottom: '0.5rem' }}>Weekend Project: {strat.weekend_project.name}</h3>
              <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>{strat.weekend_project.description}</p>
              <div style={{ display: 'flex', gap: '0.5rem' }}>
                {strat.weekend_project.tech_stack.map((tech: string, j: number) => (
                  <span key={j} style={{ fontSize: '0.7rem', background: 'var(--bg-color)', padding: '0.25rem 0.5rem', border: '1px solid var(--border-color)', borderRadius: '4px' }}>
                    {tech}
                  </span>
                ))}
              </div>
            </div>
          </div>
        ))}

        {!loading && !analysis && strategies.length === 0 && (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
            <FileCode size={48} style={{ marginBottom: '1rem', opacity: 0.2 }} />
            <p>Select a mode above to begin your profile optimization.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default ResumeTailor;
