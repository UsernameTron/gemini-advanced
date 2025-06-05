import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface Assessment {
  id: number;
  status: 'in_progress' | 'completed' | 'expired';
  positionLevel: 'level_1' | 'level_2' | 'level_3';
  startedAt: string;
  completedAt: string | null;
}

const Dashboard: React.FC = () => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  
  useEffect(() => {
    // Check if user is logged in
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }
    
    // TODO: Fetch actual assessments from API
    const fetchAssessments = async () => {
      try {
        // Simulate API call
        setTimeout(() => {
          const mockAssessments: Assessment[] = [
            {
              id: 1,
              status: 'completed',
              positionLevel: 'level_1',
              startedAt: '2023-03-15T10:30:00Z',
              completedAt: '2023-03-15T11:15:00Z'
            },
            {
              id: 2,
              status: 'in_progress',
              positionLevel: 'level_2',
              startedAt: '2023-03-20T14:00:00Z',
              completedAt: null
            }
          ];
          
          setAssessments(mockAssessments);
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load assessments');
        setLoading(false);
      }
    };
    
    fetchAssessments();
  }, [navigate]);
  
  const handleLogout = () => {
    localStorage.removeItem('token');
    navigate('/login');
  };
  
  const startNewAssessment = () => {
    // TODO: Implement actual API call to create a new assessment
    navigate('/assessment/new');
  };

  return (
    <div className="min-h-screen p-4 sm:p-6 md:p-8">
      <div className="max-w-6xl mx-auto">
        <header className="flex justify-between items-center mb-8">
          <h1 className="text-h2 font-bold gradient-text">Dashboard</h1>
          <button 
            onClick={handleLogout}
            className="border border-primary-pink py-2 px-4 rounded-lg text-primary-pink font-medium hover:bg-primary-pink/10 transition-colors duration-300"
          >
            Logout
          </button>
        </header>
        
        <div className="glassmorphism p-6 mb-8">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-6">
            <h2 className="text-h3 font-medium text-white mb-4 sm:mb-0">Your Assessments</h2>
            <button 
              onClick={startNewAssessment}
              className="btn-primary"
            >
              Start New Assessment
            </button>
          </div>
          
          {loading ? (
            <p className="text-text-secondary">Loading assessments...</p>
          ) : error ? (
            <p className="text-red-400">{error}</p>
          ) : assessments.length === 0 ? (
            <p className="text-text-secondary">No assessments found. Start a new one!</p>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-white/10">
                    <th className="text-left py-3 px-4 text-text-secondary">ID</th>
                    <th className="text-left py-3 px-4 text-text-secondary">Status</th>
                    <th className="text-left py-3 px-4 text-text-secondary">Position Level</th>
                    <th className="text-left py-3 px-4 text-text-secondary">Started</th>
                    <th className="text-left py-3 px-4 text-text-secondary">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {assessments.map((assessment) => (
                    <tr key={assessment.id} className="border-b border-white/10 hover:bg-white/5">
                      <td className="py-4 px-4">{assessment.id}</td>
                      <td className="py-4 px-4">
                        <span className={`px-2 py-1 rounded-full text-xs ${
                          assessment.status === 'completed' ? 'bg-green-500/20 text-green-300' :
                          assessment.status === 'in_progress' ? 'bg-blue-500/20 text-blue-300' :
                          'bg-red-500/20 text-red-300'
                        }`}>
                          {assessment.status.replace('_', ' ')}
                        </span>
                      </td>
                      <td className="py-4 px-4 capitalize">{assessment.positionLevel.replace('_', ' ')}</td>
                      <td className="py-4 px-4">{new Date(assessment.startedAt).toLocaleString()}</td>
                      <td className="py-4 px-4">
                        {assessment.status === 'completed' ? (
                          <Link 
                            to={`/results/${assessment.id}`}
                            className="text-primary-blue hover:underline"
                          >
                            View Results
                          </Link>
                        ) : (
                          <Link 
                            to={`/assessment/${assessment.id}`}
                            className="text-primary-blue hover:underline"
                          >
                            Continue
                          </Link>
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;