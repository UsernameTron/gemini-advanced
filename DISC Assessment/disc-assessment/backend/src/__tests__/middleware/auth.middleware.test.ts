import { Request, Response } from 'express';
import { protect, restrictTo } from '../../middleware/auth.middleware';
import jwt from 'jsonwebtoken';
import { ApiError } from '../../middleware/error.middleware';

// Mock jwt
jest.mock('jsonwebtoken');

describe('Auth Middleware', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: jest.Mock;

  beforeEach(() => {
    mockRequest = {
      headers: {},
    };
    mockResponse = {};
    nextFunction = jest.fn();
  });

  describe('protect', () => {
    it('should call next() if token is valid', async () => {
      // Arrange
      const mockUser = {
        id: 1,
        email: 'test@example.com',
        role: 'candidate',
      };

      mockRequest.headers = {
        authorization: 'Bearer valid_token',
      };

      (jwt.verify as jest.Mock).mockReturnValueOnce(mockUser);

      // Act
      await protect(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(jwt.verify).toHaveBeenCalledWith(
        'valid_token',
        expect.any(String)
      );
      expect(mockRequest.user).toEqual(mockUser);
      expect(nextFunction).toHaveBeenCalledWith();
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(ApiError));
    });

    it('should return 401 if no token is provided', async () => {
      // Arrange
      mockRequest.headers = {};

      // Act
      await protect(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(jwt.verify).not.toHaveBeenCalled();
      expect(nextFunction).toHaveBeenCalledWith(expect.any(ApiError));
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(401);
      expect(nextFunction.mock.calls[0][0].message).toBe(
        'Not authorized to access this route'
      );
    });

    it('should return 401 if token is invalid', async () => {
      // Arrange
      mockRequest.headers = {
        authorization: 'Bearer invalid_token',
      };

      (jwt.verify as jest.Mock).mockImplementationOnce(() => {
        throw new Error('Invalid token');
      });

      // Act
      await protect(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(jwt.verify).toHaveBeenCalledWith(
        'invalid_token',
        expect.any(String)
      );
      expect(nextFunction).toHaveBeenCalledWith(expect.any(ApiError));
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(401);
      expect(nextFunction.mock.calls[0][0].message).toBe(
        'Not authorized to access this route'
      );
    });
  });

  describe('restrictTo', () => {
    it('should call next() if user has the required role', () => {
      // Arrange
      mockRequest.user = {
        id: 1,
        email: 'admin@example.com',
        role: 'admin',
      };

      const restrictToAdmin = restrictTo('admin');

      // Act
      restrictToAdmin(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(nextFunction).toHaveBeenCalledWith();
      expect(nextFunction).not.toHaveBeenCalledWith(expect.any(ApiError));
    });

    it('should return 403 if user does not have the required role', () => {
      // Arrange
      mockRequest.user = {
        id: 1,
        email: 'candidate@example.com',
        role: 'candidate',
      };

      const restrictToAdmin = restrictTo('admin', 'hr');

      // Act
      restrictToAdmin(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(nextFunction).toHaveBeenCalledWith(expect.any(ApiError));
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(403);
      expect(nextFunction.mock.calls[0][0].message).toBe(
        'You do not have permission to perform this action'
      );
    });

    it('should return 401 if user is not authenticated', () => {
      // Arrange
      mockRequest.user = undefined;

      const restrictToAdmin = restrictTo('admin');

      // Act
      restrictToAdmin(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(nextFunction).toHaveBeenCalledWith(expect.any(ApiError));
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(401);
      expect(nextFunction.mock.calls[0][0].message).toBe(
        'Not authorized to access this route'
      );
    });
  });
});