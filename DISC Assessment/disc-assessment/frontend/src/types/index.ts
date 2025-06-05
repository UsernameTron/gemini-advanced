// User types
export interface User {
  id: number;
  email: string;
  firstName: string;
  lastName: string;
  role: 'admin' | 'hr' | 'candidate';
  createdAt: string;
  updatedAt: string;
}

// Assessment types
export interface Assessment {
  id: number;
  candidateId: number;
  positionLevel: 'level_1' | 'level_2' | 'level_3';
  status: 'in_progress' | 'completed' | 'expired';
  startedAt: string;
  completedAt: string | null;
  dominanceScore: number;
  influenceScore: number;
  steadinessScore: number;
  conscientiousnessScore: number;
  totalTimeMinutes: number;
}

// Question types
export interface AssessmentQuestion {
  id: number;
  scenarioText: string;
  options: {
    A: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
    B: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
    C: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
    D: { text: string; dimension: 'D' | 'I' | 'S' | 'C' };
  };
}

// Response types
export interface AssessmentResponse {
  id?: number;
  assessmentId: number;
  questionNumber: number;
  selectedOption: 'A' | 'B' | 'C' | 'D';
  responseTimeSeconds: number;
  createdAt?: string;
}

// Results types
export interface DiscScores {
  dominance: number;
  influence: number;
  steadiness: number;
  conscientiousness: number;
}

export interface ProfileInterpretation {
  interpretations: {
    dominance: string;
    influence: string;
    steadiness: string;
    conscientiousness: string;
  };
  recommendedLevel: 'Level 1' | 'Level 2' | 'Level 3';
  profileSummary: string;
}

export interface AssessmentResult {
  id: number;
  candidateName: string;
  positionLevel: string;
  completedAt: string;
  totalTimeMinutes: number;
  scores: DiscScores;
  interpretation: ProfileInterpretation;
}

// Auth types
export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  firstName: string;
  lastName: string;
  email: string;
  password: string;
  role: 'admin' | 'hr' | 'candidate';
}

export interface AuthResponse {
  user: User;
  token: string;
}