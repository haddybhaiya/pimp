import React, { useEffect, useState } from 'react';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { PaymentAttemptItem } from '@/types/portal';
import { formatPaiseToINR, formatRelativeTime } from '@/lib/utils';
import { CreditCard } from 'lucide-react';

export const PaymentsPage: React.FC = () => {
  const [payments, setPayments] = useState<PaymentAttemptItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchPayments = async () => {
      try {
        const data = await api.listPayments();
        setPayments(data);
      } finally {
        setIsLoading(false);
      }
    };
    fetchPayments();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Payment Attempts & Settlements</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Razorpay capture attempts, webhook verification results, and transaction binding references.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
        </div>
      ) : payments.length === 0 ? (
        <EmptyState
          icon={<CreditCard className="h-10 w-10" />}
          title="No payment attempts logged"
          description="When payment capture occurs via webhook or settlement fetch, records will appear here."
        />
      ) : (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 text-muted-foreground uppercase text-[10px] border-b border-border">
              <tr>
                <th className="p-3.5">Payment ID</th>
                <th className="p-3.5">Razorpay Payment</th>
                <th className="p-3.5">Razorpay Order</th>
                <th className="p-3.5 text-right">Amount</th>
                <th className="p-3.5 text-center">Status</th>
                <th className="p-3.5">Method</th>
                <th className="p-3.5">Date</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border font-medium">
              {payments.map((p) => (
                <tr key={p.id} className="hover:bg-accent/30 transition-colors">
                  <td className="p-3.5 font-mono text-primary">{p.id.slice(0, 8)}...</td>
                  <td className="p-3.5 font-mono text-muted-foreground">{p.rzp_payment_id || 'N/A'}</td>
                  <td className="p-3.5 font-mono text-muted-foreground">{p.rzp_order_id}</td>
                  <td className="p-3.5 text-right font-bold text-foreground">{formatPaiseToINR(p.amount_paise)}</td>
                  <td className="p-3.5 text-center">
                    <Badge variant={p.status === 'CAPTURED' ? 'success' : p.status === 'FAILED' ? 'destructive' : 'default'} className="text-[9px]">
                      {p.status}
                    </Badge>
                  </td>
                  <td className="p-3.5 uppercase">{p.payment_method || 'CARD / UPI'}</td>
                  <td className="p-3.5 text-muted-foreground">{formatRelativeTime(p.created_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
