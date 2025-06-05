import { Request, Response, NextFunction } from 'express';
import { logger } from '../utils/logger';

// Custom error class for API errors
export class ApiError extends Error {
  statusCode: number;
  
  constructor(statusCode: number, message: string) {
    super(message);
    this.statusCode = statusCode;
    this.name = this.constructor.name;
    Error.captureStackTrace(this, this.constructor);
  }
}

// Error handling middleware
export const errorHandler = (
  err: Error | ApiError, 
  req: Request, 
  res: Response, 
  next: NextFunction
) => {
  logger.error(`${err.name}: ${err.message}`, { 
    error: err.stack,
    method: req.method,
    path: req.path,
    body: req.body,
    query: req.query
  });

  // Default status code and message
  let statusCode = 500;
  let message = 'Internal Server Error';
  
  // If it's an ApiError, use its status code and message
  if (err instanceof ApiError) {
    statusCode = err.statusCode;
    message = err.message;
  } else if (process.env.NODE_ENV === 'development') {
    // In development, expose the error message
    message = err.message;
  }

  res.status(statusCode).json({
    status: 'error',
    statusCode,
    message
  });
};