import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { ApprovalItem } from '@/types/portal';
import { formatPaiseToINR, formatRelativeTime } from '@/lib/utils';
import {
  Clock,
  CheckCircle2,
  XCircle,
  AlertTriangle,
} from 'lucide-react';

export const ApprovalsPage: React.FC = () => {
  const [approvals, setApprovals] = useState<ApprovalItem[]>([]);
  const [filter, setFilter] = useState<'ALL' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'EXPIRED'>('PENDING');
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedTicket, setSelectedTicket] = useState<ApprovalItem | null>(null);
  const [actionType, setActionType] = useState<'APPROVE' | 'REJECT' | 'COUNTER_OFFER'>('APPROVE');
  const [reasonNote, setReasonNote] = useState<string>('');
  const [isSubmitting, setIsSubmitting] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const fetchApprovals = async () => {
    setIsLoading(true);
    try {
      const data = await api.listApprovals(filter);
      setApprovals(data);
      setLoadError(null);
    } catch (err: unknown) {
      setLoadError(err instanceof Error ? err.message : 'Unable to load approval tickets.');
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
      {/* Header & Filter Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight text-text-primary">
            Human Approval Decision Workbench (HITL)
          </h2>
          <p className="text-xs text-text-secondary mt-0.5">
            Server-escalated buyer agent discount proposals requiring authoritative merchant clearance.
          </p>
        </div>

        {/* Filter Tabs */}
        <div className="flex gap-1 bg-[#0D1424] p-1 rounded-xl border border-[#24314A]">
          {(['PENDING', 'APPROVED', 'REJECTED', 'ALL'] as const).map((f) => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`px-3 py-1.5 text-xs font-mono font-medium rounded-lg transition-all ${
                filter === f
                  ? 'bg-brand text-white shadow-sm font-semibold'
                  : 'text-text-muted hover:text-text-primary hover:bg-[#141D31]'
              }`}
            >
              {f}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-32 w-full rounded-xl bg-[#0D1424]" />
          ))}
        </div>
      ) : loadError ? (
        <div className="glass-panel rounded-2xl p-10 text-center border border-rose-400/30">
          <EmptyState icon={<AlertTriangle className="h-10 w-10 text-rose-300" />} title="Approval queue unavailable" description={loadError} />
          <Button onClick={fetchApprovals} variant="outline" size="sm" className="mt-4">Retry</Button>
        </div>
      ) : approvals.length === 0 ? (
        <div className="glass-panel rounded-2xl p-10 text-center border border-[#24314A]">
          <EmptyState
            icon={<Clock className="h-10 w-10 text-brand-bright" />}
            title={`No ${filter.toLowerCase()} approval tickets`}
            description="When buyer negotiations exceed autonomous policy limits, tickets are escalated here for merchant review."
          />
        </div>
      ) : (
        <div className="space-y-4">
          {approvals.map((ticket) => {
            const isPending = ticket.status === 'PENDING';
            return (
              <div
                key={ticket.id}
                className={`glass-panel rounded-xl p-5 border transition-all ${
                  isPending
                    ? 'border-amber-500/40 bg-[#0D1424]/90 shadow-glow-warning'
                    : 'border-[#24314A] bg-[#0D1424]/60 opacity-90'
                }`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-4">
                  <div className="flex items-center gap-3">
                    <span className="font-mono text-xs text-brand-bright font-bold">
                      Ticket {ticket.id.slice(0, 8)}
                    </span>
                    <Badge
                      variant={
                        ticket.status === 'PENDING'
                          ? 'warning'
                          : ticket.status === 'APPROVED'
                          ? 'success'
                          : 'destructive'
                      }
                      className="text-[10px] font-mono"
                    >
                      {ticket.status}
                    </Badge>
                  </div>
                  <span className="text-[11px] font-mono text-text-muted">
                    {formatRelativeTime(ticket.created_at)}
                  </span>
                </div>

                {/* Financial Decision Grid */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#070B14] p-3.5 rounded-xl border border-[#24314A]/80 mb-3">
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase">Requested Offer</span>
                    <p className="font-bold text-text-primary text-sm mt-0.5">
                      {formatPaiseToINR(ticket.requested_amount_paise)}
                    </p>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase">Proposed Discount</span>
                    <p className="font-bold text-amber-400 text-sm mt-0.5">
                      -{formatPaiseToINR(ticket.proposed_discount_paise)}
                    </p>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase">Discount Rate</span>
                    <p className="font-bold text-text-primary text-sm mt-0.5">
                      {ticket.proposed_discount_percentage}%
                    </p>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase">Policy Code</span>
                    <p className="font-mono text-xs text-brand-bright mt-0.5 truncate">
                      {ticket.policy_rule_code}
                    </p>
                  </div>
                </div>

                {ticket.reason_note && (
                  <div className="text-xs text-text-secondary italic mb-3 bg-[#141D31]/40 px-3 py-1.5 rounded-lg border border-[#24314A]/40">
                    Resolution note: {ticket.reason_note}
                  </div>
                )}

                {/* Action Area */}
                {isPending && (
                  <div className="flex justify-end gap-2.5 pt-2 border-t border-[#24314A]/60">
                    <Button
                      onClick={() => {
                        setSelectedTicket(ticket);
                        setActionType('REJECT');
                        setReasonNote('');
                      }}
                      variant="outline"
                      size="sm"
                      className="text-xs text-rose-400 border-rose-500/30 hover:bg-rose-500/10 hover:text-rose-300"
                    >
                      <XCircle className="h-3.5 w-3.5 mr-1" /> Reject Offer
                    </Button>
                    <Button
                      onClick={() => {
                        setSelectedTicket(ticket);
                        setActionType('APPROVE');
                        setReasonNote('');
                      }}
                      size="sm"
                      className="text-xs bg-emerald-500 hover:bg-emerald-600 text-[#070B14] font-semibold shadow-glow-success"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Approve Offer
                    </Button>
                  </div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {/* Action Dialog */}
      <Dialog
        isOpen={!!selectedTicket}
        onClose={() => setSelectedTicket(null)}
        title={`${actionType === 'APPROVE' ? 'Approve' : 'Reject'} Ticket ${selectedTicket?.id.slice(0, 8)}`}
        description={`Authoritatively ${actionType.toLowerCase()} the requested counter-offer of ${formatPaiseToINR(selectedTicket?.requested_amount_paise || 0)}.`}
      >
        <form onSubmit={handleResolve} className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 rounded-lg bg-rose-500/15 border border-rose-500/30 p-2.5 text-xs text-rose-300">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <Input
            label="Authoritative Reason Note"
            placeholder="e.g. Approved bulk order discount / Below floor margin rejection"
            value={reasonNote}
            onChange={(e) => setReasonNote(e.target.value)}
            required
          />

          <div className="flex justify-end gap-2.5 pt-2">
            <Button
              type="button"
              onClick={() => setSelectedTicket(null)}
              variant="outline"
              size="sm"
              className="text-xs"
            >
              Cancel
            </Button>
            <Button
              type="submit"
              isLoading={isSubmitting}
              className={`text-xs ${
                actionType === 'APPROVE'
                  ? 'bg-emerald-500 hover:bg-emerald-600 text-[#070B14] font-bold'
                  : 'bg-rose-500 hover:bg-rose-600 text-white'
              }`}
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

