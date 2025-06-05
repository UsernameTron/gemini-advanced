import dotenv from 'dotenv';
import path from 'path';

// Load environment variables
dotenv.config();

// Define configuration for different environments
const config = {
  development: {
    client: process.env.DB_CLIENT || 'sqlite3',
    connection: process.env.DB_CLIENT === 'sqlite3' 
      ? { filename: path.join(__dirname, `${process.env.DB_NAME || 'disc_assessment_dev'}.sqlite`) }
      : {
          host: process.env.DB_HOST,
          user: process.env.DB_USER,
          password: process.env.DB_PASSWORD,
          database: process.env.DB_NAME,
          port: parseInt(process.env.DB_PORT || '5432', 10),
        },
    migrations: {
      directory: path.join(__dirname, 'src/db/migrations'),
    },
    seeds: {
      directory: path.join(__dirname, 'src/db/seeds'),
    },
    useNullAsDefault: process.env.DB_CLIENT === 'sqlite3',
  },
  
  test: {
    client: 'sqlite3',
    connection: {
      filename: ':memory:',
    },
    migrations: {
      directory: path.join(__dirname, 'src/db/migrations'),
    },
    seeds: {
      directory: path.join(__dirname, 'src/db/seeds/test'),
    },
    useNullAsDefault: true,
  },
  
  production: {
    client: 'pg',
    connection: {
      host: process.env.DB_HOST,
      user: process.env.DB_USER,
      password: process.env.DB_PASSWORD,
      database: process.env.DB_NAME,
      port: parseInt(process.env.DB_PORT || '5432', 10),
      ssl: { rejectUnauthorized: false },
    },
    migrations: {
      directory: path.join(__dirname, 'src/db/migrations'),
    },
    seeds: {
      directory: path.join(__dirname, 'src/db/seeds/production'),
    },
    pool: {
      min: 2,
      max: 10,
    },
  },
};

// Export the configuration for the current environment
export default config;