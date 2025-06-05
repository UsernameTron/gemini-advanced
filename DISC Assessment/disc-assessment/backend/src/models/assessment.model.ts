import db from '../db';

export interface Assessment {
  id: number;
  candidate_id: number;
  position_level: 'level_1' | 'level_2' | 'level_3';
  status: 'in_progress' | 'completed' | 'expired';
  started_at: string;
  completed_at: string | null;
  dominance_score: number;
  influence_score: number;
  steadiness_score: number;
  conscientiousness_score: number;
  total_time_minutes: number;
}

export interface AssessmentInput {
  candidate_id: number;
  position_level: 'level_1' | 'level_2' | 'level_3';
}

export interface AssessmentResponse {
  id?: number;
  assessment_id: number;
  question_number: number;
  selected_option: 'A' | 'B' | 'C' | 'D';
  response_time_seconds: number;
}

export interface Question {
  id: number;
  question_number: number;
  scenario_text: string;
  option_a: string;
  option_b: string;
  option_c: string;
  option_d: string;
  dimension_a: 'D' | 'I' | 'S' | 'C';
  dimension_b: 'D' | 'I' | 'S' | 'C';
  dimension_c: 'D' | 'I' | 'S' | 'C';
  dimension_d: 'D' | 'I' | 'S' | 'C';
  created_at: string;
}

// Assessment model with static methods
export const AssessmentModel = {
  // Get all assessments (for admin/HR)
  async getAllAssessments(): Promise<Assessment[]> {
    return db('assessments').select('*');
  },

  // Get assessments for a specific candidate
  async getCandidateAssessments(candidateId: number): Promise<Assessment[]> {
    return db('assessments').where({ candidate_id: candidateId }).select('*');
  },

  // Get assessment by ID
  async getAssessmentById(id: number): Promise<Assessment | null> {
    const assessment = await db('assessments').where({ id }).first();
    return assessment || null;
  },

  // Create a new assessment
  async createAssessment(assessmentData: AssessmentInput): Promise<Assessment> {
    const [id] = await db('assessments').insert({
      candidate_id: assessmentData.candidate_id,
      position_level: assessmentData.position_level,
      status: 'in_progress',
      started_at: db.fn.now()
    });

    return this.getAssessmentById(id) as Promise<Assessment>;
  },

  // Update assessment
  async updateAssessment(id: number, data: Partial<Assessment>): Promise<Assessment | null> {
    await db('assessments').where({ id }).update(data);
    return this.getAssessmentById(id);
  },

  // Complete assessment
  async completeAssessment(id: number, totalTimeMinutes: number): Promise<Assessment | null> {
    const now = new Date().toISOString();
    
    // Calculate scores
    const responses = await this.getAssessmentResponses(id);
    const questions = await this.getAllQuestions();
    
    // Initialize scores
    let dominanceScore = 0;
    let influenceScore = 0;
    let steadinessScore = 0;
    let conscientiousnessScore = 0;
    
    // Calculate scores based on responses
    for (const response of responses) {
      const question = questions.find(q => q.question_number === response.question_number);
      
      if (question) {
        const dimensionKey = `dimension_${response.selected_option.toLowerCase()}` as 
          'dimension_a' | 'dimension_b' | 'dimension_c' | 'dimension_d';
        
        const dimension = question[dimensionKey];
        
        switch (dimension) {
          case 'D':
            dominanceScore += 1;
            break;
          case 'I':
            influenceScore += 1;
            break;
          case 'S':
            steadinessScore += 1;
            break;
          case 'C':
            conscientiousnessScore += 1;
            break;
        }
      }
    }
    
    // Update assessment with scores
    await db('assessments').where({ id }).update({
      status: 'completed',
      completed_at: now,
      dominance_score: dominanceScore,
      influence_score: influenceScore,
      steadiness_score: steadinessScore,
      conscientiousness_score: conscientiousnessScore,
      total_time_minutes: totalTimeMinutes
    });
    
    return this.getAssessmentById(id);
  },

  // Delete assessment
  async deleteAssessment(id: number): Promise<boolean> {
    // First delete related responses
    await db('assessment_responses').where({ assessment_id: id }).del();
    
    // Then delete the assessment
    const deleted = await db('assessments').where({ id }).del();
    return deleted > 0;
  },

  // Get all questions
  async getAllQuestions(): Promise<Question[]> {
    return db('questions').select('*').orderBy('question_number');
  },

  // Get question by number
  async getQuestionByNumber(questionNumber: number): Promise<Question | null> {
    const question = await db('questions').where({ question_number: questionNumber }).first();
    return question || null;
  },

  // Save assessment response
  async saveResponse(responseData: AssessmentResponse): Promise<number> {
    const [id] = await db('assessment_responses').insert({
      assessment_id: responseData.assessment_id,
      question_number: responseData.question_number,
      selected_option: responseData.selected_option,
      response_time_seconds: responseData.response_time_seconds,
      created_at: db.fn.now()
    });
    
    return id;
  },

  // Get responses for an assessment
  async getAssessmentResponses(assessmentId: number): Promise<AssessmentResponse[]> {
    return db('assessment_responses')
      .where({ assessment_id: assessmentId })
      .select('*')
      .orderBy('question_number');
  }
};