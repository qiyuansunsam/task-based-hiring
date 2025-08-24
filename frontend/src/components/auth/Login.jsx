import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import Button from '../ui/Button';
import Input from '../ui/Input';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const { login, loading } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    const result = await login(email, password);
    if (!result.success) {
      setError(result.message);
    }
  };

  const demoAccounts = [
    { email: 'demo@test.com', type: 'Company' },
    { email: 'custom@test.com', type: 'Applicant' },
    { email: 'gpt@test.com', type: 'Applicant' },
    { email: 'gemini@test.com', type: 'Applicant' },
    { email: 'deepseek@test.com', type: 'Applicant' }
  ];

  return (
    <div className="min-h-screen bg-black flex items-center justify-center">
      <div className="w-full max-w-md">
        <div className="bg-zinc-900 rounded-2xl border border-zinc-800 p-8">
          <h2 className="text-3xl font-bold text-white mb-2">
            Welcome to <span className="text-purple-500">SkillsFoundry</span>
          </h2>
          <p className="text-zinc-400 mb-8">AI-Powered Skills Assessment Platform</p>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Email"
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />
            
            <Input
              label="Password"
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
            />
            
            {error && (
              <div className="text-red-500 text-sm">{error}</div>
            )}
            
            <Button
              type="submit"
              disabled={loading}
              className="w-full"
              size="lg"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </Button>
          </form>

          <div className="mt-8">
            <p className="text-zinc-500 text-sm mb-3">Demo Accounts (Password: 123)</p>
            <div className="space-y-2">
              {demoAccounts.map(acc => (
                <button
                  key={acc.email}
                  onClick={() => {
                    setEmail(acc.email);
                    setPassword('123');
                  }}
                  className="w-full px-3 py-2 bg-zinc-800 hover:bg-zinc-700 rounded-lg text-left text-sm transition flex justify-between items-center"
                >
                  <span className="text-zinc-300">{acc.email}</span>
                  <span className="text-purple-400 text-xs">{acc.type}</span>
                </button>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Login;
