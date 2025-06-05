import { Request, Response, NextFunction } from 'express';
import { AssessmentModel } from '../models/assessment.model';
import { UserModel } from '../models/user.model';
import { ApiError } from '../middleware/error.middleware';

// Get candidate summary reports (admin/HR only)
export const getCandidateSummaryReports = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    // Get all candidates
    const candidates = await UserModel.getAllUsers();
    const candidateList = candidates.filter(user => user.role === 'candidate');
    
    // Get all assessments
    const assessments = await AssessmentModel.getAllAssessments();
    
    // Create summary reports
    const summaryReports = await Promise.all(
      candidateList.map(async (candidate) => {
        // Get assessments for this candidate
        const candidateAssessments = assessments.filter(
          assessment => assessment.candidate_id === candidate.id
        );
        
        // Count assessments by status
        const completedAssessments = candidateAssessments.filter(
          assessment => assessment.status === 'completed'
        );
        
        const inProgressAssessments = candidateAssessments.filter(
          assessment => assessment.status === 'in_progress'
        );
        
        const expiredAssessments = candidateAssessments.filter(
          assessment => assessment.status === 'expired'
        );
        
        // Calculate average scores across all completed assessments
        const avgScores = completedAssessments.length > 0
          ? {
              dominance: calculateAverage(completedAssessments.map(a => a.dominance_score)),
              influence: calculateAverage(completedAssessments.map(a => a.influence_score)),
              steadiness: calculateAverage(completedAssessments.map(a => a.steadiness_score)),
              conscientiousness: calculateAverage(completedAssessments.map(a => a.conscientiousness_score))
            }
          : null;
        
        // Determine most common recommended level
        const recommendedLevels = completedAssessments.map(assessment => 
          determineRecommendedLevel(assessment)
        );
        
        const mostCommonLevel = recommendedLevels.length > 0
          ? getMostCommonValue(recommendedLevels)
          : null;
        
        return {
          candidate: {
            id: candidate.id,
            name: `${candidate.first_name} ${candidate.last_name}`,
            email: candidate.email
          },
          assessmentCounts: {
            total: candidateAssessments.length,
            completed: completedAssessments.length,
            inProgress: inProgressAssessments.length,
            expired: expiredAssessments.length
          },
          averageScores: avgScores,
          recommendedLevel: mostCommonLevel,
          lastAssessmentDate: completedAssessments.length > 0
            ? completedAssessments
                .sort((a, b) => 
                  new Date(b.completed_at || '').getTime() - 
                  new Date(a.completed_at || '').getTime()
                )[0].completed_at
            : null
        };
      })
    );
    
    res.status(200).json({
      status: 'success',
      results: summaryReports.length,
      data: {
        summaryReports
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get assessment analytics (admin/HR only)
export const getAssessmentAnalytics = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    // Get all assessments
    const assessments = await AssessmentModel.getAllAssessments();
    
    // Get completed assessments
    const completedAssessments = assessments.filter(
      assessment => assessment.status === 'completed'
    );
    
    // Calculate completion rate
    const completionRate = assessments.length > 0
      ? (completedAssessments.length / assessments.length) * 100
      : 0;
    
    // Calculate average completion time
    const avgCompletionTime = completedAssessments.length > 0
      ? calculateAverage(completedAssessments.map(a => a.total_time_minutes))
      : 0;
    
    // Calculate average scores
    const avgScores = completedAssessments.length > 0
      ? {
          dominance: calculateAverage(completedAssessments.map(a => a.dominance_score)),
          influence: calculateAverage(completedAssessments.map(a => a.influence_score)),
          steadiness: calculateAverage(completedAssessments.map(a => a.steadiness_score)),
          conscientiousness: calculateAverage(completedAssessments.map(a => a.conscientiousness_score))
        }
      : {
          dominance: 0,
          influence: 0,
          steadiness: 0,
          conscientiousness: 0
        };
    
    // Count assessments by position level
    const levelCounts = {
      level_1: assessments.filter(a => a.position_level === 'level_1').length,
      level_2: assessments.filter(a => a.position_level === 'level_2').length,
      level_3: assessments.filter(a => a.position_level === 'level_3').length
    };
    
    // Count recommended levels
    const recommendedLevelCounts = {
      'Level 1': 0,
      'Level 2': 0,
      'Level 3': 0
    };
    
    completedAssessments.forEach(assessment => {
      const level = determineRecommendedLevel(assessment);
      recommendedLevelCounts[level]++;
    });
    
    res.status(200).json({
      status: 'success',
      data: {
        totalAssessments: assessments.length,
        completedAssessments: completedAssessments.length,
        inProgressAssessments: assessments.filter(a => a.status === 'in_progress').length,
        expiredAssessments: assessments.filter(a => a.status === 'expired').length,
        completionRate,
        avgCompletionTime,
        avgScores,
        levelCounts,
        recommendedLevelCounts
      }
    });
  } catch (error) {
    next(error);
  }
};

// Export assessment data (admin/HR only)
export const exportAssessmentData = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { format } = req.body;
    
    if (!['json', 'csv'].includes(format)) {
      return next(new ApiError(400, 'Invalid export format. Use "json" or "csv".'));
    }
    
    // Get all assessments with candidate info
    const assessments = await AssessmentModel.getAllAssessments();
    
    // Enrich with candidate info
    const enrichedData = await Promise.all(
      assessments.map(async (assessment) => {
        const candidate = await UserModel.getUserById(assessment.candidate_id);
        
        return {
          assessmentId: assessment.id,
          status: assessment.status,
          positionLevel: assessment.position_level,
          startedAt: assessment.started_at,
          completedAt: assessment.completed_at,
          totalTimeMinutes: assessment.total_time_minutes,
          candidateId: assessment.candidate_id,
          candidateName: candidate ? `${candidate.first_name} ${candidate.last_name}` : 'Unknown',
          candidateEmail: candidate ? candidate.email : 'Unknown',
          scores: {
            dominance: assessment.dominance_score,
            influence: assessment.influence_score,
            steadiness: assessment.steadiness_score,
            conscientiousness: assessment.conscientiousness_score
          },
          recommendedLevel: assessment.status === 'completed' ? determineRecommendedLevel(assessment) : null
        };
      })
    );
    
    if (format === 'csv') {
      // TODO: Implement actual CSV generation
      // For now, return a message
      return res.status(200).json({
        status: 'success',
        message: 'CSV export functionality will be implemented in the future.',
        data: {
          exportedData: enrichedData
        }
      });
    }
    
    res.status(200).json({
      status: 'success',
      results: enrichedData.length,
      data: {
        exportedData: enrichedData
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get comparative analysis for selected candidates (admin/HR only)
export const getComparativeAnalysis = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { candidateIds } = req.body;
    
    if (!Array.isArray(candidateIds) || candidateIds.length === 0) {
      return next(new ApiError(400, 'Please provide an array of candidate IDs'));
    }
    
    // Get all assessments
    const assessments = await AssessmentModel.getAllAssessments();
    
    // Filter for completed assessments of the requested candidates
    const relevantAssessments = assessments.filter(assessment => 
      assessment.status === 'completed' && 
      candidateIds.includes(assessment.candidate_id)
    );
    
    // Group assessments by candidate
    const candidateAssessments: { [key: number]: any[] } = {};
    
    relevantAssessments.forEach(assessment => {
      if (!candidateAssessments[assessment.candidate_id]) {
        candidateAssessments[assessment.candidate_id] = [];
      }
      candidateAssessments[assessment.candidate_id].push(assessment);
    });
    
    // Generate comparative analysis
    const comparativeData = await Promise.all(
      Object.entries(candidateAssessments).map(async ([candidateId, assessments]) => {
        const candidate = await UserModel.getUserById(parseInt(candidateId));
        
        // Get the latest assessment
        const latestAssessment = assessments.sort((a, b) => 
          new Date(b.completed_at || '').getTime() - 
          new Date(a.completed_at || '').getTime()
        )[0];
        
        return {
          candidate: {
            id: parseInt(candidateId),
            name: candidate ? `${candidate.first_name} ${candidate.last_name}` : 'Unknown',
            email: candidate ? candidate.email : 'Unknown'
          },
          latestAssessment: {
            id: latestAssessment.id,
            date: latestAssessment.completed_at,
            scores: {
              dominance: latestAssessment.dominance_score,
              influence: latestAssessment.influence_score,
              steadiness: latestAssessment.steadiness_score,
              conscientiousness: latestAssessment.conscientiousness_score
            },
            recommendedLevel: determineRecommendedLevel(latestAssessment)
          },
          assessmentCount: assessments.length
        };
      })
    );
    
    res.status(200).json({
      status: 'success',
      results: comparativeData.length,
      data: {
        comparativeData
      }
    });
  } catch (error) {
    next(error);
  }
};

// Helper function to calculate average of an array of numbers
function calculateAverage(numbers: number[]): number {
  if (numbers.length === 0) return 0;
  const sum = numbers.reduce((a, b) => a + b, 0);
  return parseFloat((sum / numbers.length).toFixed(1));
}

// Helper function to get most common value in an array
function getMostCommonValue<T>(arr: T[]): T | null {
  if (arr.length === 0) return null;
  
  const counts: { [key: string]: number } = {};
  
  arr.forEach(value => {
    const key = String(value);
    counts[key] = (counts[key] || 0) + 1;
  });
  
  let maxCount = 0;
  let maxValue: string = '';
  
  for (const [value, count] of Object.entries(counts)) {
    if (count > maxCount) {
      maxCount = count;
      maxValue = value;
    }
  }
  
  // Find the original typed value
  const originalValue = arr.find(value => String(value) === maxValue);
  return originalValue !== undefined ? originalValue : null;
}

// Helper function to determine recommended level based on DISC scores
function determineRecommendedLevel(assessment: any): 'Level 1' | 'Level 2' | 'Level 3' {
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