import axios from 'axios';

const API_BASE_URL = 'http://127.0.0.1:8002';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  // Job Intelligence
  gatherIntelligence: (query: string) => 
    apiClient.post('/intelligence/gather', { query }),
  
  searchJobs: (query: string, k: number = 5) => 
    apiClient.get(`/jobs/search`, { params: { query, k } }),

  // Resume Tailor
  generateStrategy: (query: string) => 
    apiClient.post('/tailor/strategy', { query }),

  analyzeResume: (resumeFile: File) => {
    const formData = new FormData();
    formData.append('resume', resumeFile);
    return apiClient.post('/tailor/analyze', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Interview Coach
  generateQuestion: (jobTitle: string) => 
    apiClient.get('/interview/generate-question', { params: { job_title: jobTitle } }),

  evaluateInterview: (jobTitle: string, question: string, answer: string) => 
    apiClient.post('/interview/evaluate', { job_title: jobTitle, question, answer }),

  voiceTurn: (jobTitle: string, question: string, audioBlob: Blob) => {
    const formData = new FormData();
    formData.append('job_title', jobTitle);
    formData.append('question', question);
    formData.append('audio', audioBlob, 'answer.webm');
    return apiClient.post('/interview/voice-turn', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
  },

  // Salary Negotiator
  negotiateSalary: (company: string, role: string, matchScore: number) => 
    apiClient.post('/salary/negotiate', { company, role, match_score: matchScore }),

  // User Management
  createUser: (name: string, email: string, profileData: any) => 
    apiClient.post('/users/', { name, email, profile_data: profileData }),

  getInterviewHistory: (userId: number) => 
    apiClient.get(`/history/interviews/${userId}`),

  activateWarRoom: (jobTitle: string, company: string, jobContent: string) => 
    apiClient.post('/strategy/war-room', { job_title: jobTitle, company, job_content: jobContent }),

  // Autonomous Hunter
  startHunter: () => apiClient.post('/hunter/start'),
  getEliteLeads: () => apiClient.get('/hunter/elite-leads'),

  // Root status
  getStatus: () => apiClient.get('/'),
};

export default api;
