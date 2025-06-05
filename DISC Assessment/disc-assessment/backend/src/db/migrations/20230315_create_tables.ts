import { Knex } from 'knex';

export async function up(knex: Knex): Promise<void> {
  // 1. Create Users Table
  await knex.schema.createTable('users', (table) => {
    table.increments('id').primary();
    table.string('email', 255).notNullable().unique();
    table.string('password_hash', 255).notNullable();
    table.enu('role', ['admin', 'hr', 'candidate']).notNullable();
    table.string('first_name', 100).notNullable();
    table.string('last_name', 100).notNullable();
    table.timestamp('created_at').defaultTo(knex.fn.now());
    table.timestamp('updated_at').defaultTo(knex.fn.now());
  });

  // 2. Create Assessments Table
  await knex.schema.createTable('assessments', (table) => {
    table.increments('id').primary();
    table.integer('candidate_id').unsigned().references('id').inTable('users');
    table.enu('position_level', ['level_1', 'level_2', 'level_3']).notNullable();
    table.enu('status', ['in_progress', 'completed', 'expired']).defaultTo('in_progress');
    table.timestamp('started_at').defaultTo(knex.fn.now());
    table.timestamp('completed_at').nullable();
    table.integer('dominance_score').defaultTo(0);
    table.integer('influence_score').defaultTo(0);
    table.integer('steadiness_score').defaultTo(0);
    table.integer('conscientiousness_score').defaultTo(0);
    table.integer('total_time_minutes').defaultTo(0);
  });

  // 3. Create Questions Table
  await knex.schema.createTable('questions', (table) => {
    table.increments('id').primary();
    table.integer('question_number').notNullable().unique();
    table.text('scenario_text').notNullable();
    table.text('option_a').notNullable();
    table.text('option_b').notNullable();
    table.text('option_c').notNullable();
    table.text('option_d').notNullable();
    table.string('dimension_a', 1).notNullable().checkIn(['D', 'I', 'S', 'C']);
    table.string('dimension_b', 1).notNullable().checkIn(['D', 'I', 'S', 'C']);
    table.string('dimension_c', 1).notNullable().checkIn(['D', 'I', 'S', 'C']);
    table.string('dimension_d', 1).notNullable().checkIn(['D', 'I', 'S', 'C']);
    table.timestamp('created_at').defaultTo(knex.fn.now());
  });

  // 4. Create Assessment Responses Table
  await knex.schema.createTable('assessment_responses', (table) => {
    table.increments('id').primary();
    table.integer('assessment_id').unsigned().references('id').inTable('assessments');
    table.integer('question_number').notNullable();
    table.string('selected_option', 1).notNullable().checkIn(['A', 'B', 'C', 'D']);
    table.integer('response_time_seconds').notNullable();
    table.timestamp('created_at').defaultTo(knex.fn.now());
  });
}

export async function down(knex: Knex): Promise<void> {
  // Drop tables in reverse order
  await knex.schema.dropTableIfExists('assessment_responses');
  await knex.schema.dropTableIfExists('questions');
  await knex.schema.dropTableIfExists('assessments');
  await knex.schema.dropTableIfExists('users');
}