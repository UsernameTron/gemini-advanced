import { Request, Response } from 'express';
import { register, login, getMe } from '../../controllers/auth.controller';
import { UserModel } from '../../models/user.model';
import { ApiError } from '../../middleware/error.middleware';

// Mock the UserModel
jest.mock('../../models/user.model', () => ({
  UserModel: {
    getUserByEmail: jest.fn(),
    createUser: jest.fn(),
    getUserById: jest.fn(),
    comparePassword: jest.fn(),
  },
}));

// Mock jwt
jest.mock('jsonwebtoken', () => ({
  sign: jest.fn().mockReturnValue('mock-token'),
}));

describe('Auth Controller', () => {
  let mockRequest: Partial<Request>;
  let mockResponse: Partial<Response>;
  let nextFunction: jest.Mock;

  beforeEach(() => {
    mockRequest = {};
    mockResponse = {
      status: jest.fn().mockReturnThis(),
      json: jest.fn(),
    };
    nextFunction = jest.fn();
  });

  describe('register', () => {
    it('should create a new user and return 201 status', async () => {
      // Arrange
      const newUser = {
        email: 'test@example.com',
        password: 'password123',
        first_name: 'Test',
        last_name: 'User',
        role: 'candidate',
      };

      mockRequest.body = newUser;

      // Mock user doesn't exist
      (UserModel.getUserByEmail as jest.Mock).mockResolvedValue(null);

      // Mock user creation
      (UserModel.createUser as jest.Mock).mockResolvedValue({
        id: 1,
        email: newUser.email,
        first_name: newUser.first_name,
        last_name: newUser.last_name,
        role: newUser.role,
        password_hash: 'hashed_password',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      });

      // Act
      await register(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(UserModel.getUserByEmail).toHaveBeenCalledWith(newUser.email);
      expect(UserModel.createUser).toHaveBeenCalledWith(newUser);
      expect(mockResponse.status).toHaveBeenCalledWith(201);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'success',
          data: expect.objectContaining({
            user: expect.objectContaining({
              email: newUser.email,
            }),
            token: 'mock-token',
          }),
        })
      );
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should return 400 if user already exists', async () => {
      // Arrange
      const existingUser = {
        email: 'existing@example.com',
        password: 'password123',
        first_name: 'Existing',
        last_name: 'User',
        role: 'candidate',
      };

      mockRequest.body = existingUser;

      // Mock user exists
      (UserModel.getUserByEmail as jest.Mock).mockResolvedValue({
        id: 1,
        email: existingUser.email,
      });

      // Act
      await register(
        mockRequest as Request,
        mockResponse as Response,
        nextFunction
      );

      // Assert
      expect(UserModel.getUserByEmail).toHaveBeenCalledWith(existingUser.email);
      expect(UserModel.createUser).not.toHaveBeenCalled();
      expect(nextFunction).toHaveBeenCalledWith(
        expect.any(ApiError)
      );
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(400);
      expect(nextFunction.mock.calls[0][0].message).toBe('User already exists');
    });
  });

  describe('login', () => {
    it('should login user and return token', async () => {
      // Arrange
      const loginData = {
        email: 'test@example.com',
        password: 'password123',
      };

      const userData = {
        id: 1,
        email: loginData.email,
        password_hash: 'hashed_password',
        role: 'candidate',
        first_name: 'Test',
        last_name: 'User',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mockRequest.body = loginData;

      // Mock user exists
      (UserModel.getUserByEmail as jest.Mock).mockResolvedValue(userData);

      // Mock password comparison successful
      (UserModel.comparePassword as jest.Mock).mockResolvedValue(true);

      // Act
      await login(mockRequest as Request, mockResponse as Response, nextFunction);

      // Assert
      expect(UserModel.getUserByEmail).toHaveBeenCalledWith(loginData.email);
      expect(UserModel.comparePassword).toHaveBeenCalledWith(
        loginData.password,
        userData.password_hash
      );
      expect(mockResponse.status).toHaveBeenCalledWith(200);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'success',
          data: expect.objectContaining({
            user: expect.objectContaining({
              email: userData.email,
            }),
            token: 'mock-token',
          }),
        })
      );
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should return 401 if password is incorrect', async () => {
      // Arrange
      const loginData = {
        email: 'test@example.com',
        password: 'wrong_password',
      };

      const userData = {
        id: 1,
        email: loginData.email,
        password_hash: 'hashed_password',
      };

      mockRequest.body = loginData;

      // Mock user exists
      (UserModel.getUserByEmail as jest.Mock).mockResolvedValue(userData);

      // Mock password comparison failed
      (UserModel.comparePassword as jest.Mock).mockResolvedValue(false);

      // Act
      await login(mockRequest as Request, mockResponse as Response, nextFunction);

      // Assert
      expect(UserModel.getUserByEmail).toHaveBeenCalledWith(loginData.email);
      expect(UserModel.comparePassword).toHaveBeenCalledWith(
        loginData.password,
        userData.password_hash
      );
      expect(nextFunction).toHaveBeenCalledWith(
        expect.any(ApiError)
      );
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(401);
      expect(nextFunction.mock.calls[0][0].message).toBe('Invalid credentials');
    });
  });

  describe('getMe', () => {
    it('should return current user profile', async () => {
      // Arrange
      const userData = {
        id: 1,
        email: 'test@example.com',
        password_hash: 'hashed_password',
        role: 'candidate',
        first_name: 'Test',
        last_name: 'User',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };

      mockRequest.user = {
        id: userData.id,
        email: userData.email,
        role: userData.role,
      };

      // Mock getUserById
      (UserModel.getUserById as jest.Mock).mockResolvedValue(userData);

      // Act
      await getMe(mockRequest as Request, mockResponse as Response, nextFunction);

      // Assert
      expect(UserModel.getUserById).toHaveBeenCalledWith(userData.id);
      expect(mockResponse.status).toHaveBeenCalledWith(200);
      expect(mockResponse.json).toHaveBeenCalledWith(
        expect.objectContaining({
          status: 'success',
          data: expect.objectContaining({
            user: expect.objectContaining({
              email: userData.email,
              role: userData.role,
            }),
          }),
        })
      );
      // Should not contain password_hash
      expect(mockResponse.json).not.toHaveBeenCalledWith(
        expect.objectContaining({
          data: expect.objectContaining({
            user: expect.objectContaining({
              password_hash: expect.anything(),
            }),
          }),
        })
      );
      expect(nextFunction).not.toHaveBeenCalled();
    });

    it('should return 401 if user is not authenticated', async () => {
      // Arrange
      mockRequest.user = undefined;

      // Act
      await getMe(mockRequest as Request, mockResponse as Response, nextFunction);

      // Assert
      expect(UserModel.getUserById).not.toHaveBeenCalled();
      expect(nextFunction).toHaveBeenCalledWith(
        expect.any(ApiError)
      );
      expect(nextFunction.mock.calls[0][0].statusCode).toBe(401);
      expect(nextFunction.mock.calls[0][0].message).toBe('Not authorized');
    });
  });
});