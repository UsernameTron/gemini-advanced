import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="glassmorphism p-8 max-w-4xl w-full">
        <h1 className="text-h1 font-bold gradient-text mb-6 text-center">
          DISC Technician Assessment
        </h1>
        <p className="text-text-secondary text-center mb-8">
          A comprehensive assessment tool for evaluating ISPN technician candidates across Levels 1-3
        </p>
        
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/login" className="btn-primary text-center">
            Login
          </Link>
          <Link to="/register" className="border border-primary-blue py-2 px-4 rounded-lg text-primary-blue font-medium hover:bg-primary-blue/10 transition-colors duration-300 text-center">
            Register
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Home;