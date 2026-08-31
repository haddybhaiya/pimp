import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { OrderDetail } from '@/types/portal';
import { formatPaiseToINR, formatRelativeTime } from '@/lib/utils';
import { ShoppingCart, RefreshCw } from 'lucide-react';

export const OrdersPage: React.FC = () => {
  const [orders, setOrders] = useState<OrderDetail[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [reconcilingId, setReconcilingId] = useState<string | null>(null);
  const [reconcileResult, setReconcileResult] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const fetchOrders = async () => {
    setIsLoading(true);
    try {
      const data = await api.listOrders();
      setOrders(data);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load orders.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchOrders();
  }, []);

  const handleReconcile = async (orderId: string) => {
    setReconcilingId(orderId);
    try {
      const res = await api.reconcileOrder(orderId);
      setReconcileResult(`Reconciliation complete for order ${orderId.slice(0, 8)} (Status: ${res.status || 'PROCESSED'})`);
      await fetchOrders();
    } catch (err: unknown) {
      setReconcileResult(`Reconciliation error: ${err instanceof Error ? err.message : 'Failed'}`);
    } finally {
      setReconcilingId(null);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Orders & Settlement</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Server-authoritative merchant order ledger backed by Razorpay payments.
        </p>
      </div>

      {reconcileResult && (
        <div className="flex items-center justify-between rounded bg-primary/10 border border-primary/30 p-3 text-xs text-primary">
          <span>{reconcileResult}</span>
          <button onClick={() => setReconcileResult(null)} className="font-bold">✕</button>
        </div>
      )}

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
      ) : error ? (
        <EmptyState icon={<ShoppingCart className="h-10 w-10" />} title="Orders unavailable" description={error} />
      ) : orders.length === 0 ? (
        <EmptyState
          icon={<ShoppingCart className="h-10 w-10" />}
          title="No orders committed"
          description="Orders placed by external AI buyers through Razorpay checkout will be listed here."
        />
      ) : (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 text-muted-foreground uppercase text-[10px] border-b border-border">
              <tr>
                <th className="p-3.5">Order ID</th>
                <th className="p-3.5">Buyer Email</th>
                <th className="p-3.5">Razorpay Order</th>
                <th className="p-3.5 text-right">Amount</th>
                <th className="p-3.5 text-center">Status</th>
                <th className="p-3.5">Date</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y border-border font-medium">
              {orders.map((o) => (
                <tr key={o.id} className="hover:bg-accent/30 transition-colors">
                  <td className="p-3.5 font-mono text-primary">{o.id.slice(0, 8)}...</td>
                  <td className="p-3.5 text-foreground">{o.buyer_email}</td>
                  <td className="p-3.5 font-mono text-muted-foreground">{o.rzp_order_id || 'PENDING'}</td>
                  <td className="p-3.5 text-right font-bold text-foreground">{formatPaiseToINR(o.amount_paise)}</td>
                  <td className="p-3.5 text-center">
                    <Badge variant={o.status === 'PAID' ? 'success' : o.status === 'CREATED' ? 'default' : 'secondary'} className="text-[9px]">
                      {o.status}
                    </Badge>
                  </td>
                  <td className="p-3.5 text-muted-foreground">{formatRelativeTime(o.created_at)}</td>
                  <td className="p-3.5 text-right">
                    <Button
                      onClick={() => handleReconcile(o.id)}
                      isLoading={reconcilingId === o.id}
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs gap-1"
                    >
                      <RefreshCw className="h-3 w-3" /> Reconcile
                    </Button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
