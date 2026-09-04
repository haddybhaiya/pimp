import React, { useCallback, useEffect, useRef, useState } from 'react';
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
  AutonomyStatusResponse,
  AutonomyActionItem,
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
  Power,
  History,
  RotateCcw,
  Zap,
  FileJson,
} from 'lucide-react';

export const AgentPage: React.FC = () => {
  const [snapshot, setSnapshot] = useState<MerchantObservationSnapshot | null>(null);
  const [proposals, setProposals] = useState<MerchantProposalItem[]>([]);
  const [diagnoses, setDiagnoses] = useState<MerchantDiagnosisItem[]>([]);
  const [autonomyStatus, setAutonomyStatus] = useState<AutonomyStatusResponse | null>(null);
  const [autonomyActions, setAutonomyActions] = useState<AutonomyActionItem[]>([]);
  const [autonomyStatusError, setAutonomyStatusError] = useState<string | null>(null);
  const [autonomyActionsError, setAutonomyActionsError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isAnalyzing, setIsAnalyzing] = useState<boolean>(false);
  const [isTogglingKillSwitch, setIsTogglingKillSwitch] = useState<boolean>(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // Review modal state
  const [selectedProposal, setSelectedProposal] = useState<MerchantProposalItem | null>(null);
  const [reviewAction, setReviewAction] = useState<'APPROVE' | 'REJECT' | 'CONVERT_TO_EXPERIMENT' | null>(null);
  const [rejectionReason, setRejectionReason] = useState<string>('');
  const [experimentTargetValue, setExperimentTargetValue] = useState<string>('');
  const [isReviewing, setIsReviewing] = useState<boolean>(false);

  // Autonomous execution & Rollback state
  const [executingProposalId, setExecutingProposalId] = useState<string | null>(null);
  const [selectedRollbackAction, setSelectedRollbackAction] = useState<AutonomyActionItem | null>(null);
  const [rollbackReason, setRollbackReason] = useState<string>('');
  const [isRollingBack, setIsRollingBack] = useState<boolean>(false);
  const [selectedSnapshot, setSelectedSnapshot] = useState<Record<string, unknown> | null>(null);

  const requestVersionRef = useRef(0);

  const closeReviewDialog = useCallback(() => {
    setSelectedProposal(null);
    setReviewAction(null);
    setRejectionReason('');
    setExperimentTargetValue('');
  }, []);

  const closeRollbackDialog = useCallback(() => {
    setSelectedRollbackAction(null);
    setRollbackReason('');
  }, []);

  const fetchData = useCallback(async () => {
    const requestVersion = ++requestVersionRef.current;
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const [snapData, propData, statusResult, actionsResult] = await Promise.all([
        api.getAgentSnapshot(),
        api.listProposals(),
        api.getAutonomyStatus().then(
          (value) => ({ value, error: null as string | null }),
          (error: unknown) => ({
            value: null,
            error: error instanceof Error ? error.message : 'Autonomy status is unavailable.',
          })
        ),
        api.getAutonomyActions(20).then(
          (value) => ({ value, error: null as string | null }),
          (error: unknown) => ({
            value: null,
            error: error instanceof Error ? error.message : 'Autonomy action ledger is unavailable.',
          })
        ),
      ]);
      if (requestVersion === requestVersionRef.current) {
        setSnapshot(snapData);
        setProposals(propData);
        setAutonomyStatusError(statusResult.error);
        setAutonomyActionsError(actionsResult.error);
        if (statusResult.value) setAutonomyStatus(statusResult.value);
        if (actionsResult.value) setAutonomyActions(actionsResult.value);
      }
    } catch (err: unknown) {
      if (requestVersion === requestVersionRef.current) {
        setErrorMessage(err instanceof Error ? err.message : 'Failed to load merchant agent snapshot.');
      }
    } finally {
      if (requestVersion === requestVersionRef.current) {
        setIsLoading(false);
      }
    }
  }, []);

  useEffect(() => {
    void fetchData();
  }, []);

  const handleToggleKillSwitch = async () => {
    if (!autonomyStatus) {
      setErrorMessage('Autonomy status is unavailable. Refresh before changing the kill switch.');
      return;
    }
    setIsTogglingKillSwitch(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      const nextState = !autonomyStatus.kill_switch_enabled;
      await api.setKillSwitch(
        nextState,
        nextState ? 'Admin activated kill switch' : 'Admin deactivated kill switch'
      );
      setSuccessMessage(
        nextState
          ? 'Autonomy Kill Switch ACTIVATED. All autonomous side effects paused.'
          : 'Kill Switch deactivated. Controlled autonomy resumed.'
      );
      await fetchData();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to toggle kill switch.');
    } finally {
      setIsTogglingKillSwitch(false);
    }
  };

  const handleExecuteAutonomously = async (p: MerchantProposalItem) => {
    setExecutingProposalId(p.id);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      if (p.proposal_type === 'SUGGEST_BOUNDED_EXPERIMENT') {
        throw new Error('Approved experiments are started from the Experiments page.');
      }
      const target = String(
        p.metadata_payload.target_product_id ?? p.metadata_payload.product_id ?? p.target_entity
      );
      const products = await api.listProducts();
      const product = products.find((item) => item.id === target || item.sku === target);
      if (!product) {
        throw new Error('The proposal target is no longer available for autonomous execution.');
      }
      const res = await api.executeAutonomyAction(p.id, product.version);
      setSuccessMessage(`Proposal executed autonomously: Action ID ${res.action.id.slice(0, 8)}.`);
      await fetchData();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Autonomous execution failed.');
    } finally {
      setExecutingProposalId(null);
    }
  };

  const handleConfirmRollback = async () => {
    if (!selectedRollbackAction || !rollbackReason) return;
    setIsRollingBack(true);
    setErrorMessage(null);
    setSuccessMessage(null);
    try {
      await api.rollbackAutonomyAction(
        selectedRollbackAction.id,
        selectedRollbackAction.target_version_after,
        rollbackReason
      );
      setSuccessMessage(`Action ${selectedRollbackAction.id.slice(0, 8)} rolled back successfully.`);
      setSelectedRollbackAction(null);
      setRollbackReason('');
      await fetchData();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Rollback failed.');
    } finally {
      setIsRollingBack(false);
    }
  };

  const handleRunAnalysis = async () => {
    if (isAnalyzing) return;
    ++requestVersionRef.current;
    setIsAnalyzing(true);
    setIsLoading(false);
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
    const proposal = selectedProposal;
    const action = reviewAction;
    const targetValue = Number(experimentTargetValue);
    if (
      action === 'CONVERT_TO_EXPERIMENT' &&
      (experimentTargetValue.trim() === '' || !Number.isFinite(targetValue) || targetValue < 0)
    ) {
      setErrorMessage('A valid non-negative target value is required to convert a proposal to an experiment.');
      return;
    }

    setIsReviewing(true);
    setErrorMessage(null);
    try {
      if (action === 'CONVERT_TO_EXPERIMENT') {
        const baseline = 0.0;
        const target = targetValue;
        await api.createExperiment({
          proposal_id: proposal.id,
          title: `Experiment: ${proposal.title}`,
          hypothesis: proposal.hypothesis,
          target_metric: proposal.expected_metric,
          baseline_value: baseline,
          target_value: target,
          proposed_variation: { description: proposal.proposed_change },
        });
        await api.reviewProposal(proposal.id, {
          decision: 'CONVERT_TO_EXPERIMENT',
        });
        setSuccessMessage(`Proposal converted to structured experiment targeting ${proposal.expected_metric}.`);
      } else {
        await api.reviewProposal(proposal.id, {
          decision: action,
          rejection_reason: action === 'REJECT' ? rejectionReason : undefined,
        });
        setSuccessMessage(`Proposal ${action === 'APPROVE' ? 'approved' : 'rejected'} successfully.`);
      }
      closeReviewDialog();
      await fetchData();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to submit proposal review.');
    } finally {
      setIsReviewing(false);
    }
  };

  const openReviewDialog = (
    proposal: MerchantProposalItem,
    action: 'APPROVE' | 'REJECT' | 'CONVERT_TO_EXPERIMENT'
  ) => {
    setSelectedProposal(proposal);
    setReviewAction(action);
    setRejectionReason('');
    setExperimentTargetValue('');
  };

  return (
    <div className="space-y-6">
      {/* Header & Primary Action Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-white/10 pb-5">
        <div className="flex items-center gap-3">
          <div className="h-10 w-10 rounded-xl bg-brand-bright/10 border border-brand-bright/30 flex items-center justify-center text-brand-bright">
            <Bot className="h-5 w-5" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold tracking-tight text-text-primary">Merchant Optimization Agent</h2>
              <Badge variant="outline" className="text-[10px] font-mono border-brand-bright/40 text-brand-bright">
                Controlled autonomy
              </Badge>
            </div>
            <p className="text-xs text-text-muted mt-1 max-w-xl">
              Merchant-side intelligence engine. Observes live commerce telemetry, diagnoses demand friction, and executes low-risk reversible optimizations autonomously.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={() => void fetchData()}
            isLoading={isLoading}
            disabled={isAnalyzing}
            className="text-xs border-white/10 bg-[#0C0F11] hover:bg-[#202426]"
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" /> Refresh
          </Button>
          <Button
            size="sm"
            onClick={handleRunAnalysis}
            isLoading={isAnalyzing}
            disabled={isLoading}
            className="text-xs font-semibold bg-brand-bright text-[#070B14] hover:bg-brand-bright/90 shadow-md shadow-brand-bright/10"
          >
            <Sparkles className="h-3.5 w-3.5 mr-1.5" /> Run Agent Analysis
          </Button>
        </div>
      </div>

      {/* Controlled Autonomy & Kill Switch Panel */}
      <Card className="p-4 bg-[#171A1C] border-white/10">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div
              className={`p-2.5 rounded-xl border ${
                !autonomyStatus
                  ? 'bg-amber-500/10 border-amber-500/30 text-amber-400'
                  : autonomyStatus.kill_switch_enabled
                  ? 'bg-rose-500/10 border-rose-500/30 text-rose-400'
                  : 'bg-emerald-500/10 border-emerald-500/30 text-emerald-400'
              }`}
            >
              <Power className="h-5 w-5" />
            </div>
            <div>
              <div className="flex items-center gap-2">
                <span className="font-bold text-sm text-text-primary">Master Autonomy Kill Switch</span>
                <Badge
                  variant={autonomyStatus?.kill_switch_enabled ? 'destructive' : 'default'}
                  className="text-[10px] font-mono"
                >
                  {!autonomyStatus
                    ? 'STATUS UNAVAILABLE'
                    : autonomyStatus.kill_switch_enabled
                    ? 'KILL SWITCH ACTIVE'
                    : 'AUTONOMY ENGAGED'}
                </Badge>
                {autonomyStatus?.anomaly_state && autonomyStatus.anomaly_state !== 'NORMAL' && (
                  <Badge variant="outline" className="text-[10px] font-mono border-amber-500/40 text-amber-400">
                    ANOMALY: {autonomyStatus.anomaly_state}
                  </Badge>
                )}
              </div>
              <p className="text-xs text-text-muted mt-0.5">
                {!autonomyStatus
                  ? 'Autonomy status could not be loaded. Mutations are unavailable until refreshed.'
                  : autonomyStatus.kill_switch_enabled
                  ? 'All autonomous mutations paused. System operates strictly in manual approval mode.'
                  : 'Allows autonomous execution of low-risk reversible optimizations within configured hourly/daily budgets.'}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-right font-mono text-[11px] text-text-muted">
              <div>
                Hourly Budget:{' '}
                <span className="text-text-primary font-bold">
                  {autonomyStatus?.hourly_executions_count ?? 0}
                </span>{' '}
                used
              </div>
              <div>
                Daily Budget:{' '}
                <span className="text-text-primary font-bold">
                  {autonomyStatus?.daily_executions_count ?? 0}
                </span>{' '}
                used
              </div>
            </div>
            <Button
              size="sm"
              variant={autonomyStatus?.kill_switch_enabled ? 'primary' : 'destructive'}
              isLoading={isTogglingKillSwitch}
              onClick={handleToggleKillSwitch}
              disabled={!autonomyStatus}
              title={!autonomyStatus ? 'Autonomy status is unavailable. Refresh and try again.' : undefined}
              className="text-xs font-semibold shrink-0"
            >
              <Power className="h-3.5 w-3.5 mr-1.5" />
              {autonomyStatus?.kill_switch_enabled ? 'Deactivate Kill Switch' : 'Trigger Kill Switch'}
            </Button>
          </div>
        </div>
      </Card>

      {(autonomyStatusError || autonomyActionsError) && (
        <div className="flex items-center gap-2.5 rounded-xl border border-amber-500/30 bg-amber-500/10 p-3.5 text-xs text-amber-100">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{autonomyStatusError ?? autonomyActionsError}</span>
        </div>
      )}

      {/* Safety & Invariant Indicator */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#171A1C] rounded-xl border border-emerald-500/20 text-xs">
        <div className="flex items-center gap-2 text-emerald-400">
          <ShieldCheck className="h-4 w-4 shrink-0" />
          <span>
            <strong>Safety Principle:</strong> Intelligence ≠ Authority. The Merchant Agent cannot mutate prices, alter financial policy, or bypass deterministic rollback gates.
          </span>
        </div>
        <div className="flex items-center gap-2 text-text-muted font-mono text-[11px]">
          <span>Autonomy: Level {snapshot?.autonomy_level ?? 1} (Controlled)</span>
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
        ) : snapshot?.telemetry && snapshot.telemetry.length > 0 ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {snapshot.telemetry.map((t) => (
              <Card key={t.metric_name} className="p-3.5 bg-[#171A1C] border-white/10">
                <div className="flex items-center justify-between text-[11px] font-mono text-text-muted mb-1">
                  <span>{t.category}</span>
                  <Badge variant="outline" className="text-[9px] px-1 py-0 border-white/10">
                    N={t.sample_size}
                  </Badge>
                </div>
                <div className="text-xl font-bold font-mono text-text-primary mt-1">
                  {t.formatted_value}
                </div>
                <div className="text-xs text-text-secondary mt-1 font-medium truncate">
                  {t.description}
                </div>
              </Card>
            ))}
          </div>
        ) : (
          <EmptyState
            icon={<Search className="h-10 w-10 text-brand-bright" />}
            title="No telemetry signals available"
            description="Run agent analysis or seed simulated commerce traffic to observe telemetry."
          />
        )}
      </div>

      {/* 2. Structured Diagnoses */}
      {diagnoses.length > 0 && (
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Search className="h-4 w-4 text-brand-bright" />
            <h3 className="text-sm font-bold tracking-tight text-text-primary uppercase font-mono">
              Diagnostic Findings ({diagnoses.length})
            </h3>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {diagnoses.map((d, idx) => (
              <Card key={idx} className="p-3.5 bg-[#171A1C] border-white/10">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-mono text-xs font-bold text-text-primary">{d.pattern}</span>
                  <Badge
                    variant={d.severity === 'HIGH' ? 'destructive' : d.severity === 'MEDIUM' ? 'default' : 'secondary'}
                    className="text-[10px] font-mono"
                  >
                    {d.severity}
                  </Badge>
                </div>
                <p className="text-xs text-text-secondary mb-2.5 leading-relaxed">{d.summary}</p>
                <div className="flex flex-wrap gap-1 mt-auto">
                  {d.evidence_references.map((ev, i) => (
                    <span key={i} className="text-[10px] font-mono px-1.5 py-0.5 rounded bg-[#0C0F11] border border-white/10 text-brand-bright">
                      {ev}
                    </span>
                  ))}
                </div>
              </Card>
            ))}
          </div>
        </div>
      )}

      {/* 3. Formulated Optimization Proposals */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <Layers className="h-4 w-4 text-brand-bright" />
            <h3 className="text-sm font-bold tracking-tight text-text-primary uppercase font-mono">
              Proposals ({proposals.length})
            </h3>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            Evidence-Backed & Risk Classified
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
            icon={<Bot className="h-10 w-10 text-brand-bright" />}
            title="No optimization proposals formulated"
            description="Run an analysis turn to evaluate current store observations and formulate proposals."
          />
        ) : (
          <div className="space-y-3">
            {proposals.map((p) => {
              const isPending = p.status === 'PROPOSED' || p.status === 'UNDER_REVIEW';
              const canAutoExecute =
                p.risk_level === 'LOW_RISK_REVERSIBLE' &&
                isPending &&
                p.proposal_type !== 'SUGGEST_BOUNDED_EXPERIMENT' &&
                autonomyStatus !== null &&
                !autonomyStatus.kill_switch_enabled &&
                !['PAUSE_AUTONOMY', 'REQUIRE_HUMAN_REVIEW'].includes(autonomyStatus.anomaly_state);

              return (
                <Card key={p.id} className="p-4 bg-[#171A1C] border-white/10">
                  <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-2">
                    <div className="flex items-center gap-2">
                      <span className="text-xs font-mono font-bold text-brand-bright">{p.proposal_type}</span>
                      <Badge
                        variant={
                          p.risk_level === 'PROHIBITED'
                            ? 'destructive'
                            : p.risk_level === 'APPROVAL_REQUIRED'
                            ? 'default'
                            : 'secondary'
                        }
                        className="text-[10px] font-mono"
                      >
                        {p.risk_level}
                      </Badge>
                      <Badge variant="outline" className="text-[10px] font-mono border-white/10 text-text-muted">
                        {p.status}
                      </Badge>
                    </div>
                    <span className="text-[11px] font-mono text-text-muted">{formatRelativeTime(p.created_at)}</span>
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
                    <div className="flex flex-wrap justify-end gap-2.5 pt-3 border-t border-white/10">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openReviewDialog(p, 'REJECT')}
                        className="text-xs text-rose-300 border-rose-500/30 hover:bg-rose-500/10"
                      >
                        <XCircle className="h-3.5 w-3.5 mr-1" /> Reject
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => openReviewDialog(p, 'CONVERT_TO_EXPERIMENT')}
                        className="text-xs border-brand-bright/40 text-brand-bright hover:bg-brand-bright/10"
                      >
                        <FlaskConical className="h-3.5 w-3.5 mr-1" /> Convert to Experiment
                      </Button>
                      <Button
                        size="sm"
                        onClick={() => openReviewDialog(p, 'APPROVE')}
                        className="text-xs font-semibold bg-emerald-500 text-slate-950 hover:bg-emerald-400"
                      >
                        <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Approve
                      </Button>

                      {/* Phase 8 Autonomous Execution Button */}
                      {canAutoExecute && (
                        <Button
                          size="sm"
                          variant="outline"
                          isLoading={executingProposalId === p.id}
                          onClick={() => handleExecuteAutonomously(p)}
                          className="text-xs font-semibold border-brand-bright/40 text-brand-bright hover:bg-brand-bright/10"
                        >
                          <Zap className="h-3.5 w-3.5 mr-1" /> Execute Autonomously
                        </Button>
                      )}
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

      {/* 4. Autonomous Actions Ledger & Deterministic Rollback */}
      <div>
        <div className="flex items-center justify-between mb-3">
          <div className="flex items-center gap-2">
            <History className="h-4 w-4 text-brand-bright" />
            <h3 className="text-sm font-bold tracking-tight text-text-primary uppercase font-mono">
              Autonomous Actions Ledger ({autonomyActions.length})
            </h3>
          </div>
          <span className="text-[11px] font-mono text-text-muted">
            Immutable Audit Linkage & Rollback Snapshots
          </span>
        </div>

        {autonomyActions.length === 0 ? (
          <EmptyState
            icon={<History className="h-10 w-10 text-brand-bright" />}
            title="No autonomous actions recorded"
            description="Autonomous mutations will appear here with version-checked deterministic rollback snapshots."
          />
        ) : (
          <div className="space-y-2.5">
            {autonomyActions.map((act) => (
              <Card
                key={act.id}
                className="p-3.5 bg-[#171A1C] border-white/10 flex flex-col md:flex-row md:items-center justify-between gap-3 text-xs"
              >
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-text-primary font-mono">{act.action_type}</span>
                    <Badge
                      variant={act.status === 'EXECUTED' ? 'default' : 'secondary'}
                      className="text-[10px] font-mono"
                    >
                      {act.status}
                    </Badge>
                    <Badge variant="outline" className="text-[10px] font-mono border-white/10 text-text-muted">
                      Rollback: {act.rollback_status}
                    </Badge>
                  </div>
                  <div className="text-[11px] text-text-muted font-mono">
                    Target: {act.target_entity_type} ({act.target_entity_id.slice(0, 8)}) | Version: v
                    {act.target_version_before} → v{act.target_version_after} |{' '}
                    {formatRelativeTime(act.created_at)}
                  </div>
                  {act.stopping_reason && (
                    <div className="text-[11px] text-amber-300 italic">
                      Reason: {act.stopping_reason}
                    </div>
                  )}
                </div>

                <div className="flex items-center gap-2 shrink-0">
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => setSelectedSnapshot(act.rollback_snapshot)}
                    className="text-[11px] border-white/10 bg-[#0C0F11] hover:bg-[#202426]"
                  >
                    <FileJson className="h-3 w-3 mr-1" /> Snapshot
                  </Button>
                  {act.rollback_status === 'AVAILABLE' && (
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedRollbackAction(act);
                        setRollbackReason('Merchant administrative rollback');
                      }}
                      className="text-[11px] text-amber-300 border-amber-500/30 hover:bg-amber-500/10"
                    >
                      <RotateCcw className="h-3 w-3 mr-1" /> Rollback
                    </Button>
                  )}
                </div>
              </Card>
            ))}
          </div>
        )}
      </div>

      {/* Review Proposal Dialog */}
      <Dialog
        isOpen={selectedProposal !== null && reviewAction !== null}
        onClose={closeReviewDialog}
        title={
          reviewAction === 'APPROVE'
            ? 'Approve Optimization Proposal'
            : reviewAction === 'REJECT'
            ? 'Reject Optimization Proposal'
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
          ) : reviewAction === 'CONVERT_TO_EXPERIMENT' ? (
            <div>
              <label className="block text-[11px] font-mono text-text-muted uppercase mb-1">
                Target value for {selectedProposal?.expected_metric}
              </label>
              <input
                className="w-full bg-[#0C0F11] border border-white/10 rounded-lg p-2 text-xs text-text-primary focus:border-brand-bright focus:outline-none"
                type="number"
                min="0"
                step="any"
                value={experimentTargetValue}
                onChange={(event) => setExperimentTargetValue(event.target.value)}
                required
              />
              <p className="mt-1.5 text-[11px] text-text-muted">
                The proposal&apos;s change and metric will be registered as an approval-first experiment.
              </p>
            </div>
          ) : (
            <p className="text-text-secondary leading-relaxed">
              Approving records your decision. It does not change your store by itself; eligible changes are reviewed and run separately.
            </p>
          )}
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={closeReviewDialog}>
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

      {/* Rollback Confirmation Dialog */}
      <Dialog
        isOpen={selectedRollbackAction !== null}
        onClose={closeRollbackDialog}
        title="Confirm Deterministic Rollback"
        description={`Roll back autonomous action "${selectedRollbackAction?.action_type}" on ${selectedRollbackAction?.target_entity_type}?`}
      >
        <div className="space-y-3 py-2 text-xs">
          <p className="text-text-secondary">
            This will revert the target resource to its pre-mutation snapshot version (v
            {selectedRollbackAction?.target_version_before}). If newer human changes were made, rollback will fail closed safely.
          </p>
          <div>
            <label className="block text-[11px] font-mono text-text-muted uppercase mb-1">
              Rollback Reason
            </label>
            <input
              className="w-full bg-[#0C0F11] border border-white/10 rounded-lg p-2 text-xs text-text-primary focus:border-brand-bright focus:outline-none"
              value={rollbackReason}
              onChange={(e) => setRollbackReason(e.target.value)}
              placeholder="e.g. Conversion drop or manual store preference"
              required
            />
          </div>
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={closeRollbackDialog}>
            Cancel
          </Button>
          <Button
            size="sm"
            isLoading={isRollingBack}
            onClick={handleConfirmRollback}
            className="bg-amber-500 text-slate-950 hover:bg-amber-400"
          >
            Execute Rollback
          </Button>
        </DialogFooter>
      </Dialog>

      {/* Pre-Mutation Snapshot Dialog */}
      <Dialog
        isOpen={selectedSnapshot !== null}
        onClose={() => setSelectedSnapshot(null)}
        title="Pre-Mutation Rollback Snapshot"
        description="Immutable snapshot captured prior to autonomous execution."
      >
        <div className="py-2 text-xs">
          <pre className="p-3 bg-[#0C0F11] border border-white/10 rounded-xl overflow-x-auto text-[11px] font-mono text-brand-bright max-h-80">
            {JSON.stringify(selectedSnapshot, null, 2)}
          </pre>
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={() => setSelectedSnapshot(null)}>
            Close
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};
