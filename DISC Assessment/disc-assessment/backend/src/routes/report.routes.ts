import express from 'express';
import {
  getCandidateSummaryReports,
  getAssessmentAnalytics,
  exportAssessmentData,
  getComparativeAnalysis
} from '../controllers/report.controller';
import { protect, restrictTo } from '../middleware/auth.middleware';

const router = express.Router();

// Protect all report routes and restrict to admin/HR
router.use(protect);
router.use(restrictTo('admin', 'hr'));

// Report endpoints
router.get('/candidates', getCandidateSummaryReports);
router.get('/analytics', getAssessmentAnalytics);
router.post('/export', exportAssessmentData);
router.post('/comparisons', getComparativeAnalysis);

export default router;