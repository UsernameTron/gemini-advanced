import db from '../db';
import bcrypt from 'bcryptjs';

export interface User {
  id: number;
  email: string;
  password_hash: string;
  role: 'admin' | 'hr' | 'candidate';
  first_name: string;
  last_name: string;
  created_at: string;
  updated_at: string;
}

export interface UserInput {
  email: string;
  password: string;
  role: 'admin' | 'hr' | 'candidate';
  first_name: string;
  last_name: string;
}

// User model with static methods
export const UserModel = {
  // Get all users
  async getAllUsers(): Promise<User[]> {
    return db('users').select('*');
  },

  // Get user by ID
  async getUserById(id: number): Promise<User | null> {
    const user = await db('users').where({ id }).first();
    return user || null;
  },

  // Get user by email
  async getUserByEmail(email: string): Promise<User | null> {
    const user = await db('users').where({ email }).first();
    return user || null;
  },

  // Create a new user
  async createUser(userData: UserInput): Promise<User> {
    // Hash password
    const salt = await bcrypt.genSalt(10);
    const password_hash = await bcrypt.hash(userData.password, salt);

    // Insert user into database
    const [id] = await db('users').insert({
      email: userData.email,
      password_hash,
      role: userData.role,
      first_name: userData.first_name,
      last_name: userData.last_name,
      created_at: db.fn.now(),
      updated_at: db.fn.now()
    });

    // Return the newly created user
    return this.getUserById(id) as Promise<User>;
  },

  // Update a user
  async updateUser(id: number, userData: Partial<UserInput>): Promise<User | null> {
    // Prepare update data
    const updateData: any = { ...userData, updated_at: db.fn.now() };
    
    // If password is being updated, hash it
    if (userData.password) {
      const salt = await bcrypt.genSalt(10);
      updateData.password_hash = await bcrypt.hash(userData.password, salt);
      delete updateData.password;
    }

    // Update user in database
    await db('users').where({ id }).update(updateData);

    // Return the updated user
    return this.getUserById(id);
  },

  // Delete a user
  async deleteUser(id: number): Promise<boolean> {
    const deleted = await db('users').where({ id }).del();
    return deleted > 0;
  },

  // Compare password
  async comparePassword(providedPassword: string, storedHash: string): Promise<boolean> {
    return bcrypt.compare(providedPassword, storedHash);
  }
};