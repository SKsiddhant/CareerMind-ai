import React, { useState, useRef } from 'react';
import { api } from '../services/api';
import { Mic2, MessageSquare, Award, AlertCircle, Quote, StopCircle, Volume2 } from 'lucide-react';

const InterviewCoach: React.FC = () => {
  const [formData, setFormData] = useState({ job_title: '', question: '', answer: '' });
  const [evaluation, setEvaluation] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [isVoiceMode, setIsVoiceMode] = useState(false);
  const [isRecording, setIsRecording] = useState(false);
  const [audioUrl, setAudioUrl] = useState<string | null>(null);
  const [statusText, setStatusText] = useState('');
  
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const chunksRef = useRef<Blob[]>([]);

  const handleGenerateQuestion = async () => {
    if (!formData.job_title) {
      alert("Please enter a Target Role first.");
      return;
    }
    setLoading(true);
    setStatusText('Generating elite question...');
    try {
      const res = await api.generateQuestion(formData.job_title);
      setFormData({ ...formData, question: res.data.question });
      if (res.data.audio_url) {
        const url = `http://127.0.0.1:8002${res.data.audio_url}`;
        const audio = new Audio(url);
        audio.play();
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
      setStatusText('');
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      chunksRef.current = [];

      mediaRecorder.ondataavailable = (e) => {
        if (e.data.size > 0) chunksRef.current.push(e.data);
      };

      mediaRecorder.onstop = async () => {
        const audioBlob = new Blob(chunksRef.current, { type: 'audio/webm' });
        handleVoiceSubmit(audioBlob);
      };

      mediaRecorder.start();
      setIsRecording(true);
    } catch (err) {
      console.error('Microphone access denied:', err);
    }
  };

  const stopRecording = () => {
    if (mediaRecorderRef.current) {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
    }
  };

  const handleVoiceSubmit = async (audioBlob: Blob) => {
    setLoading(true);
    try {
      const res = await api.voiceTurn(formData.job_title, formData.question, audioBlob);
      setEvaluation(res.data.evaluation);
      if (res.data.audio_url) {
        setAudioUrl(`http://127.0.0.1:8002${res.data.audio_url}`);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setAudioUrl(null);
    try {
      const res = await api.evaluateInterview(formData.job_title, formData.question, formData.answer);
      setEvaluation(res.data.evaluation);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div>
      <header style={{ marginBottom: '2rem', display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end' }}>
        <div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800 }}>Interview <span className="text-gradient">Coach</span></h1>
          <p style={{ color: 'var(--text-muted)' }}>Ruthless technical evaluation with Elite Neural Voice.</p>
        </div>
        <div style={{ display: 'flex', gap: '0.5rem', background: 'rgba(255,255,255,0.05)', padding: '0.5rem', borderRadius: '8px' }}>
          <button 
            onClick={() => setIsVoiceMode(false)}
            className={!isVoiceMode ? 'btn-primary' : ''}
            style={{ padding: '0.4rem 1rem', fontSize: '0.8rem', borderRadius: '4px', border: 'none', cursor: 'pointer', background: !isVoiceMode ? '' : 'transparent' }}
          >
            Text Mode
          </button>
          <button 
            onClick={() => setIsVoiceMode(true)}
            className={isVoiceMode ? 'btn-primary' : ''}
            style={{ padding: '0.4rem 1rem', fontSize: '0.8rem', borderRadius: '4px', border: 'none', cursor: 'pointer', background: isVoiceMode ? '' : 'transparent' }}
          >
            Voice Mode
          </button>
        </div>
      </header>

      {/* Elite Question Teleprompter */}
      {formData.question && (
        <section className="cyber-card" style={{ marginBottom: '2rem', border: '1px solid var(--primary-color)', background: 'rgba(0, 242, 255, 0.02)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '1rem' }}>
            <div className="pulse" style={{ width: '12px', height: '12px', background: 'var(--primary-color)', borderRadius: '50%' }}></div>
            <span style={{ fontSize: '0.75rem', fontWeight: 800, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'var(--primary-color)' }}>
              Agent Persona: Principal Engineer (Andrew)
            </span>
          </div>
          <h2 style={{ fontSize: '1.75rem', fontWeight: 700, lineHeight: 1.4, color: 'white' }}>
            {formData.question}
          </h2>
          {statusText && <p style={{ marginTop: '1rem', color: 'var(--primary-color)', fontSize: '0.9rem', fontStyle: 'italic' }}>{statusText}</p>}
        </section>
      )}

      <div style={{ display: 'grid', gridTemplateColumns: isVoiceMode ? '1fr' : '1fr 1fr', gap: '2rem' }}>
        <section>
          <div className="cyber-card">
            <h2 style={{ fontSize: '1.25rem', marginBottom: '1.5rem', display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
               Simulation Controls
            </h2>
            <form onSubmit={handleSubmit} style={{ display: 'grid', gap: '1.25rem' }}>
              <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Target Role</label>
                  <input 
                    type="text" 
                    placeholder="e.g. Senior AI Engineer" 
                    value={formData.job_title}
                    onChange={(e) => setFormData({...formData, job_title: e.target.value})}
                    style={{ width: '100%' }}
                  />
                </div>
                <div style={{ display: 'flex', alignItems: 'flex-end' }}>
                  <button 
                    type="button" 
                    onClick={handleGenerateQuestion}
                    className="btn-primary" 
                    style={{ width: '100%', height: '42px', background: 'rgba(255, 255, 255, 0.05)', color: 'white', border: '1px solid var(--border-color)' }}
                    disabled={loading}
                  >
                    {formData.question ? 'Regenerate Question' : 'Generate & Speak'}
                  </button>
                </div>
              </div>
              
              {!isVoiceMode ? (
                <div>
                  <label style={{ display: 'block', fontSize: '0.85rem', color: 'var(--text-muted)', marginBottom: '0.5rem' }}>Your Answer</label>
                  <textarea 
                    rows={6}
                    placeholder="Explain your approach..." 
                    value={formData.answer}
                    onChange={(e) => setFormData({...formData, answer: e.target.value})}
                    style={{ width: '100%', resize: 'none' }}
                  />
                  <button type="submit" className="btn-primary" disabled={loading} style={{ marginTop: '1.25rem', width: '100%' }}>
                    {loading ? 'Evaluating...' : 'Get Ruthless Feedback'}
                  </button>
                </div>
              ) : (
                <div style={{ textAlign: 'center', padding: '1rem 0' }}>
                  <div style={{ marginBottom: '2rem', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '1.5rem' }}>
                    {isRecording ? (
                      <div className="pulse" style={{ width: '100px', height: '100px', background: 'rgba(255, 0, 0, 0.1)', borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                        <button 
                          type="button"
                          onClick={stopRecording}
                          style={{ background: 'var(--error-color, #ff4d4d)', color: 'white', border: 'none', width: '70px', height: '70px', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', boxShadow: '0 0 20px rgba(255, 77, 77, 0.4)' }}
                        >
                          <StopCircle size={36} />
                        </button>
                      </div>
                    ) : (
                      <button 
                        type="button"
                        onClick={startRecording}
                        disabled={loading || !formData.question}
                        style={{ background: 'var(--primary-color)', color: 'black', border: 'none', width: '100px', height: '100px', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', opacity: (loading || !formData.question) ? 0.3 : 1, transition: 'all 0.3s ease', boxShadow: '0 0 20px rgba(0, 242, 255, 0.2)' }}
                      >
                        <Mic2 size={48} />
                      </button>
                    )}
                    <p style={{ color: isRecording ? 'var(--error-color, #ff4d4d)' : 'var(--text-muted)', fontWeight: 600 }}>
                      {isRecording ? 'RECORDING LIVE...' : loading ? 'TRANSCRIBING & ANALYZING...' : !formData.question ? 'Generate a question first' : 'Click to start speaking'}
                    </p>
                  </div>
                </div>
              )}
            </form>
          </div>
        </section>

        {/* Results section */}
        {(evaluation || !isVoiceMode) && (
          <section>
            {evaluation ? (
              <div className="cyber-card" style={{ borderLeft: '4px solid var(--primary-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem' }}>
                  <h2 style={{ fontSize: '1.25rem' }}>Evaluation Result</h2>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
                    {audioUrl && (
                      <button 
                        onClick={() => new Audio(audioUrl).play()}
                        style={{ background: 'rgba(0, 242, 255, 0.1)', color: 'var(--primary-color)', border: 'none', padding: '0.5rem', borderRadius: '50%', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center' }}
                        title="Play Audio Feedback"
                      >
                        <Volume2 size={20} />
                      </button>
                    )}
                    <div style={{ fontSize: '1.5rem', fontWeight: 900, color: 'var(--primary-color)' }}>{evaluation.total_score}/10</div>
                  </div>
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem', marginBottom: '2rem' }}>
                  {Object.entries(evaluation.scores || {}).map(([key, val]: any) => (
                    <div key={key} style={{ textAlign: 'center', padding: '0.75rem', background: 'rgba(255, 255, 255, 0.03)', borderRadius: '6px' }}>
                      <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'uppercase' }}>{key.replace('_', ' ')}</p>
                      <p style={{ fontSize: '1rem', fontWeight: 700 }}>{val}/10</p>
                    </div>
                  ))}
                </div>

                <div style={{ display: 'grid', gap: '1.5rem' }}>
                  <div>
                    <h3 style={{ fontSize: '0.9rem', color: 'var(--primary-color)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <MessageSquare size={14} /> Feedback
                    </h3>
                    <p style={{ fontSize: '0.9rem', lineHeight: 1.6 }}>{evaluation.feedback}</p>
                  </div>

                  {evaluation.mistakes && evaluation.mistakes.length > 0 && evaluation.mistakes[0] !== 'N/A' && (
                    <div style={{ padding: '1rem', background: 'rgba(255, 77, 77, 0.05)', borderRadius: '8px', borderLeft: '3px solid var(--error-color, #ff4d4d)' }}>
                      <h3 style={{ fontSize: '0.9rem', color: 'var(--error-color, #ff4d4d)', marginBottom: '0.75rem', fontWeight: 800, textTransform: 'uppercase' }}>
                         Mistakes Identified
                      </h3>
                      <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', display: 'grid', gap: '0.5rem' }}>
                        {evaluation.mistakes.map((m: string, idx: number) => <li key={idx} style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{m}</li>)}
                      </ul>
                    </div>
                  )}

                  {evaluation.corrections && evaluation.corrections.length > 0 && evaluation.corrections[0] !== 'N/A' && (
                    <div style={{ padding: '1rem', background: 'rgba(0, 255, 127, 0.05)', borderRadius: '8px', borderLeft: '3px solid #00ff7f' }}>
                      <h3 style={{ fontSize: '0.9rem', color: '#00ff7f', marginBottom: '0.75rem', fontWeight: 800, textTransform: 'uppercase' }}>
                         Required Corrections
                      </h3>
                      <ul style={{ paddingLeft: '1.25rem', fontSize: '0.85rem', display: 'grid', gap: '0.5rem' }}>
                        {evaluation.corrections.map((c: string, idx: number) => <li key={idx} style={{ color: 'rgba(255, 255, 255, 0.9)' }}>{c}</li>)}
                      </ul>
                    </div>
                  )}

                  <div>
                    <h3 style={{ fontSize: '0.9rem', color: 'var(--secondary-color)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>

                      <Award size={14} /> Seniority Signal (The Cheat Code)
                    </h3>
                    <div style={{ padding: '0.75rem', background: 'rgba(255, 0, 255, 0.05)', borderRadius: '4px', border: '1px dashed var(--secondary-color)', fontSize: '0.9rem' }}>
                      {evaluation.seniority_signal}
                    </div>
                  </div>

                  <div style={{ padding: '1rem', background: 'rgba(0, 242, 255, 0.05)', borderRadius: '8px' }}>
                    <h3 style={{ fontSize: '0.9rem', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <AlertCircle size={14} /> Curveball Follow-up
                    </h3>
                    <p style={{ fontSize: '0.9rem', fontStyle: 'italic' }}>{evaluation.curveball_question}</p>
                  </div>

                  <div>
                    <h3 style={{ fontSize: '0.9rem', color: 'var(--text-muted)', marginBottom: '0.5rem', display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                      <Quote size={14} /> Perfect Response
                    </h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.6 }}>{evaluation.ideal_answer}</p>
                  </div>
                </div>
              </div>
            ) : (
              <div style={{ height: '100%', display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', border: '2px dashed var(--border-color)', borderRadius: '8px' }}>
                <Mic2 size={48} style={{ marginBottom: '1rem', opacity: 0.1 }} />
                <p>Submit your answer for a GOATed evaluation.</p>
              </div>
            )}
          </section>
        )}
      </div>
      
      {audioUrl && isVoiceMode && (
        <audio autoPlay src={audioUrl} />
      )}
    </div>
  );
};

export default InterviewCoach;
