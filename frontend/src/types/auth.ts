export interface MerchantProfile {
  merchantId: string;
  name: string;
  slug: string;
  status: 'ACTIVE' | 'PAUSED' | 'SUSPENDED';
  currency: string;
  rzpKeyId: string;
  onboardingCompleted: boolean;
  policies: PolicySummary;
  createdAt?: string;
}

export interface PolicySummary {
  autonomyLevel: number;
  maxDiscountPercentage: number;
  minMarginPercentage: number;
  maxSingleTransactionPaise: number;
  policyHash: string;
  protocolVersion: string;
}

export interface MerchantAuthResponse {
  merchant_id: string;
  name: string;
  slug: string;
  status: 'ACTIVE' | 'PAUSED' | 'SUSPENDED';
  currency: string;
  token: string;
  expires_at: string;
  onboarding_completed: boolean;
  policies: {
    autonomy_level: number;
    max_discount_percentage: number;
    min_margin_percentage: number;
    max_single_transaction_paise: number;
    policy_hash: string;
    protocol_version: string;
  };
}

export interface LoginCredentials {
  slug: string;
  rzpKeyId?: string;
  adminToken?: string;
}

export interface SignupPayload {
  name: string;
  slug: string;
  email: string;
  rzpKeyId?: string;
  currency?: 'INR';
  initialAutonomyLevel?: number;
  maxDiscountPercentage?: number;
  minMarginPercentage?: number;
  maxSingleTransactionPaise?: number;
}
