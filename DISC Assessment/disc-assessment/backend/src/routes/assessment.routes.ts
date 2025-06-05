import express from 'express';
import {
  getAllAssessments,
  getMyCandidateAssessments,
  getCandidateAssessments,
  getAssessment,
  createAssessment,
  updateAssessment,
  deleteAssessment,
  getAllQuestions,
  submitResponse,
  completeAssessment,
  getAssessmentResults
} from '../controllers/assessment.controller';
import { protect, restrictTo } from '../middleware/auth.middleware';

const router = express.Router();

// Protect all assessment routes
router.use(protect);

// Admin/HR-only routes
router.get('/', restrictTo('admin', 'hr'), getAllAssessments);
router.get('/candidate/:candidateId', restrictTo('admin', 'hr'), getCandidateAssessments);
router.put('/:id', restrictTo('admin', 'hr'), updateAssessment);
router.delete('/:id', restrictTo('admin'), deleteAssessment);

// Candidate routes
router.get('/my-assessments', getMyCandidateAssessments);
router.post('/', createAssessment);
router.get('/:id', getAssessment);

// Questions and responses
router.get('/questions/all', getAllQuestions);
router.post('/responses', submitResponse);
router.post('/:id/complete', completeAssessment);
router.get('/:id/results', getAssessmentResults);

export default router;