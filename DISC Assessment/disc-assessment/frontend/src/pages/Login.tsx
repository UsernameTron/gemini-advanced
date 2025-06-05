import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Login: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    try {
      // TODO: Implement actual login API call
      console.log('Login with:', { email, password });
      
      // Simulate successful login
      localStorage.setItem('token', 'sample-jwt-token');
      navigate('/dashboard');
    } catch (err) {
      setError('Invalid email or password');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glassmorphism p-8 max-w-md w-full">
        <h2 className="text-h2 font-bold gradient-text mb-6 text-center">Login</h2>
        
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-200 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="email" className="block text-text-secondary mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="password" className="block text-text-secondary mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
              required
            />
          </div>
          
          <button
            type="submit"
            className="w-full btn-primary mb-4"
          >
            Login
          </button>
          
          <div className="text-center text-text-secondary">
            Don't have an account?{' '}
            <Link to="/register" className="text-primary-blue hover:underline">
              Register
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Login;