import React, { useCallback, useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Card } from '@/components/ui/card';
import { Dialog, DialogFooter } from '@/components/ui/dialog';
import { Skeleton } from '@/components/ui/skeleton';
import { EmptyState } from '@/components/ui/empty-state';
import { Input } from '@/components/ui/input';
import { api } from '@/lib/api-client';
import { MerchantExperimentItem, ExperimentCreatePayload } from '@/types/portal';
import { formatRelativeTime } from '@/lib/utils';
import {
  FlaskConical,
  CheckCircle2,
  AlertCircle,
  RefreshCw,
  Plus,
  ShieldCheck,
  Sliders,
  RotateCcw,
  StopCircle,
} from 'lucide-react';

export const ExperimentsPage: React.FC = () => {
  const [experiments, setExperiments] = useState<MerchantExperimentItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  // New experiment modal state
  const [showCreateModal, setShowCreateModal] = useState<boolean>(false);
  const [newExpTitle, setNewExpTitle] = useState<string>('');
  const [newExpHypothesis, setNewExpHypothesis] = useState<string>('');
  const [newExpMetric, setNewExpMetric] = useState<string>('quote_conversion_rate');
  const [newExpBaseline, setNewExpBaseline] = useState<string>('12.5');
  const [newExpTarget, setNewExpTarget] = useState<string>('18.0');
  const [newExpVariation, setNewExpVariation] = useState<string>('');
  const [isCreating, setIsCreating] = useState<boolean>(false);

  // Action loading states
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  const closeCreateModal = useCallback(() => {
    setShowCreateModal(false);
  }, []);

  const fetchExperiments = async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const data = await api.listExperiments();
      setExperiments(data);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to fetch experiments.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchExperiments();
  }, []);

  const handleCreateExperiment = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newExpTitle || !newExpHypothesis) return;
    setIsCreating(true);
    setErrorMessage(null);
    try {
      const payload: ExperimentCreatePayload = {
        title: newExpTitle,
        hypothesis: newExpHypothesis,
        target_metric: newExpMetric,
        baseline_value: parseFloat(newExpBaseline) || 0.0,
        target_value: parseFloat(newExpTarget) || 0.0,
        proposed_variation: { description: newExpVariation },
      };
      await api.createExperiment(payload);
      closeCreateModal();
      setNewExpTitle('');
      setNewExpHypothesis('');
      setNewExpVariation('');
      setSuccessMessage('Experiment registered in approval-first state.');
      await fetchExperiments();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to create experiment.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleApprove = async (id: string) => {
    setActionLoadingId(id);
    setErrorMessage(null);
    try {
      await api.approveExperiment(id);
      setSuccessMessage('Experiment approved and ready.');
      await fetchExperiments();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to approve experiment.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleEvaluate = async (id: string) => {
    setActionLoadingId(id);
    setErrorMessage(null);
    try {
      const result = await api.evaluateExperiment(id);
      setSuccessMessage(`Measurement completed: Recommendation is ${result.recommendation} (${result.percentage_change > 0 ? '+' : ''}${result.percentage_change}%).`);
      await fetchExperiments();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to evaluate experiment.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleStop = async (id: string) => {
    setActionLoadingId(id);
    setErrorMessage(null);
    try {
      await api.stopExperiment(id, 'Merchant requested stop');
      setSuccessMessage('Experiment stopped successfully.');
      await fetchExperiments();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to stop experiment.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const handleRollback = async (id: string) => {
    setActionLoadingId(id);
    setErrorMessage(null);
    try {
      await api.rollbackExperiment(id, 'Merchant requested rollback');
      setSuccessMessage('Experiment rolled back to baseline.');
      await fetchExperiments();
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to roll back experiment.');
    } finally {
      setActionLoadingId(null);
    }
  };

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'APPROVED':
        return <Badge variant="success" className="text-[10px] font-mono">APPROVED</Badge>;
      case 'COMPLETED':
        return <Badge variant="default" className="text-[10px] font-mono bg-emerald-500/20 text-emerald-300 border-emerald-500/30">COMPLETED</Badge>;
      case 'APPROVAL_REQUIRED':
        return <Badge variant="warning" className="text-[10px] font-mono">APPROVAL REQUIRED</Badge>;
      case 'STOPPED':
      case 'ROLLED_BACK':
        return <Badge variant="destructive" className="text-[10px] font-mono">{status}</Badge>;
      default:
        return <Badge variant="outline" className="text-[10px] font-mono">{status}</Badge>;
    }
  };

  const getRecommendationBadge = (rec: string) => {
    switch (rec) {
      case 'KEEP':
        return <Badge variant="success" className="text-[11px] font-mono">KEEP (WINNING VARIATION)</Badge>;
      case 'ROLLBACK':
        return <Badge variant="destructive" className="text-[11px] font-mono">ROLLBACK (DEGRADED METRIC)</Badge>;
      default:
        return <Badge variant="warning" className="text-[11px] font-mono">INCONCLUSIVE (CONTINUE SAMPLING)</Badge>;
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 bg-[#1B1C1E] p-5 rounded-2xl border border-white/10 shadow-lg">
        <div className="flex items-start gap-3.5">
          <div className="h-10 w-10 rounded-xl bg-brand-bright/10 border border-brand-bright/30 flex items-center justify-center shrink-0">
            <FlaskConical className="h-5 w-5 text-brand-bright" />
          </div>
          <div>
            <div className="flex items-center gap-2.5">
              <h2 className="text-xl font-bold tracking-tight text-text-primary">Optimization Experiments</h2>
              <Badge variant="outline" className="text-[10px] font-mono border-brand-bright/40 text-brand-bright">
                Approval-First Framework
              </Badge>
            </div>
            <p className="text-xs text-text-muted mt-1 max-w-xl">
              Controlled experiment definitions and deterministic measurement. Formulate hypotheses, approve variations, and compute authoritative outcomes.
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2.5">
          <Button
            variant="outline"
            size="sm"
            onClick={fetchExperiments}
            isLoading={isLoading}
            className="text-xs border-white/10 bg-[#0C0F11] hover:bg-[#202426]"
          >
            <RefreshCw className="h-3.5 w-3.5 mr-1.5" /> Refresh
          </Button>
          <Button
            size="sm"
            onClick={() => setShowCreateModal(true)}
            className="text-xs font-semibold bg-brand-bright text-[#070B14] hover:bg-brand-bright/90 shadow-md shadow-brand-bright/10"
          >
            <Plus className="h-3.5 w-3.5 mr-1.5" /> New Experiment
          </Button>
        </div>
      </div>

      {/* Safety Principle */}
      <div className="flex items-center justify-between px-4 py-2.5 bg-[#171A1C] rounded-xl border border-emerald-500/20 text-xs">
        <div className="flex items-center gap-2 text-emerald-400">
          <ShieldCheck className="h-4 w-4 shrink-0" />
          <span><strong>Measurement Invariant:</strong> Outcomes are calculated deterministically from authoritative telemetry. The model cannot hallucinate or fabricate experiment results.</span>
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

      {/* Experiments Listing */}
      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-36 w-full rounded-xl bg-[#202426]" />
          ))}
        </div>
      ) : experiments.length === 0 ? (
        <EmptyState
          icon={<FlaskConical className="h-10 w-10 text-brand-bright" />}
          title="No experiments registered"
          description="Create a new experiment or convert an agent proposal into a structured test."
        />
      ) : (
        <div className="space-y-4">
          {experiments.map((exp) => {
            const hasResult = exp.results && exp.results.length > 0;
            const latestResult = hasResult ? exp.results[exp.results.length - 1] : null;
            const isPendingApproval = exp.approval_status === 'PENDING';

            return (
              <Card key={exp.id} className="bg-[#1B1C1E] border-white/10 p-5 rounded-2xl hover:border-brand-bright/40 transition-all">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 mb-3">
                  <div className="flex items-center gap-2.5">
                    <span className="font-mono text-xs text-brand-bright font-bold">
                      EXP-{exp.id.slice(0, 8)}
                    </span>
                    {getStatusBadge(exp.status)}
                    {exp.risk_level === 'AUTO_LOW_RISK' || exp.risk_level === 'LOW_RISK_REVERSIBLE' ? (
                      <Badge variant="outline" className="text-[10px] font-mono border-brand-bright/40 text-brand-bright">
                        AUTO_ELIGIBLE
                      </Badge>
                    ) : (
                      <Badge variant="outline" className="text-[10px] font-mono border-white/10 text-text-muted">
                        APPROVAL_REQUIRED
                      </Badge>
                    )}
                    <Badge variant="outline" className="text-[10px] font-mono">
                      Risk: {exp.risk_level}
                    </Badge>
                  </div>
                  <span className="text-[11px] font-mono text-text-muted">
                    {formatRelativeTime(exp.created_at)}
                  </span>
                </div>

                <h4 className="text-base font-bold text-text-primary mb-1.5">{exp.title}</h4>
                <p className="text-xs text-text-secondary mb-3 leading-relaxed">{exp.hypothesis}</p>

                {/* Target Metric Box */}
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 bg-[#0C0F11] p-3.5 rounded-xl border border-white/10 mb-3 text-xs">
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase block">Target Metric</span>
                    <span className="font-bold text-text-primary font-mono text-xs mt-0.5 block">{exp.target_metric}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase block">Baseline Value</span>
                    <span className="font-bold text-text-primary font-mono text-xs mt-0.5 block">{exp.baseline_value}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase block">Target Goal</span>
                    <span className="font-bold text-brand-bright font-mono text-xs mt-0.5 block">{exp.target_value}</span>
                  </div>
                  <div>
                    <span className="text-[10px] font-mono text-text-muted uppercase block">Approval Status</span>
                    <span className="font-bold text-amber-400 font-mono text-xs mt-0.5 block">{exp.approval_status}</span>
                  </div>
                </div>

                {/* Measurement Result (if evaluated) */}
                {latestResult && (
                  <div className="bg-[#0C0F11] border border-emerald-500/30 p-4 rounded-xl mb-3 space-y-2 text-xs">
                    <div className="flex items-center justify-between">
                      <span className="font-mono text-xs font-bold text-emerald-400">Authoritative Measurement Result</span>
                      {getRecommendationBadge(latestResult.recommendation)}
                    </div>
                    <div className="grid grid-cols-2 sm:grid-cols-4 gap-3 pt-2 text-[11px] font-mono">
                      <div>
                        <span className="text-text-muted block uppercase text-[9px]">Sample Size</span>
                        <span className="font-bold text-text-primary">{latestResult.sample_size} events</span>
                      </div>
                      <div>
                        <span className="text-text-muted block uppercase text-[9px]">Post-Experiment</span>
                        <span className="font-bold text-text-primary">{latestResult.post_experiment_metric}</span>
                      </div>
                      <div>
                        <span className="text-text-muted block uppercase text-[9px]">Percentage Delta</span>
                        <span className={`font-bold ${latestResult.percentage_change >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                          {latestResult.percentage_change > 0 ? '+' : ''}{latestResult.percentage_change}%
                        </span>
                      </div>
                      <div>
                        <span className="text-text-muted block uppercase text-[9px]">Confidence</span>
                        <span className="font-bold text-brand-bright">{Math.round(latestResult.confidence_score * 100)}%</span>
                      </div>
                    </div>
                    {latestResult.limitations.length > 0 && (
                      <p className="text-[11px] text-amber-300/80 pt-1">
                        Limitations: {latestResult.limitations.join(' ')}
                      </p>
                    )}
                  </div>
                )}

                {/* Action Footer */}
                <div className="flex flex-wrap justify-end gap-2.5 pt-3 border-t border-white/10">
                  {isPendingApproval && (
                    <Button
                      size="sm"
                      isLoading={actionLoadingId === exp.id}
                      onClick={() => handleApprove(exp.id)}
                      className="text-xs font-semibold bg-emerald-500 text-slate-950 hover:bg-emerald-400"
                    >
                      <CheckCircle2 className="h-3.5 w-3.5 mr-1" /> Approve Experiment
                    </Button>
                  )}
                  {(exp.status === 'RUNNING' || exp.status === 'APPROVED') && (
                    <>
                      <Button
                        variant="outline"
                        size="sm"
                        isLoading={actionLoadingId === exp.id}
                        onClick={() => handleStop(exp.id)}
                        className="text-xs text-rose-400 border-rose-500/30 hover:bg-rose-500/10"
                      >
                        <StopCircle className="h-3.5 w-3.5 mr-1" /> Stop Experiment
                      </Button>
                      <Button
                        variant="outline"
                        size="sm"
                        isLoading={actionLoadingId === exp.id}
                        onClick={() => handleRollback(exp.id)}
                        className="text-xs text-amber-400 border-amber-500/30 hover:bg-amber-500/10"
                      >
                        <RotateCcw className="h-3.5 w-3.5 mr-1" /> Rollback
                      </Button>
                    </>
                  )}
                  {exp.status === 'APPROVED' && (
                    <Button
                      variant="outline"
                      size="sm"
                      isLoading={actionLoadingId === exp.id}
                      onClick={() => handleEvaluate(exp.id)}
                      className="text-xs border-brand-bright/40 text-brand-bright hover:bg-brand-bright/10"
                    >
                      <Sliders className="h-3.5 w-3.5 mr-1" /> Evaluate Results
                    </Button>
                  )}
                </div>
              </Card>
            );
          })}
        </div>
      )}

      {/* Create Experiment Modal */}
      <Dialog
        isOpen={showCreateModal}
        onClose={closeCreateModal}
        title="Register Optimization Experiment"
        description="Define an approval-first experiment with clear metric targets."
      >
        <form onSubmit={handleCreateExperiment} className="space-y-4 py-2 text-xs">
          <Input
            label="Experiment Title"
            placeholder="e.g. Earlier Delivery ETA Visibility"
            value={newExpTitle}
            onChange={(e) => setNewExpTitle(e.target.value)}
            required
          />
          <div>
            <label className="block text-[11px] font-mono text-text-muted uppercase mb-1">
              Hypothesis & Expected Mechanism
            </label>
            <textarea
              className="w-full h-20 bg-[#0C0F11] border border-white/10 rounded-lg p-2 text-xs text-text-primary focus:border-brand-bright focus:outline-none"
              placeholder="Explain what change will be made and why it improves conversion..."
              value={newExpHypothesis}
              onChange={(e) => setNewExpHypothesis(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-[11px] font-mono text-text-muted uppercase mb-1">
              Proposed Variation
            </label>
            <textarea
              className="w-full h-16 bg-[#0C0F11] border border-white/10 rounded-lg p-2 text-xs text-text-primary focus:border-brand-bright focus:outline-none"
              placeholder="Describe the exact merchant-controlled change being measured..."
              value={newExpVariation}
              onChange={(e) => setNewExpVariation(e.target.value)}
              required
            />
          </div>
          <div className="grid grid-cols-3 gap-3">
            <Input
              label="Target Metric"
              value={newExpMetric}
              onChange={(e) => setNewExpMetric(e.target.value)}
              required
            />
            <Input
              label="Baseline"
              type="number"
              step="0.1"
              value={newExpBaseline}
              onChange={(e) => setNewExpBaseline(e.target.value)}
              required
            />
            <Input
              label="Target Goal"
              type="number"
              step="0.1"
              value={newExpTarget}
              onChange={(e) => setNewExpTarget(e.target.value)}
              required
            />
          </div>
          <DialogFooter>
            <Button type="button" variant="outline" size="sm" onClick={closeCreateModal}>
              Cancel
            </Button>
            <Button type="submit" size="sm" isLoading={isCreating} className="bg-brand-bright text-[#070B14] hover:bg-brand-bright/90">
              Register Experiment
            </Button>
          </DialogFooter>
        </form>
      </Dialog>
    </div>
  );
};
