import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import MainLayout from './components/MainLayout';
import Dashboard from './pages/Dashboard';
import JobIntelligence from './pages/JobIntelligence';
import ResumeTailor from './pages/ResumeTailor';
import InterviewCoach from './pages/InterviewCoach';
import SalaryNegotiator from './pages/SalaryNegotiator';

const App: React.FC = () => {
  return (
    <Router>
      <MainLayout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/intelligence" element={<JobIntelligence />} />
          <Route path="/tailor" element={<ResumeTailor />} />
          <Route path="/interview" element={<InterviewCoach />} />
          <Route path="/negotiate" element={<SalaryNegotiator />} />
        </Routes>
      </MainLayout>
    </Router>
  );
};

export default App;
