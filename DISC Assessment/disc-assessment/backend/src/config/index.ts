import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config();

export const config = {
  // Application
  env: process.env.NODE_ENV || 'development',
  port: parseInt(process.env.PORT || '5000', 10),
  
  // Database
  db: {
    client: process.env.DB_CLIENT || 'sqlite3',
    connection: {
      filename: process.env.DB_CLIENT === 'sqlite3' 
        ? path.join(__dirname, `../../${process.env.DB_NAME || 'disc_assessment_dev'}.sqlite`) 
        : {
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME,
            port: parseInt(process.env.DB_PORT || '5432', 10),
          },
    },
    migrations: {
      directory: path.join(__dirname, '../db/migrations'),
    },
    seeds: {
      directory: path.join(__dirname, '../db/seeds'),
    },
    useNullAsDefault: process.env.DB_CLIENT === 'sqlite3',
  },
  
  // Authentication
  jwt: {
    secret: process.env.JWT_SECRET || 'your_jwt_secret_key',
    expiresIn: process.env.JWT_EXPIRES_IN || '7d',
  },
  
  // API
  api: {
    prefix: process.env.API_PREFIX || '/api',
  },
  
  // Logging
  logLevel: process.env.LOG_LEVEL || 'info',
};