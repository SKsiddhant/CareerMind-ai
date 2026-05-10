import React, { useState } from 'react';
import { api } from '../services/api';
import { Search, Globe, Building2, MapPin, ExternalLink, Zap } from 'lucide-react';

const JobIntelligence: React.FC = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [gathering, setGathering] = useState(false);
  const [warRoomLoading, setWarRoomLoading] = useState<string | null>(null);

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);
    try {
      const res = await api.searchJobs(query);
      setResults(res.data.results);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleGather = async () => {
    if (!query) return;
    setGathering(true);
    try {
      await api.gatherIntelligence(query);
      alert('Intelligence gathering started in background.');
    } catch (err) {
      console.error(err);
    } finally {
      setGathering(false);
    }
  };

  const handleActivateWarRoom = async (job: any) => {
    setWarRoomLoading(job.metadata.url);
    try {
      const res = await api.activateWarRoom(job.metadata.title, job.metadata.company, job.content);
      console.log("Battle Card Generated:", res.data);
      alert(`🚩 WAR ROOM COMPLETE: Battle Card generated for ${job.metadata.company}. Check the console for details and your tailored resume!`);
      if (res.data.resume_url) {
        window.open(`http://127.0.0.1:8002${res.data.resume_url}`, '_blank');
      }
    } catch (err) {
      console.error(err);
      alert("War Room activation failed.");
    } finally {
      setWarRoomLoading(null);
    }
  };

  return (
    <div>
      <header style={{ marginBottom: '2rem' }}>
        <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Job <span className="text-gradient">Intelligence</span></h1>
        <p style={{ color: 'var(--text-muted)' }}>Discover hidden opportunities and hiring manager data.</p>
      </header>

      <div className="cyber-card" style={{ marginBottom: '2rem' }}>
        <form onSubmit={handleSearch} style={{ display: 'flex', gap: '1rem' }}>
          <div style={{ flex: 1, position: 'relative' }}>
            <Search size={18} style={{ position: 'absolute', left: '1rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
            <input 
              type="text" 
              placeholder="Search for roles (e.g., AI Engineer)..." 
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              style={{ width: '100%', paddingLeft: '2.75rem' }}
            />
          </div>
          <button type="submit" className="btn-primary" disabled={loading}>
            {loading ? 'Searching...' : 'Vector Search'}
          </button>
          <button type="button" onClick={handleGather} style={{ border: '1px solid var(--secondary-color)', color: 'var(--secondary-color)', padding: '0.75rem 1.5rem', borderRadius: '4px' }} disabled={gathering}>
            {gathering ? 'Launching...' : 'Trigger Scrape'}
          </button>
        </form>
      </div>

      <div style={{ display: 'grid', gap: '1rem' }}>
        {results.map((res, i) => (
          <div key={i} className="cyber-card" style={{ borderLeft: '2px solid var(--primary-color)' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '1rem' }}>
              <div>
                <h3 style={{ fontSize: '1.2rem', marginBottom: '0.25rem' }}>{res.metadata.title}</h3>
                <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><Building2 size={14} /> {res.metadata.company}</span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '0.25rem' }}><MapPin size={14} /> {res.metadata.location || 'Remote'}</span>
                </div>
              </div>
              <div style={{ textAlign: 'right' }}>
                <span style={{ background: 'rgba(0, 242, 255, 0.1)', color: 'var(--primary-color)', padding: '0.25rem 0.5rem', borderRadius: '4px', fontSize: '0.75rem', fontWeight: 600 }}>
                  {(res.relevance_score * 100).toFixed(0)}% Match
                </span>
                <a href={res.metadata.url} target="_blank" rel="noreferrer" style={{ display: 'block', marginTop: '0.5rem', color: 'var(--primary-color)', fontSize: '0.8rem' }}>
                   View Source <ExternalLink size={12} />
                </a>
              </div>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-color)', lineHeight: 1.6, opacity: 0.9, marginBottom: '1.5rem' }}>
              {res.content.substring(0, 300)}...
            </p>
            <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
              <button 
                onClick={() => handleActivateWarRoom(res)}
                className="btn-primary" 
                disabled={warRoomLoading === res.metadata.url}
                style={{ padding: '0.6rem 1.2rem', fontSize: '0.85rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}
              >
                <Zap size={14} />
                {warRoomLoading === res.metadata.url ? 'Deploying Agents...' : 'Activate War Room'}
              </button>
            </div>
          </div>
        ))}

        {!loading && results.length === 0 && (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-muted)' }}>
            <Globe size={48} style={{ marginBottom: '1rem', opacity: 0.2 }} />
            <p>Enter a query to search the indexed job database.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default JobIntelligence;
