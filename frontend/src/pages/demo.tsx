import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogFooter } from '@/components/ui/dialog';
import { api } from '@/lib/api-client';
import { DemoSimulationStepRequest, DemoSimulationStepResponse, SimulationTraceStep } from '@/types/portal';
import { formatPaiseToINR } from '@/lib/utils';
import {
  Play,
  RotateCcw,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Bot,
  Scale,
  CreditCard,
  Hash,
  Terminal,
  Lock,
} from 'lucide-react';

export const DemoPage: React.FC = () => {
  const [selectedScenario, setSelectedScenario] = useState<
    'STANDARD_AUTO_COMMERCE' | 'HITL_ESCALATION_COMMERCE' | 'PAYMENT_RECONCILIATION'
  >('STANDARD_AUTO_COMMERCE');
  const [selectedSku, setSelectedSku] = useState<string>('RUN-PRO-01');
  const [quantity, setQuantity] = useState<number>(1);
  const [customDiscount, setCustomDiscount] = useState<string>('10');
  const [isRunning, setIsRunning] = useState<boolean>(false);
  const [simulationResult, setSimulationResult] = useState<DemoSimulationStepResponse | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [showResetModal, setShowResetModal] = useState<boolean>(false);
  const [isResetting, setIsResetting] = useState<boolean>(false);
  const [resetSuccess, setResetSuccess] = useState<string | null>(null);

  const handleRunSimulation = async () => {
    setIsRunning(true);
    setErrorMessage(null);
    setSimulationResult(null);

    const parsedDiscount = Number.parseFloat(customDiscount);
    const payload: DemoSimulationStepRequest = {
      scenario: selectedScenario,
      sku: selectedSku,
      quantity,
      target_discount_pct: selectedScenario === 'HITL_ESCALATION_COMMERCE' ? 20 : Number.isFinite(parsedDiscount) ? parsedDiscount : 10,
    };

    try {
      const res = await api.simulateDemo(payload);
      setSimulationResult(res);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Simulation failed');
    } finally {
      setIsRunning(false);
    }
  };

  const handleResetDemoState = async () => {
    setIsResetting(true);
    setErrorMessage(null);
    setResetSuccess(null);
    try {
      const res = await api.seedDemoState();
      setResetSuccess(res.message);
      setShowResetModal(false);
    } catch (err: unknown) {
      setErrorMessage(err instanceof Error ? err.message : 'Failed to reset demo state');
    } finally {
      setIsResetting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Top Banner */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-[#24314A]/70 pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight text-text-primary">
              Interactive Simulation Sandbox
            </h2>
            <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-brand/20 text-brand-bright border border-brand/30">
              Deterministic Sandbox
            </span>
          </div>
          <p className="text-xs text-text-secondary mt-0.5">
            Demonstrate and verify server-authoritative autonomous commerce pipelines against live PostgreSQL persistence.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowResetModal(true)}
            disabled={isResetting || isRunning}
            className="text-xs gap-1.5 bg-[#0D1424] border-[#24314A] text-text-secondary hover:text-text-primary"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Reset Demo Data
          </Button>
        </div>
      </div>

      {resetSuccess && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 rounded-xl text-xs flex items-center justify-between shadow-glow-success">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-4 w-4" />
            <span>{resetSuccess}</span>
          </div>
          <button onClick={() => setResetSuccess(null)} className="text-emerald-400 font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-3 bg-rose-500/10 border border-rose-500/30 text-rose-300 rounded-xl text-xs flex items-center justify-between">
          <div className="flex items-center gap-2">
            <AlertTriangle className="h-4 w-4" />
            <span>{errorMessage}</span>
          </div>
          <button onClick={() => setErrorMessage(null)} className="text-rose-300 font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Scenario Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Scenario 1 */}
        <div
          onClick={() => setSelectedScenario('STANDARD_AUTO_COMMERCE')}
          className={`glass-panel p-5 rounded-xl cursor-pointer transition-all border-2 ${
            selectedScenario === 'STANDARD_AUTO_COMMERCE'
              ? 'border-brand bg-[#141D31] shadow-glow'
              : 'border-[#24314A] bg-[#0D1424]/80 hover:border-brand/40'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-brand/15 text-brand-bright">
                <Bot className="h-4 w-4" />
              </div>
              <span className="font-bold text-xs text-text-primary">Standard Auto Commerce</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
              ALLOW
            </span>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed mb-3">
            Buyer agent proposes 10% discount. Policy engine evaluates <strong className="text-text-primary">ALLOW</strong>, generates order, and captures Razorpay payment automatically.
          </p>
          <div className="text-[10px] font-mono bg-[#070B14] p-2.5 rounded-lg border border-[#24314A] text-text-muted">
            Flow: Discovery → Quote (10% off) → Policy Approved → Order → Razorpay Webhook → Settled
          </div>
        </div>

        {/* Scenario 2 */}
        <div
          onClick={() => setSelectedScenario('HITL_ESCALATION_COMMERCE')}
          className={`glass-panel p-5 rounded-xl cursor-pointer transition-all border-2 ${
            selectedScenario === 'HITL_ESCALATION_COMMERCE'
              ? 'border-amber-500 bg-[#141D31] shadow-glow-warning'
              : 'border-[#24314A] bg-[#0D1424]/80 hover:border-amber-500/40'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-amber-500/15 text-amber-400">
                <Scale className="h-4 w-4" />
              </div>
              <span className="font-bold text-xs text-text-primary">HITL Human Approval</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-amber-500/10 text-amber-400 border border-amber-500/20">
              ESCALATE
            </span>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed mb-3">
            Buyer agent requests aggressive 20% discount (exceeds 15% limit). Policy engine emits <strong className="text-text-primary">ESCALATE_APPROVAL</strong> and queues a ticket in Approvals.
          </p>
          <div className="text-[10px] font-mono bg-[#070B14] p-2.5 rounded-lg border border-[#24314A] text-text-muted">
            Flow: Discovery → Quote (20% off) → Escalated → Pending Ticket → Merchant Approves/Rejects
          </div>
        </div>

        {/* Scenario 3 */}
        <div
          onClick={() => setSelectedScenario('PAYMENT_RECONCILIATION')}
          className={`glass-panel p-5 rounded-xl cursor-pointer transition-all border-2 ${
            selectedScenario === 'PAYMENT_RECONCILIATION'
              ? 'border-emerald-500 bg-[#141D31] shadow-glow-success'
              : 'border-[#24314A] bg-[#0D1424]/80 hover:border-emerald-500/40'
          }`}
        >
          <div className="flex items-center justify-between mb-3">
            <div className="flex items-center gap-2">
              <div className="p-2 rounded-lg bg-emerald-500/15 text-emerald-400">
                <CreditCard className="h-4 w-4" />
              </div>
              <span className="font-bold text-xs text-text-primary">Payment Reconciliation</span>
            </div>
            <span className="text-[10px] font-mono px-2 py-0.5 rounded bg-blue-500/10 text-blue-400 border border-blue-500/20">
              RECOVER
            </span>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed mb-3">
            Simulates a dropped webhook scenario. Store operator triggers out-of-band server reconciliation directly against Razorpay API to settle the order.
          </p>
          <div className="text-[10px] font-mono bg-[#070B14] p-2.5 rounded-lg border border-[#24314A] text-text-muted">
            Flow: Order Pending → Dropped Webhook → Manual Reconcile Trigger → Razorpay Query → Settled
          </div>
        </div>
      </div>

      {/* Parameter Configuration & Run Controls */}
      <div className="glass-panel rounded-2xl p-6 border border-[#24314A] bg-[#0D1424]">
        <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#24314A]/60">
          <div className="flex items-center gap-2">
            <Terminal className="h-4 w-4 text-brand-bright" />
            <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-text-primary">
              Simulation Parameters & Engine Control
            </h3>
          </div>
          <span className="text-[11px] font-mono text-text-muted">Server-Authoritative Test Runtime</span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-5">
          <div>
            <label className="text-xs font-mono text-text-muted block mb-1.5 uppercase">Target Product SKU</label>
            <select
              value={selectedSku}
              onChange={(e) => setSelectedSku(e.target.value)}
              className="w-full bg-[#070B14] border border-[#24314A] rounded-xl p-2.5 text-xs text-text-primary focus:outline-none focus:border-brand"
            >
              <option value="RUN-PRO-01">RUN-PRO-01: Apex Carbon Pro (₹12,999)</option>
              <option value="AIR-VEST-02">AIR-VEST-02: AeroFlow Running Vest (₹4,499)</option>
              <option value="PACE-BAND-03">PACE-BAND-03: TempoPulse GPS Sensor (₹7,999)</option>
            </select>
          </div>

          <div>
            <label className="text-xs font-mono text-text-muted block mb-1.5 uppercase">Order Quantity</label>
            <input
              type="number"
              min={1}
              max={10}
              value={quantity}
              onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
              className="w-full bg-[#070B14] border border-[#24314A] rounded-xl p-2.5 text-xs text-text-primary focus:outline-none focus:border-brand"
            />
          </div>

          <div>
            <label className="text-xs font-mono text-text-muted block mb-1.5 uppercase">
              Target Discount Rate (%)
            </label>
            <input
              type="number"
              min={0}
              max={50}
              disabled={selectedScenario === 'HITL_ESCALATION_COMMERCE'}
              value={selectedScenario === 'HITL_ESCALATION_COMMERCE' ? '20' : customDiscount}
              onChange={(e) => setCustomDiscount(e.target.value)}
              className="w-full bg-[#070B14] border border-[#24314A] rounded-xl p-2.5 text-xs text-text-primary focus:outline-none focus:border-brand disabled:opacity-50"
            />
          </div>
        </div>

        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pt-3 border-t border-[#24314A]/60">
          <div className="flex items-center gap-2 text-xs text-text-secondary">
            <Lock className="h-4 w-4 text-emerald-400 shrink-0" />
            <span>Executes authentic backend state machines, HMAC webhooks, and SHA-256 audit chaining.</span>
          </div>

          <Button
            onClick={handleRunSimulation}
            disabled={isRunning}
            className="bg-brand hover:bg-brand-deep text-white font-semibold text-xs px-6 shadow-glow"
          >
            {isRunning ? (
              <span className="flex items-center gap-2">
                <span className="h-3.5 w-3.5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Executing Pipeline...
              </span>
            ) : (
              <span className="flex items-center gap-2">
                <Play className="h-3.5 w-3.5 fill-current" /> Run Simulation Scenario
              </span>
            )}
          </Button>
        </div>
      </div>

      {/* Execution Results & Live Trace */}
      {simulationResult && (
        <div className="space-y-4">
          {/* Summary Banner */}
          <div
            className={`glass-panel p-5 rounded-2xl border text-xs flex flex-col md:flex-row md:items-center justify-between gap-4 ${
              simulationResult.status === 'SETTLED'
                ? 'border-emerald-500/40 bg-emerald-500/5 shadow-glow-success'
                : 'border-amber-500/40 bg-amber-500/5 shadow-glow-warning'
            }`}
          >
            <div className="space-y-1.5">
              <div className="flex items-center gap-2">
                {simulationResult.status === 'SETTLED' ? (
                  <CheckCircle2 className="h-5 w-5 text-emerald-400" />
                ) : (
                  <AlertTriangle className="h-5 w-5 text-amber-400" />
                )}
                <span className="font-bold text-sm text-text-primary">{simulationResult.message}</span>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-text-secondary text-xs">
                <span>Scenario: <strong className="text-text-primary">{simulationResult.scenario}</strong></span>
                <span>•</span>
                <span>Subtotal: <strong className="text-text-primary">{formatPaiseToINR(simulationResult.subtotal_paise)}</strong></span>
                <span>•</span>
                <span>Discount: <strong className="text-amber-400">-{formatPaiseToINR(simulationResult.discount_paise)}</strong></span>
                <span>•</span>
                <span>Settled Total: <strong className="text-emerald-400 font-bold">{formatPaiseToINR(simulationResult.total_paise)}</strong></span>
              </div>
            </div>

            <div className="flex flex-wrap items-center gap-2">
              {simulationResult.approval_id && (
                <a
                  href="/approvals"
                  className="px-3.5 py-2 bg-amber-500 text-[#070B14] rounded-xl text-xs font-bold hover:bg-amber-400 transition flex items-center gap-1.5"
                >
                  Resolve in Queue <ExternalLink className="h-3 w-3" />
                </a>
              )}
              {simulationResult.order_id && (
                <a
                  href="/orders"
                  className="px-3.5 py-2 bg-brand text-white rounded-xl text-xs font-semibold hover:bg-brand-deep transition flex items-center gap-1.5"
                >
                  View Order Ledger <ExternalLink className="h-3 w-3" />
                </a>
              )}
              <a
                href="/audit"
                className="px-3.5 py-2 bg-[#141D31] text-text-primary border border-[#24314A] rounded-xl text-xs font-medium hover:bg-[#1E293B] transition flex items-center gap-1.5"
              >
                Audit Evidence <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>

          {/* Trace Steps Timeline */}
          <div className="glass-panel rounded-2xl p-6 border border-[#24314A] bg-[#0D1424]">
            <div className="flex items-center justify-between mb-4 pb-3 border-b border-[#24314A]/60">
              <div className="flex items-center gap-2">
                <Hash className="h-4 w-4 text-brand-bright" />
                <h3 className="text-xs font-mono font-bold uppercase tracking-wider text-text-primary">
                  Deterministic Execution Trace ({simulationResult.steps.length} Steps)
                </h3>
              </div>
              <span className="font-mono text-[11px] text-text-muted">
                Policy Hash: {simulationResult.policy_hash.slice(0, 16)}...
              </span>
            </div>

            <div className="space-y-4">
              {simulationResult.steps.map((step: SimulationTraceStep) => (
                <div
                  key={step.step_number}
                  className="flex items-start gap-3 relative pb-2 border-l-2 border-[#24314A] pl-4 ml-2 last:border-transparent"
                >
                  <div className="absolute -left-[9px] top-0.5 h-4 w-4 rounded-full bg-[#070B14] border-2 border-brand flex items-center justify-center text-[9px] font-bold text-brand-bright">
                    {step.step_number}
                  </div>
                  <div className="w-full bg-[#070B14]/80 border border-[#24314A] rounded-xl p-3.5 text-xs space-y-2">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <span className="font-bold text-text-primary">{step.actor}</span>
                        <span className="font-mono text-[10px] text-brand-bright">[{step.action}]</span>
                      </div>
                      <Badge
                        variant={
                          step.status === 'SETTLED' || step.status === 'SUCCESS'
                            ? 'success'
                            : step.status === 'ESCALATED'
                            ? 'warning'
                            : 'secondary'
                        }
                        className="text-[9px] font-mono"
                      >
                        {step.status}
                      </Badge>
                    </div>
                    <p className="text-text-secondary text-xs">{step.summary}</p>
                    {step.details && Object.keys(step.details).length > 0 && (
                      <pre className="text-[11px] font-mono bg-[#0D1424] p-3 rounded-lg border border-[#24314A] text-text-secondary overflow-x-auto">
                        {JSON.stringify(step.details, null, 2)}
                      </pre>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Confirmation Dialog for Resetting Demo State */}
      <Dialog
        isOpen={showResetModal}
        onClose={() => setShowResetModal(false)}
        title="Reset & Re-seed Demo Sandbox Data?"
        description="This will re-initialize standard test products and restore default policy limits for evaluation."
      >
        <div className="text-xs text-text-secondary space-y-2 py-2">
          <p>
            Standard products (<strong className="text-text-primary">RUN-PRO-01</strong>, <strong className="text-text-primary">AIR-VEST-02</strong>, <strong className="text-text-primary">PACE-BAND-03</strong>) and default autonomy bounds (15% max discount, 20% min margin) will be verified and ensured on PostgreSQL.
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={() => setShowResetModal(false)} className="text-xs">
            Cancel
          </Button>
          <Button
            size="sm"
            onClick={handleResetDemoState}
            disabled={isResetting}
            className="text-xs bg-brand hover:bg-brand-deep text-white"
          >
            {isResetting ? 'Resetting...' : 'Confirm Reset'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};

