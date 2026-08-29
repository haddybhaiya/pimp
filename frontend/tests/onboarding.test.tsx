import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { OnboardingPage } from '@/pages/onboarding';
import { AuthProvider } from '@/lib/auth-store';

describe('Onboarding Wizard Flow Tests', () => {
  const onNavigate = vi.fn();

  const renderWithAuth = (component: React.ReactNode) => {
    return render(<AuthProvider>{component}</AuthProvider>);
  };

  it('progresses through the 4 setup steps correctly', async () => {
    renderWithAuth(<OnboardingPage onNavigate={onNavigate} />);

    // Step 1: Identity
    expect(screen.getByText(/Store Identity & Branding/i)).toBeInTheDocument();
    const continueBtn = screen.getByRole('button', { name: /continue/i });
    fireEvent.click(continueBtn);

    // Step 2: Razorpay
    expect(screen.getByText(/Razorpay Settlement Gateway/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));

    // Step 3: Policies
    expect(screen.getByText(/Autonomous Policy Bounds/i)).toBeInTheDocument();
    fireEvent.click(screen.getByRole('button', { name: /continue/i }));

    // Step 4: Review & Activate
    expect(screen.getByText(/Review & Activate Control Plane/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /complete & launch/i })).toBeInTheDocument();
  });
});
