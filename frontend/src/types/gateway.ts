export interface GatewayEnvelope<T> {
  status: 'SUCCESS' | 'REJECTED' | 'ERROR';
  capability: string;
  data?: T;
  error?: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
  context?: {
    request_id?: string;
    policy_decision_hash?: string;
    state?: string;
  };
}

export interface CapabilityDefinition {
  name: string;
  description: string;
  input_schema_name: string;
  output_schema_name: string;
  classification: 'READ_ONLY' | 'STATEFUL_COMMERCE' | 'PRIVILEGED_FINANCIAL';
  side_effects: string[];
  monetary_impact: boolean;
  required_capability: string;
  approval_requirement: 'NONE' | 'EXPLICIT_HUMAN' | 'CONDITIONAL_POLICY';
  idempotency_requirement: boolean;
  failure_states: string[];
}
