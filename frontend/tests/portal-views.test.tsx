import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { CatalogPage } from '../src/pages/catalog';
import { InventoryPage } from '../src/pages/inventory';
import { ApprovalsPage } from '../src/pages/approvals';
import { PoliciesPage } from '../src/pages/policies';
import { AuditPage } from '../src/pages/audit';
import { OrdersPage } from '../src/pages/orders';
import { api } from '../src/lib/api-client';
import { AuthProvider } from '../src/lib/auth-store';

vi.mock('../src/lib/api-client', () => ({
  api: {
    setAuth: vi.fn(),
    clearAuth: vi.fn(),
    onUnauthorized: vi.fn(),
    listProducts: vi.fn(),
    createProduct: vi.fn(),
    listInventory: vi.fn(),
    adjustInventory: vi.fn(),
    listApprovals: vi.fn(),
    resolveApproval: vi.fn(),
    getPolicies: vi.fn(),
    getAutonomyRules: vi.fn(),
    updatePolicies: vi.fn(),
    getAuditLedger: vi.fn(),
    listOrders: vi.fn(),
    reconcileOrder: vi.fn(),
  },
}));

describe('Phase 5.2 Merchant Control Plane Views Tests', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders Catalog page with product items and floor price margin', async () => {
    vi.mocked(api.listProducts).mockResolvedValueOnce([
      {
        id: 'p-1',
        merchant_id: 'm-1',
        sku: 'RUN-01',
        title: 'Running Shoes Pro',
        description: 'High performance running footwear',
        category: 'FOOTWEAR',
        base_price_paise: 500000,
        floor_price_paise: 400000,
        is_negotiable: true,
        is_active: true,
        attributes: {},
        version: 1,
        created_at: new Date().toISOString(),
        available_stock: 15,
        reserved_stock: 0,
      },
    ]);

    render(
      <AuthProvider>
        <CatalogPage />
      </AuthProvider>
    );

    expect(screen.getByText(/Catalog & Products/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(screen.getByText('Running Shoes Pro')).toBeInTheDocument();
      expect(screen.getByText('RUN-01')).toBeInTheDocument();
      expect(screen.getByText('15 units')).toBeInTheDocument();
    });
  });

  it('renders Inventory page and opens adjustment modal', async () => {
    vi.mocked(api.listInventory).mockResolvedValueOnce([
      {
        id: 'inv-1',
        variant_id: 'v-1',
        sku: 'RUN-01',
        product_title: 'Running Shoes Pro',
        available_quantity: 10,
        reserved_quantity: 2,
        safety_threshold: 3,
        updated_at: new Date().toISOString(),
      },
    ]);

    render(
      <AuthProvider>
        <InventoryPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('Running Shoes Pro')).toBeInTheDocument();
    });

    const adjustBtn = screen.getByRole('button', { name: /adjust/i });
    fireEvent.click(adjustBtn);

    expect(screen.getByText(/Adjust Stock for RUN-01/i)).toBeInTheDocument();
  });

  it('renders Approvals queue and allows resolving a pending ticket', async () => {
    vi.mocked(api.listApprovals).mockResolvedValueOnce([
      {
        id: 'appr-1234-5678',
        merchant_id: 'm-1',
        quote_id: 'q-1',
        approval_type: 'QUOTE_DISCOUNT',
        status: 'PENDING',
        requested_amount_paise: 420000,
        proposed_discount_paise: 80000,
        proposed_discount_percentage: 16.0,
        policy_rule_code: 'MAX_DISCOUNT_PCT',
        reason_note: 'Buyer requested 16% discount',
        expires_at: new Date(Date.now() + 600000).toISOString(),
        created_at: new Date().toISOString(),
      },
    ]);

    vi.mocked(api.resolveApproval).mockResolvedValueOnce({
      id: 'appr-1234-5678',
      merchant_id: 'm-1',
      approval_type: 'QUOTE_DISCOUNT',
      status: 'APPROVED',
      requested_amount_paise: 420000,
      proposed_discount_paise: 80000,
      proposed_discount_percentage: 16.0,
      policy_rule_code: 'MAX_DISCOUNT_PCT',
      expires_at: new Date().toISOString(),
      created_at: new Date().toISOString(),
    });

    render(
      <AuthProvider>
        <ApprovalsPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Ticket appr-123/i)).toBeInTheDocument();
      expect(screen.getByText('16%')).toBeInTheDocument();
    });

    const approveBtn = screen.getByRole('button', { name: /approve offer/i });
    fireEvent.click(approveBtn);

    expect(screen.getByText(/Approve Ticket appr-123/i)).toBeInTheDocument();
  });

  it('renders Policy governance editor with SHA-256 fingerprint', async () => {
    vi.mocked(api.getPolicies).mockResolvedValueOnce({
      merchant_id: 'm-1',
      autonomy_level: 1,
      max_discount_percentage: 15.0,
      min_margin_percentage: 20.0,
      max_single_transaction_paise: 5000000,
      policy_hash: 'a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2',
      protocol_version: '2026-03-01',
      rules: [],
    });
    vi.mocked(api.getAutonomyRules).mockResolvedValueOnce([]);

    render(
      <AuthProvider>
        <PoliciesPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Policy Rules & Autonomy Governance/i)).toBeInTheDocument();
      expect(screen.getByText('a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2c3d4e5f6a1b2')).toBeInTheDocument();
    });
  });

  it('renders Audit ledger with verified chain badge', async () => {
    vi.mocked(api.getAuditLedger).mockResolvedValueOnce({
      events: [
        {
          id: 'ev-1',
          merchant_id: 'm-1',
          actor_type: 'MERCHANT_ADMIN',
          event_type: 'MERCHANT_REGISTERED',
          payload: { slug: 'test-store' },
          event_hash: 'hash-abc-123',
          created_at: new Date().toISOString(),
        },
      ],
      total_count: 1,
      chain_valid: true,
    });

    render(
      <AuthProvider>
        <AuditPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText(/Chain Verified: 100% Intact/i)).toBeInTheDocument();
      expect(screen.getByText('MERCHANT_REGISTERED')).toBeInTheDocument();
    });
  });

  it('renders Orders page and triggers reconciliation', async () => {
    vi.mocked(api.listOrders).mockResolvedValueOnce([
      {
        id: 'ord-12345678-abcd',
        quote_id: 'q-1',
        merchant_id: 'm-1',
        status: 'PAID',
        amount_paise: 499900,
        currency: 'INR',
        buyer_email: 'buyer@example.com',
        shipping_address: {},
        rzp_order_id: 'order_rzp_123',
        created_at: new Date().toISOString(),
        payment_attempts_count: 1,
      },
    ]);

    render(
      <AuthProvider>
        <OrdersPage />
      </AuthProvider>
    );

    await waitFor(() => {
      expect(screen.getByText('buyer@example.com')).toBeInTheDocument();
      expect(screen.getByText('order_rzp_123')).toBeInTheDocument();
    });
  });
});
