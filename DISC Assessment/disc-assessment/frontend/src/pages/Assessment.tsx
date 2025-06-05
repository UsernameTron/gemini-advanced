import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';

// Define question type based on the interface from the requirements
interface AssessmentQuestion {
  id: number;
  scenarioText: string;
  options: {
    A: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
    B: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
    C: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
    D: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
  };
}

interface AssessmentResponse {
  questionId: number;
  selectedOption: 'A' | 'B' | 'C' | 'D';
  responseTimeSeconds: number;
}

// Mock questions data (to be replaced with API calls)
const mockQuestions: AssessmentQuestion[] = [
  {
    id: 1,
    scenarioText: "A critical server is down and multiple teams are affected. How do you approach this situation?",
    options: {
      A: { text: "Take immediate action and lead the recovery effort", dimension: "D" },
      B: { text: "Call a meeting to discuss the issue with all stakeholders", dimension: "I" },
      C: { text: "Follow established protocols and methodically work through the problem", dimension: "S" },
      D: { text: "Analyze the logs and documentation to determine the root cause", dimension: "C" }
    }
  },
  {
    id: 2,
    scenarioText: "You've discovered a potential security vulnerability. What's your first step?",
    options: {
      A: { text: "Immediately implement a fix to address the vulnerability", dimension: "D" },
      B: { text: "Notify your team and coordinate a response plan", dimension: "I" },
      C: { text: "Document the issue thoroughly before taking action", dimension: "S" },
      D: { text: "Research the vulnerability to understand its full implications", dimension: "C" }
    }
  },
  {
    id: 3,
    scenarioText: "A colleague has proposed a network redesign that you believe has flaws. How do you respond?",
    options: {
      A: { text: "Directly point out the flaws and propose your own solution", dimension: "D" },
      B: { text: "Discuss your concerns in a team meeting to get everyone's input", dimension: "I" },
      C: { text: "Suggest small improvements while maintaining the original concept", dimension: "S" },
      D: { text: "Present a detailed analysis of the potential issues with supporting data", dimension: "C" }
    }
  },
  // Add additional questions up to 15...
];

const Assessment: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [questions, setQuestions] = useState<AssessmentQuestion[]>([]);
  const [responses, setResponses] = useState<AssessmentResponse[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedOption, setSelectedOption] = useState<'A' | 'B' | 'C' | 'D' | null>(null);
  const [startTime, setStartTime] = useState<number>(0);
  const [questionStartTime, setQuestionStartTime] = useState<number>(0);
  const [timeRemaining, setTimeRemaining] = useState<number>(30 * 60); // 30 minutes in seconds

  // Initialize assessment
  useEffect(() => {
    const fetchAssessment = async () => {
      try {
        // TODO: Replace with actual API call
        setTimeout(() => {
          setQuestions(mockQuestions);
          setStartTime(Date.now());
          setQuestionStartTime(Date.now());
          setLoading(false);
        }, 1000);
      } catch (err) {
        setError('Failed to load assessment');
        setLoading(false);
      }
    };

    // Check authentication
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login');
      return;
    }

    fetchAssessment();
  }, [id, navigate]);

  // Timer effect
  useEffect(() => {
    if (loading || timeRemaining <= 0) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          clearInterval(timer);
          // TODO: Submit assessment when time expires
          navigate('/results/' + id);
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [loading, timeRemaining, id, navigate]);

  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  // Calculate progress percentage
  const progressPercentage = loading ? 0 : ((currentQuestion + 1) / questions.length) * 100;

  const handleOptionSelect = (option: 'A' | 'B' | 'C' | 'D') => {
    setSelectedOption(option);
  };

  const handleNextQuestion = () => {
    if (selectedOption === null) return;

    // Record response with time
    const responseTime = Math.round((Date.now() - questionStartTime) / 1000);
    const newResponse: AssessmentResponse = {
      questionId: questions[currentQuestion].id,
      selectedOption,
      responseTimeSeconds: responseTime
    };

    setResponses([...responses, newResponse]);

    // TODO: Implement auto-save to API

    // Move to next question or finish
    if (currentQuestion < questions.length - 1) {
      setCurrentQuestion(currentQuestion + 1);
      setSelectedOption(null);
      setQuestionStartTime(Date.now());
    } else {
      // Assessment complete
      finishAssessment();
    }
  };

  const finishAssessment = async () => {
    try {
      // TODO: Submit assessment to API
      navigate('/results/' + id);
    } catch (err) {
      setError('Failed to submit assessment');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glassmorphism p-8 text-center">
          <h2 className="text-h2 font-bold gradient-text mb-4">Loading Assessment</h2>
          <p className="text-text-secondary">Please wait while we load your assessment...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="glassmorphism p-8 text-center">
          <h2 className="text-h2 font-bold text-red-400 mb-4">Error</h2>
          <p className="text-text-secondary mb-6">{error}</p>
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

  const currentQuestionData = questions[currentQuestion];

  return (
    <div className="min-h-screen p-4 sm:p-6 md:p-8">
      <div className="max-w-4xl mx-auto">
        <header className="flex justify-between items-center mb-6">
          <h1 className="text-h3 font-bold gradient-text">DISC Assessment</h1>
          <div className="flex items-center gap-4">
            <div className="text-text-secondary font-medium">
              Question {currentQuestion + 1} of {questions.length}
            </div>
            <div className="bg-red-500/20 text-red-300 px-3 py-1 rounded-full font-medium">
              Time: {formatTime(timeRemaining)}
            </div>
          </div>
        </header>

        {/* Progress bar */}
        <div className="w-full h-2 bg-background-dark rounded-full mb-8">
          <div
            className="h-full bg-gradient-to-r from-primary-blue to-primary-purple rounded-full"
            style={{ width: `${progressPercentage}%` }}
          ></div>
        </div>

        <div className="glassmorphism p-6 mb-8">
          <h2 className="text-h3 font-medium text-white mb-6">
            {currentQuestionData.scenarioText}
          </h2>

          <div className="space-y-4 mb-8">
            {(['A', 'B', 'C', 'D'] as const).map(option => (
              <button
                key={option}
                onClick={() => handleOptionSelect(option)}
                className={`w-full text-left p-4 rounded-lg border transition-all duration-300 ${
                  selectedOption === option
                    ? 'border-primary-blue bg-primary-blue/10'
                    : 'border-white/10 hover:border-white/30 hover:bg-white/5'
                }`}
              >
                <div className="flex items-start gap-3">
                  <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                    selectedOption === option
                      ? 'bg-primary-blue text-background-dark'
                      : 'bg-background-dark border border-white/20'
                  }`}>
                    {option}
                  </div>
                  <span>{currentQuestionData.options[option].text}</span>
                </div>
              </button>
            ))}
          </div>

          <div className="flex justify-end">
            <button
              onClick={handleNextQuestion}
              disabled={selectedOption === null}
              className={`btn-primary ${
                selectedOption === null ? 'opacity-50 cursor-not-allowed' : ''
              }`}
            >
              {currentQuestion < questions.length - 1 ? 'Next Question' : 'Finish Assessment'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Assessment;