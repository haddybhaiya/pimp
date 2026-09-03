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
  AuditCursor,
  DemoSimulationStepRequest,
  DemoSimulationStepResponse,
  DemoSeedResponse,
  MerchantObservationSnapshot,
  MerchantProposalItem,
  MerchantProposalReviewPayload,
  MerchantExperimentItem,
  MerchantExperimentResultItem,
  ExperimentCreatePayload,
  MerchantAgentAnalyzeResponse,
  AutonomyStatusResponse,
  AutonomyRuleItem,
  AutonomyActionItem,
  KillSwitchResponse,
  RollbackResponse,
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

  private createIdempotencyKey(): string {
    if (typeof crypto?.randomUUID === 'function') {
      return crypto.randomUUID();
    }
    throw new ApiError(0, 'IDEMPOTENCY_UNAVAILABLE', 'This browser cannot create a secure request key.');
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

  async signup(payload: SignupPayload, insforgeAccessToken?: string): Promise<MerchantAuthResponse> {
    return this.request<MerchantAuthResponse>('/api/v1/merchant/auth/signup', {
      method: 'POST',
      headers: insforgeAccessToken ? { Authorization: `Bearer ${insforgeAccessToken}` } : undefined,
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

  async login(credentials: LoginCredentials, insforgeAccessToken?: string): Promise<MerchantAuthResponse> {
    return this.request<MerchantAuthResponse>('/api/v1/merchant/auth/login', {
      method: 'POST',
      headers: insforgeAccessToken ? { Authorization: `Bearer ${insforgeAccessToken}` } : undefined,
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
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
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
    const approvals = await this.request<Array<ApprovalItem & { reason?: string }>>(
      `/api/v1/merchant/approvals${query}`
    );
    return approvals.map(({ reason, reason_note, ...approval }) => ({
      ...approval,
      reason_note: reason_note ?? reason,
    }));
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

  async getAuditLedger(limit = 50, before?: AuditCursor): Promise<AuditLedger> {
    const query = new URLSearchParams({ limit: String(limit) });
    if (before) {
      query.set('before_created_at', before.created_at);
      query.set('before_id', before.id);
    }
    return this.request<AuditLedger>(`/api/v1/merchant/audit?${query.toString()}`);
  }

  async seedDemoState(): Promise<DemoSeedResponse> {
    return this.request<DemoSeedResponse>('/api/v1/merchant/demo/seed', {
      method: 'POST',
    });
  }

  async simulateDemo(payload: DemoSimulationStepRequest): Promise<DemoSimulationStepResponse> {
    return this.request<DemoSimulationStepResponse>('/api/v1/merchant/demo/simulate', {
      method: 'POST',
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
      body: JSON.stringify(payload),
    });
  }

  // =========================================================================
  // Phase 7 — Merchant Agent & Experiment Methods
  // =========================================================================

  async getAgentSnapshot(windowDays = 30): Promise<MerchantObservationSnapshot> {
    return this.request<MerchantObservationSnapshot>(`/api/v1/merchant/agent/snapshot?window_days=${windowDays}`);
  }

  async runAgentAnalysis(): Promise<MerchantAgentAnalyzeResponse> {
    return this.request<MerchantAgentAnalyzeResponse>('/api/v1/merchant/agent/analyze', {
      method: 'POST',
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
    });
  }

  async listProposals(status?: string): Promise<MerchantProposalItem[]> {
    const query = status ? `?status_filter=${status}` : '';
    return this.request<MerchantProposalItem[]>(`/api/v1/merchant/agent/proposals${query}`);
  }

  async reviewProposal(proposalId: string, payload: MerchantProposalReviewPayload): Promise<MerchantProposalItem> {
    return this.request<MerchantProposalItem>(`/api/v1/merchant/agent/proposals/${proposalId}/review`, {
      method: 'POST',
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
      body: JSON.stringify(payload),
    });
  }

  async createExperiment(payload: ExperimentCreatePayload): Promise<MerchantExperimentItem> {
    return this.request<MerchantExperimentItem>('/api/v1/merchant/experiments', {
      method: 'POST',
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
      body: JSON.stringify(payload),
    });
  }

  async listExperiments(): Promise<MerchantExperimentItem[]> {
    return this.request<MerchantExperimentItem[]>('/api/v1/merchant/experiments');
  }

  async approveExperiment(experimentId: string): Promise<MerchantExperimentItem> {
    return this.request<MerchantExperimentItem>(`/api/v1/merchant/experiments/${experimentId}/approve`, {
      method: 'POST',
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
    });
  }

  async evaluateExperiment(experimentId: string): Promise<MerchantExperimentResultItem> {
    return this.request<MerchantExperimentResultItem>(`/api/v1/merchant/experiments/${experimentId}/evaluate`, {
      method: 'POST',
      headers: { 'X-Idempotency-Key': this.createIdempotencyKey() },
    });
  }

  // =========================================================================
  // Phase 8 — Controlled Autonomy & Deterministic Rollback Methods
  // =========================================================================

  async getAutonomyStatus(): Promise<AutonomyStatusResponse> {
    return this.request<AutonomyStatusResponse>('/api/v1/merchant/autonomy/status');
  }

  async setKillSwitch(enabled: boolean, reason?: string): Promise<KillSwitchResponse> {
    return this.request<KillSwitchResponse>('/api/v1/merchant/autonomy/kill-switch', {
      method: 'POST',
      body: JSON.stringify({
        enabled,
        reason: reason ?? 'Merchant administrative kill switch trigger',
      }),
    });
  }

  async getAutonomyRules(): Promise<AutonomyRuleItem[]> {
    return this.request<AutonomyRuleItem[]>('/api/v1/merchant/autonomy/rules');
  }

  async updateAutonomyRule(
    actionType: string,
    payload: {
      is_enabled?: boolean;
      classification?: string;
      max_executions_per_hour?: number;
      max_executions_per_day?: number;
      cooldown_seconds?: number;
      experiment_duration_limit_days?: number;
      rollback_required?: boolean;
      approval_required?: boolean;
      expected_version: number;
    }
  ): Promise<AutonomyRuleItem> {
    return this.request<AutonomyRuleItem>(`/api/v1/merchant/autonomy/rules/${actionType}`, {
      method: 'PUT',
      body: JSON.stringify(payload),
    });
  }

  async getAutonomyActions(limit = 50, offset = 0): Promise<AutonomyActionItem[]> {
    return this.request<AutonomyActionItem[]>(`/api/v1/merchant/autonomy/actions?limit=${limit}&offset=${offset}`);
  }

  async getAutonomyAction(actionId: string): Promise<AutonomyActionItem> {
    return this.request<AutonomyActionItem>(`/api/v1/merchant/autonomy/actions/${actionId}`);
  }

  async executeAutonomyAction(
    proposalId: string,
    expectedTargetVersion: number,
    idempotencyKey?: string
  ): Promise<{ action: AutonomyActionItem; message: string; status: string }> {
    return this.request('/api/v1/merchant/autonomy/execute', {
      method: 'POST',
      headers: { 'X-Idempotency-Key': idempotencyKey ?? this.createIdempotencyKey() },
      body: JSON.stringify({
        proposal_id: proposalId,
        expected_target_version: expectedTargetVersion,
      }),
    });
  }

  async rollbackAutonomyAction(
    actionId: string,
    expectedTargetVersion: number,
    reason: string,
    idempotencyKey?: string
  ): Promise<RollbackResponse> {
    return this.request(`/api/v1/merchant/autonomy/actions/${actionId}/rollback`, {
      method: 'POST',
      headers: { 'X-Idempotency-Key': idempotencyKey ?? this.createIdempotencyKey() },
      body: JSON.stringify({
        expected_target_version: expectedTargetVersion,
        reason,
      }),
    });
  }

  async stopExperiment(
    experimentId: string,
    reason: string,
    requireRollback = false,
    idempotencyKey?: string
  ): Promise<{ experiment_id: string; status: string; reason: string; message: string }> {
    return this.request(`/api/v1/merchant/experiments/${experimentId}/stop`, {
      method: 'POST',
      headers: { 'X-Idempotency-Key': idempotencyKey ?? this.createIdempotencyKey() },
      body: JSON.stringify({ reason, require_rollback: requireRollback }),
    });
  }

  async rollbackExperiment(
    experimentId: string,
    reason: string,
    idempotencyKey?: string
  ): Promise<{ experiment_id: string; status: string; reason: string; message: string }> {
    return this.request(`/api/v1/merchant/experiments/${experimentId}/rollback`, {
      method: 'POST',
      headers: { 'X-Idempotency-Key': idempotencyKey ?? this.createIdempotencyKey() },
      body: JSON.stringify({ reason }),
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
