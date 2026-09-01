import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { AuthProvider, useAuth } from '@/lib/auth-store';
import { api } from '@/lib/api-client';

describe('AuthStore & Session Management Unit Tests', () => {
  beforeEach(() => {
    localStorage.clear();
    vi.restoreAllMocks();
  });

  const wrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  it('starts unauthenticated when localStorage is empty', () => {
    const { result } = renderHook(() => useAuth(), { wrapper });
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.merchant).toBeNull();
  });

  it('successfully logs in merchant without persisting the HttpOnly session token', async () => {
    vi.spyOn(api, 'login').mockResolvedValue({
      merchant_id: '11111111-1111-1111-1111-111111111111',
      name: 'Apex Athletic',
      slug: 'apex-athletic',
      status: 'ACTIVE',
      currency: 'INR',
      token: null,
      expires_at: new Date(Date.now() + 86400000).toISOString(),
      onboarding_completed: true,
      policies: {
        autonomy_level: 1,
        max_discount_percentage: 15.0,
        min_margin_percentage: 20.0,
        max_single_transaction_paise: 5000000,
        policy_hash: 'abcdef1234567890',
        protocol_version: '2026-03-01',
      },
    });

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login({ slug: 'apex-athletic' });
    });

    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.merchant?.name).toBe('Apex Athletic');
    expect(localStorage.getItem('arm_auth_token')).toBeNull();
  });

  it('clears session on logout', async () => {
    vi.spyOn(api, 'logout').mockResolvedValue(undefined);
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.logout();
    });

    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.merchant).toBeNull();
    expect(localStorage.getItem('arm_auth_token')).toBeNull();
  });
});
