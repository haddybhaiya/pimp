import React from 'react';
import { AuthProvider } from '@/lib/auth-store';
import { Router } from '@/router';

export const App: React.FC = () => {
  return (
    <AuthProvider>
      <Router />
    </AuthProvider>
  );
};
