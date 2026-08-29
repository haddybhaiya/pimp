import React, { createContext, useContext, useEffect, useState } from 'react';
import { MerchantProfile, LoginCredentials, SignupPayload } from '@/types/auth';
import { api } from '@/lib/api-client';

interface AuthContextType {
  merchant: MerchantProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionExpired: boolean;
  login: (creds: LoginCredentials) => Promise<void>;
  signup: (payload: SignupPayload) => Promise<void>;
  logout: () => void;
  updateProfile: (profile: Partial<MerchantProfile>) => void;
  refreshProfile: () => Promise<void>;
  dismissExpiredDialog: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY_TOKEN = 'arm_auth_token';
const STORAGE_KEY_MERCHANT = 'arm_merchant_data';
const STORAGE_KEY_EXPIRY = 'arm_auth_expiry';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [merchant, setMerchant] = useState<MerchantProfile | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_MERCHANT);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem(STORAGE_KEY_TOKEN);
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [sessionExpired, setSessionExpired] = useState<boolean>(false);

  useEffect(() => {
    if (token && merchant) {
      api.setAuth(merchant.merchantId, token);
      const exp = localStorage.getItem(STORAGE_KEY_EXPIRY);
      if (exp && new Date(exp).getTime() < Date.now()) {
        setSessionExpired(true);
        logout();
      }
    }

    api.onUnauthorized(() => {
      setSessionExpired(true);
      logout();
    });

    setIsLoading(false);
  }, []);

  const login = async (creds: LoginCredentials) => {
    setIsLoading(true);
    try {
      const res = await api.login(creds);
      const profile: MerchantProfile = {
        merchantId: res.merchant_id,
        name: res.name,
        slug: res.slug,
        status: res.status,
        currency: res.currency,
        rzpKeyId: creds.rzpKeyId || 'rzp_test_placeholder',
        onboardingCompleted: res.onboarding_completed,
        policies: {
          autonomyLevel: res.policies.autonomy_level,
          maxDiscountPercentage: res.policies.max_discount_percentage,
          minMarginPercentage: res.policies.min_margin_percentage,
          maxSingleTransactionPaise: res.policies.max_single_transaction_paise,
          policyHash: res.policies.policy_hash,
          protocolVersion: res.policies.protocol_version,
        },
      };

      setMerchant(profile);
      setToken(res.token);
      setSessionExpired(false);

      api.setAuth(profile.merchantId, res.token);
      localStorage.setItem(STORAGE_KEY_TOKEN, res.token);
      localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(profile));
      localStorage.setItem(STORAGE_KEY_EXPIRY, res.expires_at);
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (payload: SignupPayload) => {
    setIsLoading(true);
    try {
      const res = await api.signup(payload);
      const profile: MerchantProfile = {
        merchantId: res.merchant_id,
        name: res.name,
        slug: res.slug,
        status: res.status,
        currency: res.currency,
        rzpKeyId: payload.rzpKeyId || 'rzp_test_placeholder',
        onboardingCompleted: res.onboarding_completed,
        policies: {
          autonomyLevel: res.policies.autonomy_level,
          maxDiscountPercentage: res.policies.max_discount_percentage,
          minMarginPercentage: res.policies.min_margin_percentage,
          maxSingleTransactionPaise: res.policies.max_single_transaction_paise,
          policyHash: res.policies.policy_hash,
          protocolVersion: res.policies.protocol_version,
        },
      };

      setMerchant(profile);
      setToken(res.token);
      setSessionExpired(false);

      api.setAuth(profile.merchantId, res.token);
      localStorage.setItem(STORAGE_KEY_TOKEN, res.token);
      localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(profile));
      localStorage.setItem(STORAGE_KEY_EXPIRY, res.expires_at);
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    setMerchant(null);
    setToken(null);
    api.clearAuth();
    localStorage.removeItem(STORAGE_KEY_TOKEN);
    localStorage.removeItem(STORAGE_KEY_MERCHANT);
    localStorage.removeItem(STORAGE_KEY_EXPIRY);
  };

  const updateProfile = (partial: Partial<MerchantProfile>) => {
    if (!merchant) return;
    const updated = { ...merchant, ...partial };
    setMerchant(updated);
    localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(updated));
  };

  const refreshProfile = async () => {
    if (!token || !merchant) return;
    try {
      const updated = await api.getProfile();
      setMerchant(updated);
      localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(updated));
    } catch {
      // Ignore
    }
  };

  const dismissExpiredDialog = () => {
    setSessionExpired(false);
  };

  return (
    <AuthContext.Provider
      value={{
        merchant,
        token,
        isAuthenticated: !!merchant && !!token,
        isLoading,
        sessionExpired,
        login,
        signup,
        logout,
        updateProfile,
        refreshProfile,
        dismissExpiredDialog,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
