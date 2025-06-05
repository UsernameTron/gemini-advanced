import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

const Register: React.FC = () => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    email: '',
    password: '',
    confirmPassword: '',
    role: 'candidate'
  });
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFormData({ ...formData, [name]: value });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');
    
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      return;
    }
    
    try {
      // TODO: Implement actual registration API call
      console.log('Register with:', formData);
      
      // Simulate successful registration
      navigate('/login');
    } catch (err) {
      setError('Registration failed. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center p-4">
      <div className="glassmorphism p-8 max-w-md w-full">
        <h2 className="text-h2 font-bold gradient-text mb-6 text-center">Register</h2>
        
        {error && (
          <div className="bg-red-500/20 border border-red-500 text-red-200 p-3 rounded-lg mb-4">
            {error}
          </div>
        )}
        
        <form onSubmit={handleSubmit}>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div>
              <label htmlFor="firstName" className="block text-text-secondary mb-2">
                First Name
              </label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
                required
              />
            </div>
            
            <div>
              <label htmlFor="lastName" className="block text-text-secondary mb-2">
                Last Name
              </label>
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
                required
              />
            </div>
          </div>
          
          <div className="mb-4">
            <label htmlFor="email" className="block text-text-secondary mb-2">
              Email
            </label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="password" className="block text-text-secondary mb-2">
              Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
              required
            />
          </div>
          
          <div className="mb-4">
            <label htmlFor="confirmPassword" className="block text-text-secondary mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              id="confirmPassword"
              name="confirmPassword"
              value={formData.confirmPassword}
              onChange={handleChange}
              className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
              required
            />
          </div>
          
          <div className="mb-6">
            <label htmlFor="role" className="block text-text-secondary mb-2">
              Role
            </label>
            <select
              id="role"
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full bg-background-dark/50 border border-white/10 rounded-lg p-3 text-white"
              required
            >
              <option value="candidate">Candidate</option>
              <option value="hr">HR Personnel</option>
              <option value="admin">Administrator</option>
            </select>
          </div>
          
          <button
            type="submit"
            className="w-full btn-primary mb-4"
          >
            Register
          </button>
          
          <div className="text-center text-text-secondary">
            Already have an account?{' '}
            <Link to="/login" className="text-primary-blue hover:underline">
              Login
            </Link>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Register;