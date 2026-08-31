import { GatewayEnvelope } from '@/types/gateway';
import { MerchantAuthResponse, LoginCredentials, SignupPayload, MerchantProfile } from '@/types/auth';
import {
  DashboardSummary,
  ProductItem,
  ProductCreatePayload,
  InventoryItem,
  QuoteDetail,
  OrderDetail,
  PaymentAttemptItem,
  ApprovalItem,
  ResolveApprovalPayload,
  PolicyGovernance,
  AuditLedger,
  DemoSimulationStepRequest,
  DemoSimulationStepResponse,
  DemoSeedResponse,
} from '@/types/portal';

export class ApiError extends Error {
  constructor(
    public status: number,
    public code: string,
    message: string,
    public details?: Record<string, unknown>
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

export class ApiClient {
  private baseUrl: string;
  private merchantId: string | null = null;
  private onUnauthorizedCallback: (() => void) | null = null;

  constructor(baseUrl = '') {
    this.baseUrl = baseUrl;
  }

  setAuth(merchantId: string) {
    this.merchantId = merchantId;
  }

  clearAuth() {
    this.merchantId = null;
  }

  onUnauthorized(cb: () => void) {
    this.onUnauthorizedCallback = cb;
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      Accept: 'application/json',
      ...(options.headers as Record<string, string>),
    };

    if (this.merchantId) {
      headers['X-Merchant-ID'] = this.merchantId;
    }

    try {
      const response = await fetch(url, {
        ...options,
        headers,
        credentials: 'include',
      });

      if (response.status === 401 || response.status === 403) {
        if (this.onUnauthorizedCallback) {
          this.onUnauthorizedCallback();
        }
      }

      const data = await response.json().catch(() => ({}));

      if (!response.ok) {
        const detail = data.detail || response.statusText || 'API Error';
        throw new ApiError(
          response.status,
          data.code || `HTTP_${response.status}`,
          typeof detail === 'string' ? detail : JSON.stringify(detail),
          data.details
        );
      }

      return data as T;
    } catch (err: unknown) {
      if (err instanceof ApiError) {
        throw err;
      }
      throw new ApiError(
        0,
        'NETWORK_ERROR',
        err instanceof Error ? err.message : 'Network request failed'
      );
    }
  }

  async signup(payload: SignupPayload): Promise<MerchantAuthResponse> {
    return this.request<MerchantAuthResponse>('/api/v1/merchant/auth/signup', {
      method: 'POST',
      body: JSON.stringify({
        name: payload.name,
        slug: payload.slug,
        email: payload.email,
        rzp_key_id: payload.rzpKeyId || 'rzp_test_placeholder',
        currency: payload.currency || 'INR',
        initial_autonomy_level: payload.initialAutonomyLevel ?? 1,
        max_discount_percentage: payload.maxDiscountPercentage ?? 15.0,
        min_margin_percentage: payload.minMarginPercentage ?? 20.0,
        max_single_transaction_paise: payload.maxSingleTransactionPaise ?? 5000000,
      }),
    });
  }

  async login(credentials: LoginCredentials): Promise<MerchantAuthResponse> {
    return this.request<MerchantAuthResponse>('/api/v1/merchant/auth/login', {
      method: 'POST',
      body: JSON.stringify({
        slug: credentials.slug,
        rzp_key_id: credentials.rzpKeyId,
        admin_token: credentials.adminToken,
      }),
    });
  }

  async logout(): Promise<void> {
    await this.request<Record<string, never>>('/api/v1/merchant/auth/logout', {
      method: 'POST',
    });
  }

  async getProfile(): Promise<MerchantProfile> {
    const res = await this.request<{
      merchant_id: string;
      name: string;
      slug: string;
      status: 'ACTIVE' | 'PAUSED' | 'SUSPENDED';
      currency: string;
      rzp_key_id: string;
      onboarding_completed: boolean;
      policies: {
        autonomy_level: number;
        max_discount_percentage: number;
        min_margin_percentage: number;
        max_single_transaction_paise: number;
        policy_hash: string;
        protocol_version: string;
      };
      created_at?: string;
    }>('/api/v1/merchant/auth/me');

    return {
      merchantId: res.merchant_id,
      name: res.name,
      slug: res.slug,
      status: res.status,
      currency: res.currency,
      rzpKeyId: res.rzp_key_id,
      onboardingCompleted: res.onboarding_completed,
      policies: {
        autonomyLevel: res.policies.autonomy_level,
        maxDiscountPercentage: res.policies.max_discount_percentage,
        minMarginPercentage: res.policies.min_margin_percentage,
        maxSingleTransactionPaise: res.policies.max_single_transaction_paise,
        policyHash: res.policies.policy_hash,
        protocolVersion: res.policies.protocol_version,
      },
      createdAt: res.created_at,
    };
  }

  async completeSetup(payload: {
    name?: string;
    rzpKeyId?: string;
    autonomyLevel: number;
    maxDiscountPercentage: number;
    minMarginPercentage: number;
    maxSingleTransactionPaise: number;
  }): Promise<MerchantProfile> {
    const res = await this.request<{
      merchant_id: string;
      name: string;
      slug: string;
      status: 'ACTIVE' | 'PAUSED' | 'SUSPENDED';
      currency: string;
      rzp_key_id: string;
      onboarding_completed: boolean;
      policies: {
        autonomy_level: number;
        max_discount_percentage: number;
        min_margin_percentage: number;
        max_single_transaction_paise: number;
        policy_hash: string;
        protocol_version: string;
      };
      created_at?: string;
    }>('/api/v1/merchant/setup/complete', {
      method: 'POST',
      body: JSON.stringify({
        name: payload.name,
        rzp_key_id: payload.rzpKeyId,
        autonomy_level: payload.autonomyLevel,
        max_discount_percentage: payload.maxDiscountPercentage,
        min_margin_percentage: payload.minMarginPercentage,
        max_single_transaction_paise: payload.maxSingleTransactionPaise,
      }),
    });

    return {
      merchantId: res.merchant_id,
      name: res.name,
      slug: res.slug,
      status: res.status,
      currency: res.currency,
      rzpKeyId: res.rzp_key_id,
      onboardingCompleted: res.onboarding_completed,
      policies: {
        autonomyLevel: res.policies.autonomy_level,
        maxDiscountPercentage: res.policies.max_discount_percentage,
        minMarginPercentage: res.policies.min_margin_percentage,
        maxSingleTransactionPaise: res.policies.max_single_transaction_paise,
        policyHash: res.policies.policy_hash,
        protocolVersion: res.policies.protocol_version,
      },
      createdAt: res.created_at,
    };
  }

  async getDashboardSummary(): Promise<DashboardSummary> {
    return this.request<DashboardSummary>('/api/v1/merchant/dashboard/summary');
  }

  async listProducts(): Promise<ProductItem[]> {
    return this.request<ProductItem[]>('/api/v1/merchant/products');
  }

  async createProduct(payload: ProductCreatePayload): Promise<ProductItem> {
    return this.request<ProductItem>('/api/v1/merchant/products', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async listInventory(): Promise<InventoryItem[]> {
    return this.request<InventoryItem[]>('/api/v1/merchant/inventory');
  }

  async adjustInventory(payload: { sku: string; quantity_delta: number; reason?: string }): Promise<InventoryItem> {
    return this.request<InventoryItem>('/api/v1/merchant/inventory/adjust', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async listQuotes(): Promise<QuoteDetail[]> {
    return this.request<QuoteDetail[]>('/api/v1/merchant/quotes');
  }

  async listOrders(): Promise<OrderDetail[]> {
    return this.request<OrderDetail[]>('/api/v1/merchant/orders');
  }

  async reconcileOrder(orderId: string): Promise<Record<string, unknown>> {
    return this.request<Record<string, unknown>>(`/api/v1/orders/${orderId}/reconcile`, {
      method: 'POST',
    });
  }

  async listPayments(): Promise<PaymentAttemptItem[]> {
    return this.request<PaymentAttemptItem[]>('/api/v1/merchant/payments');
  }

  async listApprovals(status?: string): Promise<ApprovalItem[]> {
    const query = status ? `?status=${status}` : '';
    return this.request<ApprovalItem[]>(`/api/v1/merchant/approvals${query}`);
  }

  async resolveApproval(approvalId: string, payload: ResolveApprovalPayload): Promise<ApprovalItem> {
    return this.request<ApprovalItem>(`/api/v1/merchant/approvals/${approvalId}/resolve`, {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async getPolicies(): Promise<PolicyGovernance> {
    return this.request<PolicyGovernance>('/api/v1/merchant/policies');
  }

  async updatePolicies(payload: {
    autonomy_level: number;
    max_discount_percentage: number;
    min_margin_percentage: number;
    max_single_transaction_paise: number;
  }): Promise<PolicyGovernance> {
    return this.request<PolicyGovernance>('/api/v1/merchant/policies', {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async getAuditLedger(limit = 50): Promise<AuditLedger> {
    return this.request<AuditLedger>(`/api/v1/merchant/audit?limit=${limit}`);
  }

  async seedDemoState(): Promise<DemoSeedResponse> {
    return this.request<DemoSeedResponse>('/api/v1/merchant/demo/seed', {
      method: 'POST',
    });
  }

  async simulateDemo(payload: DemoSimulationStepRequest): Promise<DemoSimulationStepResponse> {
    return this.request<DemoSimulationStepResponse>('/api/v1/merchant/demo/simulate', {
      method: 'POST',
      body: JSON.stringify(payload),
    });
  }

  async executeGateway<T>(capability: string, payload: Record<string, unknown> = {}): Promise<GatewayEnvelope<T>> {
    return this.request<GatewayEnvelope<T>>('/api/v1/gateway/execute', {
      method: 'POST',
      body: JSON.stringify({
        capability,
        payload,
      }),
    });
  }
}

export const api = new ApiClient();
