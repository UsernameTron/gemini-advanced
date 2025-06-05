import knex from 'knex';
import { config } from '../config';

// Initialize knex connection
const db = knex(config.db);

export default db;