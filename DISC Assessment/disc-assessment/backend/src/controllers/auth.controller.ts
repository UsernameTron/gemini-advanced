import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';
import { config } from '../config';
import { UserModel, User } from '../models/user.model';
import { ApiError } from '../middleware/error.middleware';

// Generate JWT Token
const generateToken = (user: Partial<User>): string => {
  return jwt.sign(
    { id: user.id, email: user.email, role: user.role },
    config.jwt.secret,
    { expiresIn: config.jwt.expiresIn }
  );
};

// Register a new user
export const register = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { email, password, first_name, last_name, role } = req.body;

    // Check if user already exists
    const existingUser = await UserModel.getUserByEmail(email);
    if (existingUser) {
      return next(new ApiError(400, 'User already exists'));
    }

    // Create user
    const user = await UserModel.createUser({
      email,
      password,
      first_name,
      last_name,
      role: role || 'candidate' // Default to candidate role
    });

    // Generate JWT token
    const token = generateToken(user);

    // Remove password hash from response
    const { password_hash, ...userWithoutPassword } = user;

    res.status(201).json({
      status: 'success',
      data: {
        user: userWithoutPassword,
        token
      }
    });
  } catch (error) {
    next(error);
  }
};

// Login user
export const login = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { email, password } = req.body;

    // Check if email and password are provided
    if (!email || !password) {
      return next(new ApiError(400, 'Please provide email and password'));
    }

    // Check if user exists
    const user = await UserModel.getUserByEmail(email);
    if (!user) {
      return next(new ApiError(401, 'Invalid credentials'));
    }

    // Check if password is correct
    const isMatch = await UserModel.comparePassword(password, user.password_hash);
    if (!isMatch) {
      return next(new ApiError(401, 'Invalid credentials'));
    }

    // Generate JWT token
    const token = generateToken(user);

    // Remove password hash from response
    const { password_hash, ...userWithoutPassword } = user;

    res.status(200).json({
      status: 'success',
      data: {
        user: userWithoutPassword,
        token
      }
    });
  } catch (error) {
    next(error);
  }
};

// Get current user profile
export const getMe = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    // User should be attached to request by auth middleware
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    const user = await UserModel.getUserById(req.user.id);
    if (!user) {
      return next(new ApiError(404, 'User not found'));
    }

    // Remove password hash from response
    const { password_hash, ...userWithoutPassword } = user;

    res.status(200).json({
      status: 'success',
      data: {
        user: userWithoutPassword
      }
    });
  } catch (error) {
    next(error);
  }
};

// Update user password
export const updatePassword = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { currentPassword, newPassword } = req.body;

    // Check if user is authenticated
    if (!req.user) {
      return next(new ApiError(401, 'Not authorized'));
    }

    // Get user from database
    const user = await UserModel.getUserById(req.user.id);
    if (!user) {
      return next(new ApiError(404, 'User not found'));
    }

    // Check if current password is correct
    const isMatch = await UserModel.comparePassword(currentPassword, user.password_hash);
    if (!isMatch) {
      return next(new ApiError(401, 'Current password is incorrect'));
    }

    // Update password
    await UserModel.updateUser(user.id, { password: newPassword });

    // Generate new token
    const token = generateToken(user);

    res.status(200).json({
      status: 'success',
      data: {
        token
      }
    });
  } catch (error) {
    next(error);
  }
};

// Forgot password - initiates reset process
export const forgotPassword = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { email } = req.body;

    // Check if user exists
    const user = await UserModel.getUserByEmail(email);
    if (!user) {
      return next(new ApiError(404, 'No user with that email'));
    }

    // TODO: Implement password reset token generation and email sending
    // For now, we'll just return a success message

    res.status(200).json({
      status: 'success',
      message: 'Password reset instructions sent to email'
    });
  } catch (error) {
    next(error);
  }
};

// Reset password using reset token
export const resetPassword = async (
  req: Request,
  res: Response,
  next: NextFunction
) => {
  try {
    const { resetToken, newPassword } = req.body;

    // TODO: Implement actual token validation and password reset
    // For now, return an error
    return next(new ApiError(501, 'Password reset functionality not yet implemented'));
  } catch (error) {
    next(error);
  }
};