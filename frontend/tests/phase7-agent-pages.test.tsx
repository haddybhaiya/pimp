import { describe, expect, it, vi, beforeEach } from 'vitest';
import { fireEvent, render, screen, waitFor } from '@testing-library/react';
import { ExperimentsPage } from '@/pages/experiments';
import { AgentPage } from '@/pages/agent';
import { AuditPage } from '@/pages/audit';
import { api } from '@/lib/api-client';
import type { MerchantObservationSnapshot, MerchantProposalItem } from '@/types/portal';

vi.mock('@/lib/api-client', () => ({
  api: {
    listExperiments: vi.fn(),
    createExperiment: vi.fn(),
    approveExperiment: vi.fn(),
    evaluateExperiment: vi.fn(),
    getAgentSnapshot: vi.fn(),
    listProposals: vi.fn(),
    runAgentAnalysis: vi.fn(),
    reviewProposal: vi.fn(),
    getAutonomyStatus: vi.fn(),
    getAutonomyActions: vi.fn(),
    getAuditLedger: vi.fn(),
  },
}));

const now = '2026-09-02T00:00:00Z';

const snapshot: MerchantObservationSnapshot = {
  merchant_id: 'merchant-1',
  store_name: 'Test merchant',
  currency: 'INR',
  autonomy_level: 1,
  active_policies: {},
  catalog_summary: {},
  telemetry: [
    {
      category: 'DERIVED',
      metric_name: 'quote_conversion_rate',
      value: 12.5,
      formatted_value: '12.5%',
      unit: 'percentage',
      sample_size: 8,
      window_days: 30,
      description: 'Quote conversion rate',
    },
  ],
  signals: [],
  recent_proposals: [],
  recent_experiments: [],
  generated_at: now,
};

const proposedProposal: MerchantProposalItem = {
  id: 'proposal-1',
  merchant_id: 'merchant-1',
  proposal_type: 'EXPOSE_DELIVERY_ETA',
  title: 'Show delivery ETA earlier',
  observation: 'Buyers request delivery information.',
  evidence: ['delivery_questions'],
  hypothesis: 'Earlier ETA visibility can improve conversion.',
  proposed_change: 'Expose the delivery ETA in discovery responses.',
  target_entity: 'product discovery',
  expected_effect: 'Higher conversion',
  expected_metric: 'quote_conversion_rate',
  confidence: 0.8,
  risk_level: 'LOW_RISK_REVERSIBLE',
  status: 'PROPOSED',
  metadata_payload: {},
  created_at: now,
  updated_at: now,
};

describe('Phase 7 Agent workbench', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(api.listExperiments).mockResolvedValue([]);
    vi.mocked(api.getAgentSnapshot).mockResolvedValue(snapshot);
    vi.mocked(api.listProposals).mockResolvedValue([proposedProposal]);
    vi.mocked(api.getAutonomyStatus).mockResolvedValue({
      merchant_id: 'merchant-1',
      kill_switch_enabled: false,
      anomaly_state: 'NORMAL',
      anomaly_reasons: [],
      hourly_executions_count: 0,
      daily_executions_count: 0,
      recent_actions: [],
      rules: [],
    });
    vi.mocked(api.getAutonomyActions).mockResolvedValue([]);
  });

  it('submits the merchant-entered experiment variation', async () => {
    vi.mocked(api.createExperiment).mockResolvedValue({} as never);
    render(<ExperimentsPage />);

    await waitFor(() => expect(api.listExperiments).toHaveBeenCalled());
    fireEvent.click(screen.getByRole('button', { name: /new experiment/i }));
    fireEvent.change(screen.getByLabelText(/experiment title/i), { target: { value: 'ETA copy test' } });
    fireEvent.change(screen.getByPlaceholderText(/explain what change/i), {
      target: { value: 'Earlier ETA may reduce buyer uncertainty.' },
    });
    fireEvent.change(screen.getByPlaceholderText(/describe the exact merchant-controlled change/i), {
      target: { value: 'Show the promised delivery date beside every product result.' },
    });
    fireEvent.submit(screen.getByRole('button', { name: /register experiment/i }).closest('form')!);

    await waitFor(() => {
      expect(api.createExperiment).toHaveBeenCalledWith(
        expect.objectContaining({
          proposed_variation: {
            description: 'Show the promised delivery date beside every product result.',
          },
        })
      );
    });
  });

  it('creates a linked experiment when a proposal is converted', async () => {
    vi.mocked(api.reviewProposal).mockResolvedValue({ ...proposedProposal, status: 'CONVERTED_TO_EXPERIMENT' });
    vi.mocked(api.createExperiment).mockResolvedValue({} as never);
    render(<AgentPage />);

    await waitFor(() => expect(screen.getByText(proposedProposal.title)).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: /convert to experiment/i }));
    fireEvent.change(screen.getByRole('spinbutton'), { target: { value: '15' } });
    fireEvent.click(screen.getByRole('button', { name: /^confirm$/i }));

    await waitFor(() => {
      expect(api.createExperiment).toHaveBeenCalledWith(
        expect.objectContaining({
          proposal_id: proposedProposal.id,
          target_metric: proposedProposal.expected_metric,
          target_value: 15,
          proposed_variation: { description: proposedProposal.proposed_change },
        })
      );
    });
  });

  it('renders the actual archived lifecycle state', async () => {
    vi.mocked(api.listProposals).mockResolvedValue([{ ...proposedProposal, status: 'ARCHIVED' }]);
    render(<AgentPage />);

    await waitFor(() => expect(screen.getByText('ARCHIVED')).toBeInTheDocument());
  });

  it('fails closed when the autonomy status cannot be refreshed', async () => {
    vi.mocked(api.getAutonomyStatus).mockRejectedValue(new Error('Status temporarily unavailable.'));
    render(<AgentPage />);

    await waitFor(() => expect(screen.getByText('Status temporarily unavailable.')).toBeInTheDocument());
    expect(screen.queryByRole('button', { name: /run autonomously/i })).not.toBeInTheDocument();
  });

  it('keeps loaded audit events visible when the next cursor page fails', async () => {
    vi.mocked(api.getAuditLedger)
      .mockResolvedValueOnce({
        events: [
          {
            id: 'event-1',
            merchant_id: 'merchant-1',
            actor_type: 'MERCHANT_ADMIN',
            event_type: 'MERCHANT_REGISTERED',
            payload: {},
            event_hash: 'hash-1',
            created_at: now,
          },
        ],
        total_count: 2,
        chain_valid: true,
        next_cursor: { created_at: now, id: 'event-1' },
      })
      .mockRejectedValueOnce(new Error('Older audit events are temporarily unavailable.'));
    render(<AuditPage />);

    await waitFor(() => expect(screen.getByText('MERCHANT_REGISTERED')).toBeInTheDocument());
    fireEvent.click(screen.getByRole('button', { name: /load older events/i }));

    await waitFor(() => {
      expect(screen.getByText('MERCHANT_REGISTERED')).toBeInTheDocument();
      expect(screen.getByRole('alert')).toHaveTextContent('Older audit events are temporarily unavailable.');
      expect(api.getAuditLedger).toHaveBeenLastCalledWith(50, { created_at: now, id: 'event-1' });
    });
  });
});
