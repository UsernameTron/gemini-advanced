import React, { useEffect, useState } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';

interface DiscScores {
  dominance: number;
  influence: number;
  steadiness: number;
  conscientiousness: number;
}

interface ProfileInterpretation {
  interpretations: {
    dominance: string;
    influence: string;
    steadiness: string;
    conscientiousness: string;
  };
  recommendedLevel: 'Level 1' | 'Level 2' | 'Level 3';
  profileSummary: string;
}

interface AssessmentResult {
  id: number;
  candidateName: string;
  positionLevel: string;
  completedAt: string;
  totalTimeMinutes: number;
  scores: DiscScores;
  interpretation: ProfileInterpretation;
}

const Results: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    // Fetch assessment results
    const fetchResults = async () => {
      try {
        // TODO: Replace with actual API call
        setTimeout(() => {
          // Mock data for display purposes
          const mockResult: AssessmentResult = {
            id: Number(id),
            candidateName: 'John Doe',
            positionLevel: 'Level 2',
            completedAt: '2023-03-15T11:15:00Z',
            totalTimeMinutes: 22,
            scores: {
              dominance: 4,
              influence: 7,
              steadiness: 9,
              conscientiousness: 10
            },
            interpretation: {
              interpretations: {
                dominance: 'Low dominance indicates a preference for collaborative decision making rather than taking charge.',
                influence: 'Moderate influence suggests a balanced approach to social interactions and team communication.',
                steadiness: 'High steadiness shows reliability, patience, and a methodical approach to work.',
                conscientiousness: 'High conscientiousness demonstrates attention to detail, analytical thinking, and procedural accuracy.'
              },
              recommendedLevel: 'Level 2',
              profileSummary: 'This profile shows a technician who excels in methodical problem solving and detail-oriented work. The high conscientiousness and steadiness scores indicate someone who works well with established procedures and maintains consistency in their approach. The moderate influence score suggests they can communicate effectively when needed, while the lower dominance indicates they may prefer following established protocols rather than creating new solutions.'
            }
          };

          setResult(mockResult);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load assessment results');
        setLoading(false);
      }
    };

    fetchResults();
  }, [id, navigate]);

  const handleDownloadPDF = () => {
    // TODO: Implement PDF generation and download
    alert('PDF download functionality will be implemented here');
  };

  const handleShareResults = () => {
    // TODO: Implement sharing functionality
    alert('Share functionality will be implemented here');
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glassmorphism p-8 text-center">
          <h2 className="text-h2 font-bold gradient-text mb-4">Loading Results</h2>
          <p className="text-text-secondary">Please wait while we load your assessment results...</p>
        </div>
      </div>
    );
  }

  if (error || !result) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glassmorphism p-8 text-center">
          <h2 className="text-h2 font-bold text-red-400 mb-4">Error</h2>
          <p className="text-text-secondary mb-6">{error || 'Results not found'}</p>
          <button
            onClick={() => navigate('/dashboard')}
            className="btn-primary"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  // Calculate maximum score for scaling the charts
  const maxScore = 15; // Assuming 15 questions total, with 1 point per question
  
  return (
    <div className="min-h-screen p-4 sm:p-6 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-h2 font-bold gradient-text">Assessment Results</h1>
          <Link 
            to="/dashboard"
            className="border border-primary-blue py-2 px-4 rounded-lg text-primary-blue font-medium hover:bg-primary-blue/10 transition-colors duration-300"
          >
            Back to Dashboard
          </Link>
        </header>
        
        {/* Summary Section */}
        <div className="glassmorphism p-6 mb-8">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
            <div>
              <h2 className="text-h3 font-medium text-white mb-4">Candidate Details</h2>
              <div className="space-y-3">
                <div className="flex justify-between border-b border-white/10 pb-2">
                  <span className="text-text-secondary">Name:</span>
                  <span className="text-white font-medium">{result.candidateName}</span>
                </div>
                <div className="flex justify-between border-b border-white/10 pb-2">
                  <span className="text-text-secondary">Assessment ID:</span>
                  <span className="text-white font-medium">{result.id}</span>
                </div>
                <div className="flex justify-between border-b border-white/10 pb-2">
                  <span className="text-text-secondary">Completed:</span>
                  <span className="text-white font-medium">{new Date(result.completedAt).toLocaleString()}</span>
                </div>
                <div className="flex justify-between border-b border-white/10 pb-2">
                  <span className="text-text-secondary">Time Taken:</span>
                  <span className="text-white font-medium">{result.totalTimeMinutes} minutes</span>
                </div>
              </div>
            </div>
            
            <div>
              <h2 className="text-h3 font-medium text-white mb-4">DISC Profile</h2>
              <div className="flex flex-col h-full">
                <div className="flex-1 flex items-center justify-center">
                  <div className="bg-background-dark/80 rounded-xl p-4 w-full">
                    <div className="grid grid-cols-4 gap-2 mb-2">
                      <div className="text-center">
                        <div className="text-primary-blue font-bold">D</div>
                        <div className="text-text-secondary text-small">Dominance</div>
                      </div>
                      <div className="text-center">
                        <div className="text-primary-pink font-bold">I</div>
                        <div className="text-text-secondary text-small">Influence</div>
                      </div>
                      <div className="text-center">
                        <div className="text-secondary-teal font-bold">S</div>
                        <div className="text-text-secondary text-small">Steadiness</div>
                      </div>
                      <div className="text-center">
                        <div className="text-secondary-coral font-bold">C</div>
                        <div className="text-text-secondary text-small">Conscientiousness</div>
                      </div>
                    </div>
                    
                    <div className="grid grid-cols-4 gap-2 mb-2">
                      <div className="flex flex-col items-center">
                        <div className="h-32 w-full bg-background-dark/50 rounded-lg relative">
                          <div 
                            className="absolute bottom-0 w-full bg-primary-blue rounded-b-lg"
                            style={{ height: `${(result.scores.dominance / maxScore) * 100}%` }}
                          ></div>
                        </div>
                        <div className="mt-1 font-bold">{result.scores.dominance}</div>
                      </div>
                      
                      <div className="flex flex-col items-center">
                        <div className="h-32 w-full bg-background-dark/50 rounded-lg relative">
                          <div 
                            className="absolute bottom-0 w-full bg-primary-pink rounded-b-lg"
                            style={{ height: `${(result.scores.influence / maxScore) * 100}%` }}
                          ></div>
                        </div>
                        <div className="mt-1 font-bold">{result.scores.influence}</div>
                      </div>
                      
                      <div className="flex flex-col items-center">
                        <div className="h-32 w-full bg-background-dark/50 rounded-lg relative">
                          <div 
                            className="absolute bottom-0 w-full bg-secondary-teal rounded-b-lg"
                            style={{ height: `${(result.scores.steadiness / maxScore) * 100}%` }}
                          ></div>
                        </div>
                        <div className="mt-1 font-bold">{result.scores.steadiness}</div>
                      </div>
                      
                      <div className="flex flex-col items-center">
                        <div className="h-32 w-full bg-background-dark/50 rounded-lg relative">
                          <div 
                            className="absolute bottom-0 w-full bg-secondary-coral rounded-b-lg"
                            style={{ height: `${(result.scores.conscientiousness / maxScore) * 100}%` }}
                          ></div>
                        </div>
                        <div className="mt-1 font-bold">{result.scores.conscientiousness}</div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Recommendation Section */}
        <div className="glassmorphism p-6 mb-8">
          <h2 className="text-h3 font-medium text-white mb-4">Recommendation</h2>
          <div className="bg-background-dark/80 rounded-xl p-6 mb-6">
            <div className="flex items-center mb-4">
              <div className="mr-4">
                <div className="w-16 h-16 rounded-full bg-gradient-to-r from-primary-blue to-primary-purple flex items-center justify-center text-h2 font-bold">
                  {result.interpretation.recommendedLevel.split(' ')[1]}
                </div>
              </div>
              <div>
                <h3 className="text-h3 font-bold text-white">
                  Recommended Position: <span className="gradient-text">{result.interpretation.recommendedLevel}</span>
                </h3>
              </div>
            </div>
            <p className="text-text-secondary mb-4">
              {result.interpretation.profileSummary}
            </p>
          </div>
          
          <h2 className="text-h3 font-medium text-white mb-4">Dimension Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-background-dark/80 rounded-xl p-4">
              <h3 className="font-bold text-primary-blue mb-2">Dominance</h3>
              <p className="text-text-secondary text-sm">
                {result.interpretation.interpretations.dominance}
              </p>
            </div>
            <div className="bg-background-dark/80 rounded-xl p-4">
              <h3 className="font-bold text-primary-pink mb-2">Influence</h3>
              <p className="text-text-secondary text-sm">
                {result.interpretation.interpretations.influence}
              </p>
            </div>
            <div className="bg-background-dark/80 rounded-xl p-4">
              <h3 className="font-bold text-secondary-teal mb-2">Steadiness</h3>
              <p className="text-text-secondary text-sm">
                {result.interpretation.interpretations.steadiness}
              </p>
            </div>
            <div className="bg-background-dark/80 rounded-xl p-4">
              <h3 className="font-bold text-secondary-coral mb-2">Conscientiousness</h3>
              <p className="text-text-secondary text-sm">
                {result.interpretation.interpretations.conscientiousness}
              </p>
            </div>
          </div>
        </div>
        
        {/* Actions Section */}
        <div className="flex flex-col sm:flex-row gap-4 justify-end">
          <button
            onClick={handleShareResults}
            className="border border-primary-blue py-2 px-4 rounded-lg text-primary-blue font-medium hover:bg-primary-blue/10 transition-colors duration-300 flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path d="M15 8a3 3 0 10-2.977-2.63l-4.94 2.47a3 3 0 100 4.319l4.94 2.47a3 3 0 10.895-1.789l-4.94-2.47a3.027 3.027 0 000-.74l4.94-2.47C13.456 7.68 14.19 8 15 8z"></path>
            </svg>
            Share Results
          </button>
          <button
            onClick={handleDownloadPDF}
            className="btn-primary flex items-center justify-center"
          >
            <svg className="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 20 20" xmlns="http://www.w3.org/2000/svg">
              <path fillRule="evenodd" d="M3 17a1 1 0 011-1h12a1 1 0 110 2H4a1 1 0 01-1-1zm3.293-7.707a1 1 0 011.414 0L9 10.586V3a1 1 0 112 0v7.586l1.293-1.293a1 1 0 111.414 1.414l-3 3a1 1 0 01-1.414 0l-3-3a1 1 0 010-1.414z" clipRule="evenodd"></path>
            </svg>
            Download PDF
          </button>
        </div>
      </div>
    </div>
  );
};

export default Results;