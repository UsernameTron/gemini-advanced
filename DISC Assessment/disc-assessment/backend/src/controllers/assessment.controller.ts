import { Request, Response, NextFunction } from 'express';
import { AssessmentModel, AssessmentInput, AssessmentResponse } from '../models/assessment.model';
import { ApiError } from '../middleware/error.middleware';
import { UserModel } from '../models/user.model';

// Get all assessments (admin/HR only)
export const getAllAssessments = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const assessments = await AssessmentModel.getAllAssessments();

    res.status(200).json({
      status: 'success',
      results: assessments.length,
      data: {
        assessments
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get assessments for the authenticated candidate
export const getMyCandidateAssessments = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    const assessments = await AssessmentModel.getCandidateAssessments(req.user.id);

    res.status(200).json({
      status: 'success',
      results: assessments.length,
      data: {
        assessments
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get assessments for a specific candidate (admin/HR only)
export const getCandidateAssessments = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { candidateId } = req.params;

    // Check if candidate exists
    const candidate = await UserModel.getUserById(parseInt(candidateId));
    if (!candidate) {
      return next(new ApiError(404, 'Candidate not found'));
    }

    const assessments = await AssessmentModel.getCandidateAssessments(parseInt(candidateId));

    res.status(200).json({
      status: 'success',
      results: assessments.length,
      data: {
        assessments
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get assessment by ID
export const getAssessment = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { id } = req.params;

    const assessment = await AssessmentModel.getAssessmentById(parseInt(id));
    if (!assessment) {
      return next(new ApiError(404, 'Assessment not found'));
    }

    // Check if user has permission to access this assessment
    if (
      req.user?.role !== 'admin' &&
      req.user?.role !== 'hr' &&
      assessment.candidate_id !== req.user?.id
    ) {
      return next(new ApiError(403, 'You do not have permission to access this assessment'));
    }

    res.status(200).json({
      status: 'success',
      data: {
        assessment
      }
    });
  } catch (error) {
    next(error);
  }
};

// Create a new assessment
export const createAssessment = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { position_level } = req.body;
    
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    // Prepare assessment data
    const assessmentData: AssessmentInput = {
      candidate_id: req.user.id,
      position_level
    };

    // Create assessment
    const assessment = await AssessmentModel.createAssessment(assessmentData);

    res.status(201).json({
      status: 'success',
      data: {
        assessment
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update assessment (admin/HR only)
export const updateAssessment = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { id } = req.params;
    const { status, position_level } = req.body;

    // Check if assessment exists
    const assessment = await AssessmentModel.getAssessmentById(parseInt(id));
    if (!assessment) {
      return next(new ApiError(404, 'Assessment not found'));
    }

    // Update assessment
    const updatedAssessment = await AssessmentModel.updateAssessment(parseInt(id), {
      status,
      position_level
    });

    res.status(200).json({
      status: 'success',
      data: {
        assessment: updatedAssessment
      }
    });
  } catch (error) {
    next(error);
  }
};

// Delete assessment (admin only)
export const deleteAssessment = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { id } = req.params;

    // Check if assessment exists
    const assessment = await AssessmentModel.getAssessmentById(parseInt(id));
    if (!assessment) {
      return next(new ApiError(404, 'Assessment not found'));
    }

    // Delete assessment
    await AssessmentModel.deleteAssessment(parseInt(id));

    res.status(204).json({
      status: 'success',
      data: null
    });
  } catch (error) {
    next(error);
  }
};

// Get all questions
export const getAllQuestions = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const questions = await AssessmentModel.getAllQuestions();

    res.status(200).json({
      status: 'success',
      results: questions.length,
      data: {
        questions
      }
    });
  } catch (error) {
    next(error);
  }
};

// Submit a response to a question
export const submitResponse = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { assessment_id, question_number, selected_option, response_time_seconds } = req.body;
    
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    // Check if assessment exists
    const assessment = await AssessmentModel.getAssessmentById(assessment_id);
    if (!assessment) {
      return next(new ApiError(404, 'Assessment not found'));
    }

    // Check if user has permission to submit response
    if (assessment.candidate_id !== req.user.id) {
      return next(new ApiError(403, 'You do not have permission to submit responses for this assessment'));
    }

    // Check if assessment is still in progress
    if (assessment.status !== 'in_progress') {
      return next(new ApiError(400, 'Cannot submit responses for a completed or expired assessment'));
    }

    // Check if question exists
    const question = await AssessmentModel.getQuestionByNumber(question_number);
    if (!question) {
      return next(new ApiError(404, 'Question not found'));
    }

    // Prepare response data
    const responseData: AssessmentResponse = {
      assessment_id,
      question_number,
      selected_option,
      response_time_seconds
    };

    // Save response
    const responseId = await AssessmentModel.saveResponse(responseData);

    res.status(201).json({
      status: 'success',
      data: {
        response_id: responseId
      }
    });
  } catch (error) {
    next(error);
  }
};

// Complete an assessment
export const completeAssessment = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { id } = req.params;
    const { total_time_minutes } = req.body;
    
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    // Check if assessment exists
    const assessment = await AssessmentModel.getAssessmentById(parseInt(id));
    if (!assessment) {
      return next(new ApiError(404, 'Assessment not found'));
    }

    // Check if user has permission to complete assessment
    if (assessment.candidate_id !== req.user.id) {
      return next(new ApiError(403, 'You do not have permission to complete this assessment'));
    }

    // Check if assessment is still in progress
    if (assessment.status !== 'in_progress') {
      return next(new ApiError(400, 'Assessment is already completed or expired'));
    }

    // Get responses for this assessment
    const responses = await AssessmentModel.getAssessmentResponses(parseInt(id));
    
    // Check if all questions have been answered
    const questions = await AssessmentModel.getAllQuestions();
    if (responses.length < questions.length) {
      return next(new ApiError(400, 'Cannot complete assessment. Not all questions have been answered.'));
    }

    // Complete assessment and calculate scores
    const completedAssessment = await AssessmentModel.completeAssessment(
      parseInt(id), 
      total_time_minutes
    );

    res.status(200).json({
      status: 'success',
      data: {
        assessment: completedAssessment
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get assessment results
export const getAssessmentResults = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { id } = req.params;
    
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    // Check if assessment exists
    const assessment = await AssessmentModel.getAssessmentById(parseInt(id));
    if (!assessment) {
      return next(new ApiError(404, 'Assessment not found'));
    }

    // Check if user has permission to view results
    if (
      req.user.role !== 'admin' &&
      req.user.role !== 'hr' &&
      assessment.candidate_id !== req.user.id
    ) {
      return next(new ApiError(403, 'You do not have permission to view these assessment results'));
    }

    // Check if assessment is completed
    if (assessment.status !== 'completed') {
      return next(new ApiError(400, 'Assessment is not yet completed'));
    }

    // Get candidate details
    const candidate = await UserModel.getUserById(assessment.candidate_id);
    if (!candidate) {
      return next(new ApiError(404, 'Candidate not found'));
    }

    // Generate results
    const results = {
      assessment,
      candidate: {
        id: candidate.id,
        first_name: candidate.first_name,
        last_name: candidate.last_name,
        email: candidate.email
      },
      scores: {
        dominance: assessment.dominance_score,
        influence: assessment.influence_score,
        steadiness: assessment.steadiness_score,
        conscientiousness: assessment.conscientiousness_score
      },
      interpretation: generateInterpretation(assessment),
      recommendedLevel: determineRecommendedLevel(assessment)
    };

    res.status(200).json({
      status: 'success',
      data: {
        results
      }
    });
  } catch (error) {
    next(error);
  }
};

// Helper function to generate interpretation based on scores
function generateInterpretation(assessment: any) {
  // Dominance interpretation
  let dominanceInterpretation = '';
  if (assessment.dominance_score >= 11) {
    dominanceInterpretation = 'High dominance indicates a preference for taking charge, making quick decisions, and driving for results.';
  } else if (assessment.dominance_score >= 5) {
    dominanceInterpretation = 'Moderate dominance suggests a balanced approach to decision making and leadership.';
  } else {
    dominanceInterpretation = 'Low dominance indicates a preference for collaborative decision making rather than taking charge.';
  }
  
  // Influence interpretation
  let influenceInterpretation = '';
  if (assessment.influence_score >= 11) {
    influenceInterpretation = 'High influence indicates strong communication skills, persuasiveness, and a people-oriented approach.';
  } else if (assessment.influence_score >= 5) {
    influenceInterpretation = 'Moderate influence suggests a balanced approach to social interactions and team communication.';
  } else {
    influenceInterpretation = 'Low influence indicates a preference for working independently and focusing on tasks rather than social interactions.';
  }
  
  // Steadiness interpretation
  let steadinessInterpretation = '';
  if (assessment.steadiness_score >= 11) {
    steadinessInterpretation = 'High steadiness shows reliability, patience, and a methodical approach to work.';
  } else if (assessment.steadiness_score >= 5) {
    steadinessInterpretation = 'Moderate steadiness indicates a balance between adaptability and consistency.';
  } else {
    steadinessInterpretation = 'Low steadiness suggests a preference for variety, change, and fast-paced environments.';
  }
  
  // Conscientiousness interpretation
  let conscientiousnessInterpretation = '';
  if (assessment.conscientiousness_score >= 11) {
    conscientiousnessInterpretation = 'High conscientiousness demonstrates attention to detail, analytical thinking, and procedural accuracy.';
  } else if (assessment.conscientiousness_score >= 5) {
    conscientiousnessInterpretation = 'Moderate conscientiousness indicates a balance between following procedures and adapting to situations.';
  } else {
    conscientiousnessInterpretation = 'Low conscientiousness suggests a preference for flexibility and big-picture thinking over detailed analysis.';
  }
  
  // Profile summary
  let profileSummary = '';
  
  // Based on dominant traits, create a profile summary
  const scores = [
    { trait: 'dominance', score: assessment.dominance_score },
    { trait: 'influence', score: assessment.influence_score },
    { trait: 'steadiness', score: assessment.steadiness_score },
    { trait: 'conscientiousness', score: assessment.conscientiousness_score }
  ].sort((a, b) => b.score - a.score);
  
  const highestTrait = scores[0].trait;
  const secondHighestTrait = scores[1].trait;
  
  profileSummary = `This profile shows a technician with strong ${highestTrait} characteristics, complemented by ${secondHighestTrait} traits. `;
  
  if (highestTrait === 'dominance') {
    profileSummary += 'They are likely to take initiative, work independently, and drive for results. ';
  } else if (highestTrait === 'influence') {
    profileSummary += 'They are likely to communicate effectively, work well in teams, and build strong relationships. ';
  } else if (highestTrait === 'steadiness') {
    profileSummary += 'They are likely to be reliable, patient, and methodical in their approach to work. ';
  } else if (highestTrait === 'conscientiousness') {
    profileSummary += 'They are likely to be detail-oriented, analytical, and focused on accuracy and quality. ';
  }
  
  return {
    dominance: dominanceInterpretation,
    influence: influenceInterpretation,
    steadiness: steadinessInterpretation,
    conscientiousness: conscientiousnessInterpretation,
    profileSummary
  };
}

// Helper function to determine recommended level based on DISC scores
function determineRecommendedLevel(assessment: any) {
  // Level 1: High S (11-15) + High C (11-15), Low-Moderate D (0-10), Low I (0-4)
  if (
    assessment.steadiness_score >= 11 && 
    assessment.conscientiousness_score >= 11 && 
    assessment.dominance_score <= 10 && 
    assessment.influence_score <= 4
  ) {
    return 'Level 1';
  }
  
  // Level 3: High D (11-15) + Moderate-High I (5-15) + High C (11-15)
  if (
    assessment.dominance_score >= 11 && 
    assessment.influence_score >= 5 && 
    assessment.conscientiousness_score >= 11
  ) {
    return 'Level 3';
  }
  
  // Level 2: Balanced profile with moderate scores
  return 'Level 2';
}