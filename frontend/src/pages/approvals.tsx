import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { ApprovalItem } from '@/types/portal';
import { formatPaiseToINR, formatRelativeTime } from '@/lib/utils';
import { Clock, CheckCircle2, XCircle, AlertTriangle } from 'lucide-react';

export const ApprovalsPage: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED'>('PENDING');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedTicket, setSelectedTicket] = useState<ApprovalItem | null>(null);
  const [actionType, setActionType] = useState<'APPROVE' | 'REJECT' | 'COUNTER_OFFER'>('APPROVE');
  const [reasonNote, setReasonNote] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setIsLoading(true);
    try {
      const data = await api.listApprovals(filter);
      setApprovals(data);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchApprovals();
  }, [filter]);

  const handleResolve = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedTicket) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await api.resolveApproval(selectedTicket.id, {
        decision: actionType,
        reason_note: reasonNote.trim() || `Merchant ${actionType}`,
      });
      setSelectedTicket(null);
      setReasonNote('');
      fetchApprovals();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Resolution failed.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight">Human Approval Queue (HITL)</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Escalated buyer agent discount offers requiring explicit merchant authorization.
          </p>
        </div>
        <div className="flex gap-1.5 bg-muted/40 p-1 rounded-md border border-border">
          {(['PENDING', 'APPROVED', 'REJECTED', 'ALL'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1 text-xs font-semibold rounded transition-colors ${
                filter === f ? 'bg-primary text-primary-foreground shadow-sm' : 'text-muted-foreground hover:text-foreground'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-28 w-full" />)}
        </div>
      ) : approvals.length === 0 ? (
        <EmptyState
          icon={<Clock className="h-10 w-10" />}
          title={`No ${filter.toLowerCase()} approval tickets`}
          description="When buyer negotiations exceed merchant autonomy levels, tickets will appear here for review."
        />
      ) : (
        <div className="space-y-4">
          {approvals.map((ticket) => (
            <Card key={ticket.id} className="border-border bg-card/80">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-primary font-semibold">Ticket {ticket.id.slice(0, 8)}</span>
                    <Badge variant={ticket.status === 'PENDING' ? 'warning' : ticket.status === 'APPROVED' ? 'success' : 'destructive'} className="text-[9px]">
                      {ticket.status}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">{formatRelativeTime(ticket.created_at)}</span>
                </div>
              </CardHeader>
              <CardContent className="border-t border-border pt-3 text-xs space-y-3">
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 bg-muted/20 p-3 rounded">
                  <div>
                    <span className="text-muted-foreground">Requested Offer:</span>
                    <p className="font-bold text-foreground text-sm">{formatPaiseToINR(ticket.requested_amount_paise)}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Proposed Discount:</span>
                    <p className="font-bold text-amber-400 text-sm">-{formatPaiseToINR(ticket.proposed_discount_paise)}</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Discount Rate:</span>
                    <p className="font-bold text-foreground text-sm">{ticket.proposed_discount_percentage}%</p>
                  </div>
                  <div>
                    <span className="text-muted-foreground">Policy Rule:</span>
                    <p className="font-mono text-muted-foreground text-xs">{ticket.policy_rule_code}</p>
                  </div>
                </div>

                {ticket.reason_note && (
                  <p className="text-[11px] text-muted-foreground italic">Note: {ticket.reason_note}</p>
                )}

                {ticket.status === 'PENDING' && (
                  <div className="flex justify-end gap-2 pt-1">
                    <Button
                      onClick={() => { setSelectedTicket(ticket); setActionType('REJECT'); setReasonNote(''); }}
                      variant="outline"
                      size="sm"
                      className="text-destructive border-destructive/30 hover:bg-destructive/10"
                    >
                      <XCircle className="h-3.5 w-3.5 mr-1" /> Reject
                    </Button>
                    <Button
                      onClick={() => { setSelectedTicket(ticket); setActionType('APPROVE'); setReasonNote(''); }}
                      variant="primary"
                      size="sm"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Approve Offer
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Action Dialog */}
      <Dialog
        isOpen={!!selectedTicket}
        onClose={() => setSelectedTicket(null)}
        title={`${actionType === 'APPROVE' ? 'Approve' : 'Reject'} Ticket ${selectedTicket?.id.slice(0, 8)}`}
        description={`Authoritatively ${actionType.toLowerCase()} the requested counter-offer of ${formatPaiseToINR(selectedTicket?.requested_amount_paise || 0)}.`}
      >
        <form onSubmit={handleResolve} className="space-y-3.5">
          {error && (
            <div className="flex items-center gap-2 rounded bg-destructive/15 p-2 text-xs text-destructive">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <Input
            label="Decision Reason / Note"
            placeholder="e.g. Approved bulk order discount / Margin floor breach"
            value={reasonNote}
            onChange={(e) => setReasonNote(e.target.value)}
            required
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" onClick={() => setSelectedTicket(null)} variant="outline" size="sm">
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={isSubmitting}
              variant={actionType === 'APPROVE' ? 'primary' : 'destructive'}
              size="sm"
            >
              Confirm {actionType}
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
