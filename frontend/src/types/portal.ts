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

export interface ObservationTelemetryItem {
  category: 'OBSERVED' | 'DERIVED' | 'ESTIMATED';
  metric_name: string;
  value: number | string;
  formatted_value: string;
  unit: string;
  sample_size: number;
  window_days: number;
  description: string;
}

export interface MerchantObservationSnapshot {
  merchant_id: string;
  store_name: string;
  currency: string;
  autonomy_level: number;
  active_policies: Record<string, unknown>;
  catalog_summary: Record<string, unknown>;
  telemetry: ObservationTelemetryItem[];
  signals: Array<{ signal_key: string; title: string; count: number; description: string }>;
  recent_proposals: Array<{ id: string; type: string; title: string; status: string; risk_level: string }>;
  recent_experiments: Array<{ id: string; title: string; target_metric: string; status: string; approval_status: string }>;
  generated_at: string;
}

export interface MerchantDiagnosisItem {
  pattern: string;
  summary: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH';
  evidence_references: string[];
  affected_entities: string[];
}

export interface MerchantProposalItem {
  id: string;
  merchant_id: string;
  run_id?: string;
  proposal_type: string;
  title: string;
  observation: string;
  evidence: string[];
  hypothesis: string;
  proposed_change: string;
  target_entity: string;
  expected_effect: string;
  expected_metric: string;
  confidence: number;
  risk_level: 'READ_ONLY' | 'LOW_RISK_REVERSIBLE' | 'APPROVAL_REQUIRED' | 'PROHIBITED';
  status: 'PROPOSED' | 'UNDER_REVIEW' | 'APPROVED' | 'REJECTED' | 'CONVERTED_TO_EXPERIMENT' | 'ARCHIVED';
  rejection_reason?: string;
  reviewed_by?: string;
  reviewed_at?: string;
  metadata_payload: Record<string, unknown>;
  created_at: string;
  updated_at: string;
}

export interface MerchantProposalReviewPayload {
  decision: 'APPROVE' | 'REJECT' | 'CONVERT_TO_EXPERIMENT';
  rejection_reason?: string;
}

export interface MerchantExperimentResultItem {
  id: string;
  experiment_id: string;
  merchant_id: string;
  sample_size: number;
  baseline_metric: number;
  post_experiment_metric: number;
  absolute_change: number;
  percentage_change: number;
  confidence_score: number;
  limitations: string[];
  recommendation: 'KEEP' | 'ROLLBACK' | 'INCONCLUSIVE';
  deterministic_evidence: Record<string, unknown>;
  recorded_at: string;
}

export interface MerchantExperimentItem {
  id: string;
  merchant_id: string;
  proposal_id?: string;
  title: string;
  hypothesis: string;
  target_metric: string;
  baseline_value: number;
  target_value: number;
  proposed_variation: Record<string, unknown>;
  risk_level: string;
  status: string;
  approval_status: string;
  approved_by?: string;
  approved_at?: string;
  stopping_condition: Record<string, unknown>;
  rollback_condition: Record<string, unknown>;
  start_time?: string;
  end_time?: string;
  created_at: string;
  updated_at: string;
  results: MerchantExperimentResultItem[];
}

export interface ExperimentCreatePayload {
  proposal_id?: string;
  title: string;
  hypothesis: string;
  target_metric: string;
  baseline_value: number;
  target_value: number;
  proposed_variation?: Record<string, unknown>;
  stopping_condition?: Record<string, unknown>;
  rollback_condition?: Record<string, unknown>;
}

export interface MerchantAgentAnalyzeResponse {
  run_id: string;
  merchant_id: string;
  status: string;
  snapshot: MerchantObservationSnapshot;
  diagnoses: MerchantDiagnosisItem[];
  proposals: MerchantProposalItem[];
  step_count: number;
  total_tokens: number;
  execution_duration_ms: number;
  executed_at: string;
  message: string;
}

