export interface DashboardSummary {
  merchant_id: string;
  merchant_name: string;
  status: string;
  currency: string;
  total_products: number;
  total_orders: number;
  total_revenue_paise: number;
  pending_approvals_count: number;
  active_quotes_count: number;
  autonomy_level: number;
  max_discount_percentage: number;
  min_margin_percentage: number;
  max_single_transaction_paise: number;
  policy_hash: string;
  system_health: string;
}

export interface ProductItem {
  id: string;
  merchant_id: string;
  sku: string;
  title: string;
  description: string;
  category: string;
  base_price_paise: number;
  floor_price_paise: number;
  is_negotiable: boolean;
  is_active: boolean;
  attributes: Record<string, unknown>;
  created_at: string;
  available_stock: number;
  reserved_stock: number;
}

export interface ProductCreatePayload {
  sku: string;
  title: string;
  description?: string;
  category: string;
  base_price_paise: number;
  floor_price_paise: number;
  is_negotiable?: boolean;
  is_active?: boolean;
  initial_stock?: number;
  safety_threshold?: number;
  attributes?: Record<string, unknown>;
}

export interface InventoryItem {
  id: string;
  variant_id: string;
  sku: string;
  product_title: string;
  available_quantity: number;
  reserved_quantity: number;
  safety_threshold: number;
  updated_at: string;
}

export interface QuoteItemDetail {
  sku: string;
  title: string;
  quantity: number;
  unit_price_paise: number;
  total_price_paise: number;
}

export interface QuoteDetail {
  id: string;
  session_id: string;
  merchant_id: string;
  status: string;
  subtotal_paise: number;
  discount_paise: number;
  shipping_paise: number;
  total_paise: number;
  discount_reason?: string;
  expires_at: string;
  created_at: string;
  items: QuoteItemDetail[];
}

export interface OrderDetail {
  id: string;
  quote_id: string;
  merchant_id: string;
  status: string;
  amount_paise: number;
  currency: string;
  buyer_email: string;
  shipping_address: Record<string, unknown>;
  rzp_order_id?: string;
  created_at: string;
  payment_attempts_count: number;
}

export interface PaymentAttemptItem {
  id: string;
  order_id: string;
  status: string;
  amount_paise: number;
  rzp_payment_id?: string;
  rzp_order_id: string;
  payment_method?: string;
  error_code?: string;
  error_description?: string;
  created_at: string;
}

export interface ApprovalItem {
  id: string;
  merchant_id: string;
  quote_id?: string;
  order_id?: string;
  session_id?: string;
  approval_type: string;
  status: 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED';
  requested_amount_paise: number;
  proposed_discount_paise: number;
  proposed_discount_percentage: number;
  policy_rule_code: string;
  reason_note?: string;
  expires_at: string;
  created_at: string;
}

export interface ResolveApprovalPayload {
  decision: 'APPROVE' | 'REJECT' | 'COUNTER_OFFER';
  reason_note: string;
  counter_amount_paise?: number;
}

export interface PolicyRuleDetail {
  id: string;
  rule_type: string;
  target_scope: string;
  target_id?: string;
  rule_value: Record<string, unknown>;
  is_active: boolean;
}

export interface PolicyGovernance {
  merchant_id: string;
  autonomy_level: number;
  max_discount_percentage: number;
  min_margin_percentage: number;
  max_single_transaction_paise: number;
  policy_hash: string;
  protocol_version: string;
  rules: PolicyRuleDetail[];
}

export interface AuditEventItem {
  id: string;
  merchant_id: string;
  actor_type: string;
  actor_id?: string;
  event_type: string;
  payload: Record<string, unknown>;
  event_hash: string;
  previous_event_hash?: string;
  created_at: string;
}

export interface AuditLedger {
  events: AuditEventItem[];
  total_count: number;
  chain_valid: boolean;
  chain_error?: string;
}

export interface SimulationTraceStep {
  step_number: number;
  actor: string;
  action: string;
  status: 'SUCCESS' | 'ESCALATED' | 'REJECTED' | 'SETTLED' | 'RECONCILED';
  summary: string;
  details: Record<string, unknown>;
  timestamp: string;
}

export interface DemoSimulationStepRequest {
  scenario: 'STANDARD_AUTO_COMMERCE' | 'HITL_ESCALATION_COMMERCE' | 'PAYMENT_RECONCILIATION';
  sku?: string;
  quantity?: number;
  target_discount_pct?: number;
}

export interface DemoSimulationStepResponse {
  scenario: string;
  session_id: string;
  quote_id?: string;
  approval_id?: string;
  order_id?: string;
  rzp_order_id?: string;
  rzp_payment_id?: string;
  status: string;
  subtotal_paise: number;
  discount_paise: number;
  total_paise: number;
  policy_verdict: string;
  policy_rule_code?: string;
  policy_hash: string;
  audit_event_hash: string;
  steps: SimulationTraceStep[];
  message: string;
}

export interface DemoSeedResponse {
  merchant_id: string;
  products_seeded: number;
  policies_configured: boolean;
  message: string;
}

