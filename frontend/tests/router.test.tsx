import { render, screen } from '@testing-library/react';
import { describe, it, expect, beforeEach } from 'vitest';
import { Router } from '@/router';
import { AuthProvider } from '@/lib/auth-store';

describe('Client Router & Protected Route Guards Tests', () => {
  beforeEach(() => {
    localStorage.clear();
  });

  it('renders landing page on root path', () => {
    window.history.pushState({}, '', '/');
    render(
      <AuthProvider>
        <Router />
      </AuthProvider>
    );
    expect(screen.getByText(/The Autonomous AI Commerce/i)).toBeInTheDocument();
  });

  it('renders login page on /login path when unauthenticated', () => {
    window.history.pushState({}, '', '/login');
    render(
      <AuthProvider>
        <Router />
      </AuthProvider>
    );
    expect(screen.getByRole('heading', { name: /Merchant Sign In/i })).toBeInTheDocument();
  });

  it('renders signup page on /signup path when unauthenticated', () => {
    window.history.pushState({}, '', '/signup');
    render(
      <AuthProvider>
        <Router />
      </AuthProvider>
    );
    expect(screen.getByRole('heading', { name: /Register Merchant/i })).toBeInTheDocument();
  });

  it('redirects unauthenticated access from /dashboard to login', () => {
    window.history.pushState({}, '', '/dashboard');
    render(
      <AuthProvider>
        <Router />
      </AuthProvider>
    );
    expect(screen.getByRole('heading', { name: /Merchant Sign In/i })).toBeInTheDocument();
  });
});
