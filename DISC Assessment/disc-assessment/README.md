# DISC Assessment Application

A comprehensive web application for conducting DISC-style behavioral assessments specifically designed for ISPN technician hiring across Levels 1-3.

## Features

- Interactive 15-question scenario-based assessment
- Real-time DISC dimension scoring
- Technician level recommendations based on DISC profile
- User management with role-based access control
- Modern UI with glassmorphism effects and animations
- Detailed reporting and analytics

## Tech Stack

- **Frontend**: React with TypeScript, Tailwind CSS
- **Backend**: Node.js with Express
- **Database**: PostgreSQL (production), SQLite (development)
- **Authentication**: JWT-based authentication system

## Project Structure

```
disc-assessment/
├── frontend/           # React frontend application
├── backend/            # Node.js backend API
└── shared/             # Shared types and utilities
```

## Installation

### Prerequisites

- Node.js (v14 or later)
- npm (v6 or later)
- SQLite (for development)
- PostgreSQL (for production)

### Setup

1. Clone the repository:

```bash
git clone <repository-url>
cd disc-assessment
```

2. Install dependencies for both frontend and backend:

```bash
npm run install:all
```

3. Set up environment variables:

```bash
# In the backend directory
cp .env.example .env
# Edit .env with your specific configuration
```

4. Set up the database:

```bash
cd backend
npm run migrate
npm run seed
```

## Running the Application Locally

### Development Mode

To run both frontend and backend concurrently:

```bash
npm run dev
```

Or run them separately:

```bash
# Run frontend only
npm run frontend

# Run backend only
npm run backend
```

The frontend will be available at http://localhost:3000 and the API at http://localhost:5000.

### Production Mode

1. Build the application:

```bash
npm run build
```

2. Start the production server:

```bash
npm start
```

## API Documentation

The API provides the following endpoints:

### Authentication
- `POST /api/auth/login`
- `POST /api/auth/register`
- `POST /api/auth/forgot-password`
- `POST /api/auth/reset-password`
- `GET /api/auth/me`
- `POST /api/auth/update-password`

### Assessments
- `GET /api/assessments`
- `POST /api/assessments`
- `GET /api/assessments/:id`
- `PUT /api/assessments/:id`
- `DELETE /api/assessments/:id`
- `GET /api/assessments/questions/all`
- `POST /api/assessments/responses`
- `POST /api/assessments/:id/complete`
- `GET /api/assessments/:id/results`

### Reporting
- `GET /api/reports/candidates`
- `GET /api/reports/analytics`
- `POST /api/reports/export`
- `POST /api/reports/comparisons`

## User Roles

- **Admin**: Full access to all features
- **HR**: Access to candidate management, assessments, and reports
- **Candidate**: Can complete assessments and view their own results

## DISC Dimensions

- **D - Dominance**: Focus on accomplishing results and the bottom line
- **I - Influence**: Focus on influencing or persuading others and openness
- **S - Steadiness**: Focus on cooperation, sincerity, and dependability
- **C - Conscientiousness**: Focus on quality, accuracy, and competency

## License

[License information here]