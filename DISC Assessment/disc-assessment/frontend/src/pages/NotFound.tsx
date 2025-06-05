import React from 'react';
import { Link } from 'react-router-dom';

const NotFound: React.FC = () => {
  return (
    <div className="min-h-screen flex flex-col items-center justify-center p-4">
      <div className="glassmorphism p-8 max-w-md w-full text-center">
        <h1 className="text-h1 font-bold gradient-text mb-6">404</h1>
        <h2 className="text-h3 font-medium text-white mb-4">Page Not Found</h2>
        <p className="text-text-secondary mb-8">
          The page you are looking for doesn't exist or has been moved.
        </p>
        <Link to="/" className="btn-primary inline-block">
          Go Home
        </Link>
      </div>
    </div>
  );
};

export default NotFound;