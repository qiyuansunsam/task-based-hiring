import React from 'react';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './components/ui/Toast';
import Login from './components/auth/Login';
import CompanyDashboard from './components/company/CompanyDashboard';
import ApplicantDashboard from './components/applicant/ApplicantDashboard';

// Helper component to consume auth context
const AuthContextConsumer = () => {
  const { user } = useAuth();
  
  if (!user) {
    return <Login />;
  }
  
  if (user.type === 'company') {
    return <CompanyDashboard />;
  }
  
  return <ApplicantDashboard />;
};

// Main App Component
export default function App() {
  return (
    <ToastProvider>
      <AuthProvider>
        <AuthContextConsumer />
      </AuthProvider>
    </ToastProvider>
  );
}