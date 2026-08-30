import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { DemoPage } from '../src/pages/demo';
import { api } from '../src/lib/api-client';
import { AuthProvider } from '../src/lib/auth-store';

vi.mock('../src/lib/api-client', () => ({
  api: {
    setAuth: vi.fn(),
    clearAuth: vi.fn(),
    onUnauthorized: vi.fn(),
    simulateDemo: vi.fn(),
    seedDemoState: vi.fn(),
  },
}));

describe('Phase 5.3 Demo Simulator & Hardening Views Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Demo Sandbox page with scenario options', () => {
    render(
      <AuthProvider>
        <DemoPage />
      </AuthProvider>
    );

    expect(screen.getByText(/Interactive Simulation Sandbox/i)).toBeInTheDocument();
    expect(screen.getByText(/Standard Auto Commerce/i)).toBeInTheDocument();
    expect(screen.getByText(/HITL Human Approval/i)).toBeInTheDocument();
    expect(screen.getByText(/Payment Reconciliation/i)).toBeInTheDocument();
  });

  it('executes Standard Auto Commerce scenario and renders execution trace', async () => {
    vi.mocked(api.simulateDemo).mockResolvedValueOnce({
      scenario: 'STANDARD_AUTO_COMMERCE',
      session_id: 'sess-12345',
      quote_id: 'quote-12345',
      order_id: 'order-12345',
      rzp_order_id: 'order_demo_123',
      rzp_payment_id: 'pay_demo_123',
      status: 'SETTLED',
      subtotal_paise: 1299900,
      discount_paise: 129990,
      total_paise: 1169910,
      policy_verdict: 'ALLOW',
      policy_hash: 'a'.repeat(64),
      audit_event_hash: 'b'.repeat(64),
      message: 'Standard Autonomous Commerce completed and settled successfully.',
      steps: [
        {
          step_number: 1,
          actor: 'Buyer Agent (External AI)',
          action: 'session_init',
          status: 'SUCCESS',
          summary: 'Initiated ACP buyer session for ai-buyer-1 with scoped commerce capabilities.',
          details: { session_id: 'sess-12345' },
          timestamp: new Date().toISOString(),
        },
        {
          step_number: 2,
          actor: 'Razorpay Payment Webhook Receiver',
          action: 'process_payment_webhook',
          status: 'SETTLED',
          summary: 'Cryptographically verified webhook received and processed. Payment pay_demo_123 captured.',
          details: { payment_id: 'pay_demo_123' },
          timestamp: new Date().toISOString(),
        },
      ],
    });

    render(
      <AuthProvider>
        <DemoPage />
      </AuthProvider>
    );

    const runButton = screen.getByRole('button', { name: /Run Simulation Scenario/i });
    fireEvent.click(runButton);

    await waitFor(() => {
      expect(api.simulateDemo).toHaveBeenCalledWith(
        expect.objectContaining({
          scenario: 'STANDARD_AUTO_COMMERCE',
          sku: 'RUN-PRO-01',
          quantity: 1,
          target_discount_pct: 10,
        })
      );
      expect(screen.getByText(/Standard Autonomous Commerce completed and settled successfully/i)).toBeInTheDocument();
      expect(screen.getByText(/Initiated ACP buyer session for ai-buyer-1/i)).toBeInTheDocument();
      expect(screen.getByText(/Cryptographically verified webhook received/i)).toBeInTheDocument();
    });
  });

  it('triggers Reset Demo Data modal and confirms re-seeding', async () => {
    vi.mocked(api.seedDemoState).mockResolvedValueOnce({
      merchant_id: 'm-12345',
      products_seeded: 3,
      policies_configured: true,
      message: 'Demo sandbox catalog and baseline policies successfully initialized.',
    });

    render(
      <AuthProvider>
        <DemoPage />
      </AuthProvider>
    );

    const resetButton = screen.getByRole('button', { name: /Reset Demo Data/i });
    fireEvent.click(resetButton);

    expect(screen.getByText(/Reset & Re-seed Demo Sandbox Data/i)).toBeInTheDocument();

    const confirmButton = screen.getByRole('button', { name: /Confirm Reset/i });
    fireEvent.click(confirmButton);

    await waitFor(() => {
      expect(api.seedDemoState).toHaveBeenCalled();
      expect(screen.getByText(/Demo sandbox catalog and baseline policies successfully initialized/i)).toBeInTheDocument();
    });
  });
});
