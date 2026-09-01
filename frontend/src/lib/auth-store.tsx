import React, { createContext, useContext, useEffect, useState } from 'react';
import { MerchantProfile, LoginCredentials, SignupPayload } from '@/types/auth';
import { api } from '@/lib/api-client';

interface AuthContextType {
  merchant: MerchantProfile | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  sessionExpired: boolean;
  login: (creds: LoginCredentials, insforgeAccessToken?: string) => Promise<void>;
  signup: (payload: SignupPayload, insforgeAccessToken?: string) => Promise<void>;
  logout: () => void;
  updateProfile: (profile: Partial<MerchantProfile>) => void;
  refreshProfile: () => Promise<void>;
  dismissExpiredDialog: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

const STORAGE_KEY_MERCHANT = 'arm_merchant_data';

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [merchant, setMerchant] = useState<MerchantProfile | null>(() => {
    try {
      const saved = localStorage.getItem(STORAGE_KEY_MERCHANT);
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [sessionExpired, setSessionExpired] = useState<boolean>(false);

  useEffect(() => {
    if (merchant) {
      api.setAuth(merchant.merchantId);
    }

    api.onUnauthorized(() => {
      setSessionExpired(true);
    });

    setIsLoading(false);
  }, []);

  const login = async (creds: LoginCredentials, insforgeAccessToken?: string) => {
    setIsLoading(true);
    try {
      const res = await api.login(creds, insforgeAccessToken);
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
      setSessionExpired(false);

      api.setAuth(profile.merchantId);
      localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(profile));
    } finally {
      setIsLoading(false);
    }
  };

  const signup = async (payload: SignupPayload, insforgeAccessToken?: string) => {
    setIsLoading(true);
    try {
      const res = await api.signup(payload, insforgeAccessToken);
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
      setSessionExpired(false);

      api.setAuth(profile.merchantId);
      localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(profile));
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    void api.logout().catch(() => undefined);
    setMerchant(null);
    api.clearAuth();
    localStorage.removeItem(STORAGE_KEY_MERCHANT);
  };

  const updateProfile = (partial: Partial<MerchantProfile>) => {
    if (!merchant) return;
    const updated = { ...merchant, ...partial };
    setMerchant(updated);
    localStorage.setItem(STORAGE_KEY_MERCHANT, JSON.stringify(updated));
  };

  const refreshProfile = async () => {
    if (!merchant) return;
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
    setMerchant(null);
    api.clearAuth();
    localStorage.removeItem(STORAGE_KEY_MERCHANT);
  };

  return (
    <AuthContext.Provider
      value={{
        merchant,
        isAuthenticated: !!merchant,
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
