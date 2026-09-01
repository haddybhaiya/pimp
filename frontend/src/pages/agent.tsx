import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Dialog, DialogFooter } from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { api } from '@/lib/api-client';
import {
  MerchantObservationSnapshot,
  MerchantProposalItem,
  MerchantDiagnosisItem,
  MerchantAgentAnalyzeResponse,
} from '@/types/portal';
import { formatRelativeTime } from '@/lib/utils';
import {
  Bot,
  Sparkles,
  TrendingUp,
  AlertCircle,
  CheckCircle2,
  XCircle,
  FlaskConical,
  RefreshCw,
  Search,
  Activity,
  Layers,
  ShieldCheck,
  HelpCircle,
} from 'lucide-react';

export const AgentPage: React.FC = () => {
  const [snapshot, setSnapshot] = useState<MerchantObservationSnapshot | null>(null);
  const [proposals, setProposals] = useState<MerchantProposalItem[]>([]);
  const [diagnoses, setDiagnoses] = useState<MerchantDiagnosisItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Review modal state
  const [selectedProposal, setSelectedProposal] = useState<MerchantProposalItem | null>(null);
  const [reviewAction, setReviewAction] = useState<'APPROVE' | 'REJECT' | 'CONVERT_TO_EXPERIMENT' | null>(null);
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [isReviewing, setIsReviewing] = useState<boolean>(false);

  const fetchData = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [snapData, propData] = await Promise.all([
        api.getAgentSnapshot(),
        api.listProposals(),
      ]);
      setSnapshot(snapData);
      setProposals(propData);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to load merchant agent snapshot.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  const handleRunAnalysis = async () => {
    setIsAnalyzing(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const res: MerchantAgentAnalyzeResponse = await api.runAgentAnalysis();
      setSnapshot(res.snapshot);
      setDiagnoses(res.diagnoses);
      setProposals(res.proposals);
      setSuccessMessage(`Analysis completed: ${res.diagnoses.length} findings, ${res.proposals.length} proposals formulated.`);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Agent analysis turn failed.');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const handleConfirmReview = async () => {
    if (!selectedProposal || !reviewAction) return;
    setIsReviewing(true);
    try {
      await api.reviewProposal(selectedProposal.id, {
        decision: reviewAction,
        rejection_reason: reviewAction === 'REJECT' ? rejectionReason : undefined,
      });
      setSelectedProposal(null);
      setReviewAction(null);
      setRejectionReason('');
      await fetchData();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to update proposal state.');
    } finally {
      setIsReviewing(false);
    }
  };

  const getRiskBadge = (risk: string) => {
    switch (risk) {
      case 'READ_ONLY':
        return <Badge variant="secondary" className="text-[10px] font-mono">READ ONLY</Badge>;
      case 'LOW_RISK_REVERSIBLE':
        return <Badge variant="success" className="text-[10px] font-mono">LOW RISK (REVERSIBLE)</Badge>;
      case 'APPROVAL_REQUIRED':
        return <Badge variant="warning" className="text-[10px] font-mono">APPROVAL REQUIRED</Badge>;
      case 'PROHIBITED':
        return <Badge variant="destructive" className="text-[10px] font-mono">PROHIBITED</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px] font-mono">{risk}</Badge>;
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <Badge variant="success" className="text-[10px] font-mono">APPROVED</Badge>;
      case 'REJECTED':
        return <Badge variant="destructive" className="text-[10px] font-mono">REJECTED</Badge>;
      case 'CONVERTED_TO_EXPERIMENT':
        return <Badge variant="default" className="text-[10px] font-mono bg-brand-bright/10 text-brand-bright border-brand-bright/30">EXPERIMENT</Badge>;
      case 'UNDER_REVIEW':
        return <Badge variant="warning" className="text-[10px] font-mono">UNDER REVIEW</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px] font-mono">PROPOSED</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#1B1C1E] p-5 rounded-2xl border border-white/10 shadow-lg">
        <div className="flex items-start gap-3.5">
          <div className="h-10 w-10 rounded-xl bg-brand-bright/10 border border-brand-bright/30 flex items-center justify-center shrink-0">
            <Bot className="h-5 w-5 text-brand-bright" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold tracking-tight text-text-primary">Merchant Optimization Agent</h2>
              <Badge variant="outline" className="text-[10px] font-mono border-brand-bright/40 text-brand-bright">
                Phase 7 Intelligence
              </Badge>
            </div>
            <p className="text-xs text-text-muted mt-1 max-w-xl">
              Merchant-side intelligence engine. Observes live commerce telemetry, diagnoses demand friction, and formulates evidence-backed proposals for human review.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchData}
            isLoading={isLoading}
            className="text-xs border-white/10 bg-[#0C0F11] hover:bg-[#202426]"
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" /> Refresh
          </Button>
          <Button
            size="sm"
            onClick={handleRunAnalysis}
            isLoading={isAnalyzing}
            className="text-xs font-semibold bg-brand-bright text-[#070B14] hover:bg-brand-bright/90 shadow-md shadow-brand-bright/10"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5" /> Run Agent Analysis
          </Button>
        </div>
      </div>

      {/* Safety & Invariant Indicator */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#171A1C] rounded-xl border border-emerald-500/20 text-xs">
        <div className="flex items-center gap-2 text-emerald-400">
          <ShieldCheck className="h-4 w-4 shrink-0" />
          <span><strong>Safety Principle:</strong> Intelligence ≠ Authority. The Merchant Agent cannot mutate prices, alter financial policy, or grant capabilities directly.</span>
        </div>
        <div className="flex items-center gap-2 text-text-muted font-mono text-[11px]">
          <span>Autonomy: Level {snapshot?.autonomy_level ?? 1} (Bounded)</span>
        </div>
      </div>

      {/* Feedback Alerts */}
      {errorMessage && (
        <div className="flex items-center gap-2.5 rounded-xl border border-rose-500/30 bg-rose-500/10 p-3.5 text-xs text-rose-200">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}
      {successMessage && (
        <div className="flex items-center gap-2.5 rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-3.5 text-xs text-emerald-200">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* 1. Authoritative Observation Telemetry */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Activity className="h-4 w-4 text-brand-bright" />
            <h3 className="text-sm font-bold tracking-tight text-text-primary uppercase font-mono">
              Authoritative Commerce Telemetry
            </h3>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            Window: 30 Days (Tenant Scoped)
          </span>
        </div>

        {isLoading ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {[1, 2, 3, 4, 5, 6, 7, 8].map((i) => (
              <Skeleton key={i} className="h-24 w-full rounded-xl bg-[#202426]" />
            ))}
          </div>
        ) : snapshot?.telemetry ? (
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-3">
            {snapshot.telemetry.map((t) => (
              <Card key={t.metric_name} className="bg-[#202426] border-white/10 p-3.5 rounded-xl hover:border-brand-bright/30 transition-all">
                <div className="flex items-center justify-between gap-1 mb-1.5">
                  <span className="text-[10px] font-mono text-text-muted uppercase truncate">
                    {t.metric_name.replace(/_/g, ' ')}
                  </span>
                  <Badge
                    variant={
                      t.category === 'OBSERVED'
                        ? 'default'
                        : t.category === 'DERIVED'
                        ? 'secondary'
                        : 'warning'
                    }
                    className="text-[9px] font-mono px-1.5 py-0"
                  >
                    {t.category}
                  </Badge>
                </div>
                <div className="text-lg font-bold text-text-primary font-mono tracking-tight">
                  {t.formatted_value}
                </div>
                <p className="text-[10px] text-text-muted mt-1 truncate" title={t.description}>
                  {t.description}
                </p>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<HelpCircle className="h-8 w-8" />}
            title="No telemetry data recorded"
            description="Commerce events and buyer interactions will populate this live observation matrix."
          />
        )}
      </div>

      {/* 2. Diagnostic Findings */}
      {diagnoses.length > 0 && (
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Search className="h-4 w-4 text-amber-400" />
            <h3 className="text-sm font-bold tracking-tight text-text-primary uppercase font-mono">
              Diagnostic Findings & Evidence Links
            </h3>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {diagnoses.map((d, idx) => (
              <Card key={idx} className="bg-[#202426] border-amber-500/20 p-4 rounded-xl">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs text-amber-400 font-semibold">{d.pattern}</span>
                  <Badge variant={d.severity === 'HIGH' ? 'destructive' : 'warning'} className="text-[10px]">
                    {d.severity} SEVERITY
                  </Badge>
                </div>
                <p className="text-xs text-text-secondary leading-relaxed mb-3">{d.summary}</p>
                <div className="flex flex-wrap items-center gap-1.5 pt-2 border-t border-white/10 text-[11px] font-mono text-text-muted">
                  <span>Evidence:</span>
                  {d.evidence_references.map((ev, i) => (
                    <span key={i} className="px-1.5 py-0.5 rounded bg-[#202426] text-brand-bright text-[10px]">
                      {ev}
                    </span>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 3. Optimization Proposals */}
      <div className="space-y-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-brand-bright" />
            <h3 className="text-sm font-bold tracking-tight text-text-primary uppercase font-mono">
              Optimization Proposals ({proposals.length})
            </h3>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            Approval-First Governance
          </span>
        </div>

        {isLoading ? (
          <div className="space-y-3">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-32 w-full rounded-xl bg-[#202426]" />
            ))}
          </div>
        ) : proposals.length === 0 ? (
          <EmptyState
            icon={<Sparkles className="h-10 w-10 text-brand-bright" />}
            title="No optimization proposals formulated"
            description="Run the Merchant Agent Analysis to discover friction points and generate actionable proposals."
          />
        ) : (
          <div className="space-y-3">
            {proposals.map((p) => {
              const isPending = p.status === 'PROPOSED' || p.status === 'UNDER_REVIEW';
              return (
                <Card key={p.id} className="bg-[#1B1C1E] border-white/10 p-5 rounded-2xl hover:border-brand-bright/40 transition-all">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                    <div className="flex items-center gap-2.5">
                      <span className="font-mono text-xs text-brand-bright font-bold">
                        {p.proposal_type}
                      </span>
                      {getRiskBadge(p.risk_level)}
                      {getStatusBadge(p.status)}
                    </div>
                    <span className="text-[11px] font-mono text-text-muted">
                      {formatRelativeTime(p.created_at)}
                    </span>
                  </div>

                  <h4 className="text-base font-bold text-text-primary mb-1.5">{p.title}</h4>
                  <p className="text-xs text-text-secondary mb-3 leading-relaxed">{p.proposed_change}</p>

                  {/* Hypothesis & Expected Impact Box */}
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-3 bg-[#0C0F11] p-3.5 rounded-xl border border-white/10 mb-3 text-xs">
                    <div>
                      <span className="text-[10px] font-mono text-text-muted uppercase block">Observation & Hypothesis</span>
                      <p className="text-text-secondary text-xs mt-0.5">{p.hypothesis}</p>
                    </div>
                    <div>
                      <span className="text-[10px] font-mono text-text-muted uppercase block">Expected Metric Impact</span>
                      <div className="flex items-center gap-1.5 text-emerald-400 font-semibold mt-0.5">
                        <TrendingUp className="h-3.5 w-3.5" />
                        <span>{p.expected_effect}</span>
                      </div>
                      <span className="text-[10px] font-mono text-text-muted">Target: {p.expected_metric}</span>
                    </div>
                  </div>

                  {/* Evidence References */}
                  <div className="flex flex-wrap items-center gap-1.5 mb-3 text-[11px] font-mono text-text-muted">
                    <span>Evidence Links:</span>
                    {p.evidence.map((ev, i) => (
                      <span key={i} className="px-1.5 py-0.5 rounded bg-[#202426] text-brand-bright text-[10px]">
                        {ev}
                      </span>
                    ))}
                    <span className="ml-auto text-[10px]">Confidence: {Math.round(p.confidence * 100)}%</span>
                  </div>

                  {/* Review Action Footer */}
                  {isPending && p.risk_level !== 'PROHIBITED' && (
                    <div className="flex justify-end gap-2.5 pt-3 border-t border-white/10">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedProposal(p);
                          setReviewAction('REJECT');
                        }}
                        className="text-xs text-rose-300 border-rose-500/30 hover:bg-rose-500/10"
                      >
                        <XCircle className="h-3.5 w-3.5 mr-1" /> Reject
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => {
                          setSelectedProposal(p);
                          setReviewAction('CONVERT_TO_EXPERIMENT');
                        }}
                        className="text-xs border-brand-bright/40 text-brand-bright hover:bg-brand-bright/10"
                      >
                        <FlaskConical className="h-3.5 w-3.5 mr-1" /> Convert to Experiment
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => {
                          setSelectedProposal(p);
                          setReviewAction('APPROVE');
                        }}
                        className="text-xs font-semibold bg-emerald-500 text-slate-950 hover:bg-emerald-400"
                      >
                        <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Approve Proposal
                      </Button>
                    </div>
                  )}

                  {p.rejection_reason && (
                    <div className="text-xs text-rose-300 italic bg-rose-500/10 p-2.5 rounded-lg border border-rose-500/20 mt-2">
                      Rejection Reason: {p.rejection_reason}
                    </div>
                  )}
                </Card>
              );
            })}
          </div>
        )}
      </div>

      {/* Review Dialog */}
      <Dialog
        isOpen={selectedProposal !== null && reviewAction !== null}
        onClose={() => {
          setSelectedProposal(null);
          setReviewAction(null);
        }}
        title={
          reviewAction === 'APPROVE'
            ? 'Approve Optimization Proposal'
            : reviewAction === 'REJECT'
            ? 'Reject Proposal'
            : 'Convert to Structured Experiment'
        }
        description={`Confirm action for "${selectedProposal?.title}".`}
      >
        <div className="space-y-3 py-2 text-xs">
          {reviewAction === 'REJECT' ? (
            <div>
              <label className="block text-[11px] font-mono text-text-muted uppercase mb-1">
                Reason for Rejection
              </label>
              <textarea
                className="w-full h-20 bg-[#0C0F11] border border-white/10 rounded-lg p-2 text-xs text-text-primary focus:border-brand-bright focus:outline-none"
                placeholder="Explain why this proposal is unsuitable..."
                value={rejectionReason}
                onChange={(e) => setRejectionReason(e.target.value)}
              />
            </div>
          ) : (
            <p className="text-text-secondary leading-relaxed">
              {reviewAction === 'APPROVE'
                ? 'Approving this proposal registers merchant administrative consent. In Phase 7, all changes remain supervised.'
                : 'Converting this proposal into a structured experiment will register baseline metrics and allow deterministic measurement.'}
            </p>
          )}
        </div>
        <DialogFooter>
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              setSelectedProposal(null);
              setReviewAction(null);
            }}
          >
            Cancel
          </Button>
          <Button
            size="sm"
            isLoading={isReviewing}
            onClick={handleConfirmReview}
            className={
              reviewAction === 'REJECT'
                ? 'bg-rose-500 text-white hover:bg-rose-600'
                : 'bg-emerald-500 text-slate-950 hover:bg-emerald-400'
            }
          >
            Confirm
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};
