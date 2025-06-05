import express from 'express';
import { 
  register, 
  login, 
  getMe, 
  updatePassword, 
  forgotPassword, 
  resetPassword 
} from '../controllers/auth.controller';
import { protect } from '../middleware/auth.middleware';

const router = express.Router();

// Public routes
router.post('/register', register);
router.post('/login', login);
router.post('/forgot-password', forgotPassword);
router.post('/reset-password', resetPassword);

// Protected routes (require authentication)
router.get('/me', protect, getMe);
router.post('/update-password', protect, updatePassword);

export default router;