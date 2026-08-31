import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ApiClient, ApiError } from '@/lib/api-client';

describe('ApiClient Unit Tests', () => {
  let client: ApiClient;

  beforeEach(() => {
    client = new ApiClient('http://localhost:8000');
    vi.restoreAllMocks();
  });

  it('uses browser credentials and sends only the non-secret merchant ID header', async () => {
    client.setAuth('merchant-123');

    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve({ success: true }),
    } as unknown as Response);

    await client.executeGateway('discover_products');

    expect(global.fetch).toHaveBeenCalledWith(
      'http://localhost:8000/api/v1/gateway/execute',
      expect.objectContaining({
        headers: expect.objectContaining({
          'X-Merchant-ID': 'merchant-123',
        }),
        credentials: 'include',
      })
    );
  });

  it('triggers onUnauthorized callback on 401 response', async () => {
    const unauthSpy = vi.fn();
    client.onUnauthorized(unauthSpy);

    global.fetch = vi.fn().mockResolvedValue({
      ok: false,
      status: 401,
      statusText: 'Unauthorized',
      json: () => Promise.resolve({ detail: 'Session expired' }),
    } as unknown as Response);

    await expect(client.getProfile()).rejects.toThrow(ApiError);
    expect(unauthSpy).toHaveBeenCalled();
  });

  it('handles network errors fail-closed', async () => {
    global.fetch = vi.fn().mockRejectedValue(new Error('Connection refused'));

    await expect(client.getProfile()).rejects.toThrow(ApiError);
  });

  it('normalizes approval reasons from the server response contract', async () => {
    global.fetch = vi.fn().mockResolvedValue({
      ok: true,
      status: 200,
      json: () => Promise.resolve([{
        id: 'approval-1',
        merchant_id: 'merchant-123',
        approval_type: 'DISCOUNT',
        status: 'PENDING',
        requested_amount_paise: 1000,
        proposed_discount_paise: 100,
        proposed_discount_percentage: 10,
        policy_rule_code: 'MAX_DISCOUNT',
        reason: 'Buyer requested a discount',
        expires_at: '2026-01-01T00:00:00Z',
        created_at: '2025-01-01T00:00:00Z',
      }]),
    } as unknown as Response);

    await expect(client.listApprovals()).resolves.toMatchObject([
      { reason_note: 'Buyer requested a discount' },
    ]);
  });
});
