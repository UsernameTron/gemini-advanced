import { AssessmentModel } from '../../models/assessment.model';
import db from '../../db';

// Mock the database
jest.mock('../../db', () => ({
  __esModule: true,
  default: {
    select: jest.fn().mockReturnThis(),
    where: jest.fn().mockReturnThis(),
    first: jest.fn(),
    insert: jest.fn().mockResolvedValue([1]),
    update: jest.fn().mockResolvedValue(1),
    del: jest.fn().mockResolvedValue(1),
    orderBy: jest.fn().mockReturnThis(),
    fn: {
      now: jest.fn().mockReturnValue('2023-03-15T12:00:00.000Z'),
    },
  },
}));

describe('AssessmentModel', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('getAssessmentById', () => {
    it('should return assessment when found', async () => {
      // Arrange
      const mockAssessment = {
        id: 1,
        candidate_id: 1,
        position_level: 'level_2',
        status: 'in_progress',
        started_at: '2023-03-15T10:00:00.000Z',
        completed_at: null,
        dominance_score: 0,
        influence_score: 0,
        steadiness_score: 0,
        conscientiousness_score: 0,
        total_time_minutes: 0,
      };

      (db.first as jest.Mock).mockResolvedValueOnce(mockAssessment);

      // Act
      const result = await AssessmentModel.getAssessmentById(1);

      // Assert
      expect(db.where).toHaveBeenCalledWith({ id: 1 });
      expect(db.first).toHaveBeenCalled();
      expect(result).toEqual(mockAssessment);
    });

    it('should return null when assessment not found', async () => {
      // Arrange
      (db.first as jest.Mock).mockResolvedValueOnce(undefined);

      // Act
      const result = await AssessmentModel.getAssessmentById(999);

      // Assert
      expect(db.where).toHaveBeenCalledWith({ id: 999 });
      expect(db.first).toHaveBeenCalled();
      expect(result).toBeNull();
    });
  });

  describe('createAssessment', () => {
    it('should create a new assessment and return it', async () => {
      // Arrange
      const assessmentData = {
        candidate_id: 1,
        position_level: 'level_2' as const,
      };

      const mockCreatedAssessment = {
        id: 1,
        ...assessmentData,
        status: 'in_progress',
        started_at: '2023-03-15T12:00:00.000Z',
        completed_at: null,
        dominance_score: 0,
        influence_score: 0,
        steadiness_score: 0,
        conscientiousness_score: 0,
        total_time_minutes: 0,
      };

      // Mock the getAssessmentById method
      jest.spyOn(AssessmentModel, 'getAssessmentById').mockResolvedValueOnce(mockCreatedAssessment);

      // Act
      const result = await AssessmentModel.createAssessment(assessmentData);

      // Assert
      expect(db.insert).toHaveBeenCalledWith({
        candidate_id: assessmentData.candidate_id,
        position_level: assessmentData.position_level,
        status: 'in_progress',
        started_at: expect.any(String),
      });
      expect(AssessmentModel.getAssessmentById).toHaveBeenCalledWith(1);
      expect(result).toEqual(mockCreatedAssessment);
    });
  });

  describe('completeAssessment', () => {
    it('should update assessment status to completed with scores', async () => {
      // Arrange
      const assessmentId = 1;
      const totalTimeMinutes = 20;

      const mockResponses = [
        { question_number: 1, selected_option: 'A' },
        { question_number: 2, selected_option: 'B' },
        { question_number: 3, selected_option: 'C' },
      ];

      const mockQuestions = [
        { question_number: 1, dimension_a: 'D', dimension_b: 'I', dimension_c: 'S', dimension_d: 'C' },
        { question_number: 2, dimension_a: 'D', dimension_b: 'I', dimension_c: 'S', dimension_d: 'C' },
        { question_number: 3, dimension_a: 'D', dimension_b: 'I', dimension_c: 'S', dimension_d: 'C' },
      ];

      const mockCompletedAssessment = {
        id: assessmentId,
        status: 'completed',
        completed_at: '2023-03-15T12:00:00.000Z',
        dominance_score: 1,
        influence_score: 1,
        steadiness_score: 1,
        conscientiousness_score: 0,
        total_time_minutes: totalTimeMinutes,
      };

      // Mock getAssessmentResponses method
      jest.spyOn(AssessmentModel, 'getAssessmentResponses').mockResolvedValueOnce(mockResponses);

      // Mock getAllQuestions method
      jest.spyOn(AssessmentModel, 'getAllQuestions').mockResolvedValueOnce(mockQuestions);

      // Mock getAssessmentById method
      jest.spyOn(AssessmentModel, 'getAssessmentById').mockResolvedValueOnce(mockCompletedAssessment);

      // Act
      const result = await AssessmentModel.completeAssessment(assessmentId, totalTimeMinutes);

      // Assert
      expect(AssessmentModel.getAssessmentResponses).toHaveBeenCalledWith(assessmentId);
      expect(AssessmentModel.getAllQuestions).toHaveBeenCalled();
      expect(db.update).toHaveBeenCalledWith({
        status: 'completed',
        completed_at: expect.any(String),
        dominance_score: expect.any(Number),
        influence_score: expect.any(Number),
        steadiness_score: expect.any(Number),
        conscientiousness_score: expect.any(Number),
        total_time_minutes: totalTimeMinutes,
      });
      expect(AssessmentModel.getAssessmentById).toHaveBeenCalledWith(assessmentId);
      expect(result).toEqual(mockCompletedAssessment);
    });
  });
});