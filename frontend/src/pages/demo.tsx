import React, { useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog, DialogFooter } from '@/components/ui/dialog';
import { api } from '@/lib/api-client';
import { DemoSimulationStepRequest, DemoSimulationStepResponse, SimulationTraceStep } from '@/types/portal';
import { formatPaiseToINR } from '@/lib/utils';
import {
  Sparkles,
  Play,
  RotateCcw,
  ShieldCheck,
  CheckCircle2,
  AlertTriangle,
  ExternalLink,
  Bot,
  Scale,
  CreditCard,
  Hash,
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

    const payload: DemoSimulationStepRequest = {
      scenario: selectedScenario,
      sku: selectedSku,
      quantity,
      target_discount_pct: selectedScenario === 'HITL_ESCALATION_COMMERCE' ? 20 : parseFloat(customDiscount) || 10,
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
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-border pb-4">
        <div>
          <div className="flex items-center gap-2">
            <h2 className="text-xl font-bold tracking-tight">Interactive Simulation Sandbox</h2>
            <Badge variant="default" className="text-[10px] gap-1">
              <Sparkles className="h-3 w-3" /> Phase 5.3 Verified
            </Badge>
          </div>
          <p className="text-xs text-muted-foreground mt-0.5">
            Demonstrate and verify the complete server-authoritative commerce flow using deterministic test-mode data.
          </p>
        </div>
        <div className="flex items-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => setShowResetModal(true)}
            disabled={isResetting || isRunning}
            className="text-xs gap-1"
          >
            <RotateCcw className="h-3.5 w-3.5" /> Reset Demo Data
          </Button>
        </div>
      </div>

      {resetSuccess && (
        <div className="p-3 bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 rounded text-xs flex items-center justify-between">
          <span>{resetSuccess}</span>
          <button onClick={() => setResetSuccess(null)} className="text-emerald-400 font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {errorMessage && (
        <div className="p-3 bg-destructive/10 border border-destructive/20 text-destructive rounded text-xs flex items-center justify-between">
          <span>{errorMessage}</span>
          <button onClick={() => setErrorMessage(null)} className="text-destructive font-bold hover:underline">
            Dismiss
          </button>
        </div>
      )}

      {/* Scenario Selection Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {/* Scenario 1 */}
        <Card
          onClick={() => setSelectedScenario('STANDARD_AUTO_COMMERCE')}
          className={`cursor-pointer transition border-2 ${
            selectedScenario === 'STANDARD_AUTO_COMMERCE'
              ? 'border-primary bg-primary/5 shadow-md shadow-primary/10'
              : 'border-border bg-card/60 hover:border-border/80'
          }`}
        >
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Bot className="h-4 w-4 text-primary" />
                <span className="font-semibold text-xs">Standard Auto Commerce</span>
              </div>
              <Badge variant="success" className="text-[9px]">Autonomy Level 1</Badge>
            </div>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground space-y-2">
            <p>
              External buyer agent proposes a 10% discount. Policy engine evaluates <strong className="text-foreground">ALLOW</strong>, generates order, and captures Razorpay payment automatically.
            </p>
            <div className="text-[10px] bg-muted/40 p-2 rounded border border-border">
              Flow: Discovery → Quote (10% off) → Policy Approved → Order → Razorpay Webhook → Settled
            </div>
          </CardContent>
        </Card>

        {/* Scenario 2 */}
        <Card
          onClick={() => setSelectedScenario('HITL_ESCALATION_COMMERCE')}
          className={`cursor-pointer transition border-2 ${
            selectedScenario === 'HITL_ESCALATION_COMMERCE'
              ? 'border-amber-500 bg-amber-500/5 shadow-md shadow-amber-500/10'
              : 'border-border bg-card/60 hover:border-border/80'
          }`}
        >
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Scale className="h-4 w-4 text-amber-400" />
                <span className="font-semibold text-xs">HITL Human Approval</span>
              </div>
              <Badge variant="warning" className="text-[9px]">Autonomy Escalation</Badge>
            </div>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground space-y-2">
            <p>
              Buyer agent requests an aggressive 20% discount (exceeds 15% limit). Policy engine emits <strong className="text-foreground">ESCALATE_APPROVAL</strong> and queues a ticket in Approvals.
            </p>
            <div className="text-[10px] bg-muted/40 p-2 rounded border border-border">
              Flow: Discovery → Quote (20% off) → Escalated → Pending Ticket → Merchant Approves/Rejects
            </div>
          </CardContent>
        </Card>

        {/* Scenario 3 */}
        <Card
          onClick={() => setSelectedScenario('PAYMENT_RECONCILIATION')}
          className={`cursor-pointer transition border-2 ${
            selectedScenario === 'PAYMENT_RECONCILIATION'
              ? 'border-emerald-500 bg-emerald-500/5 shadow-md shadow-emerald-500/10'
              : 'border-border bg-card/60 hover:border-border/80'
          }`}
        >
          <CardHeader className="pb-2">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <CreditCard className="h-4 w-4 text-emerald-400" />
                <span className="font-semibold text-xs">Payment Reconciliation</span>
              </div>
              <Badge variant="secondary" className="text-[9px]">Async Recovery</Badge>
            </div>
          </CardHeader>
          <CardContent className="text-xs text-muted-foreground space-y-2">
            <p>
              Simulates a dropped webhook scenario. Store operator triggers out-of-band server reconciliation directly against Razorpay API to settle the order.
            </p>
            <div className="text-[10px] bg-muted/40 p-2 rounded border border-border">
              Flow: Order Pending → Dropped Webhook → Manual Reconcile Trigger → Razorpay Query → Settled
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Parameter Configuration & Run Panel */}
      <Card className="border-border bg-card/80">
        <CardHeader className="pb-3 border-b border-border">
          <div className="flex items-center justify-between">
            <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
              Simulation Parameters & Launch Controls
            </h3>
            <span className="text-[11px] text-muted-foreground">Server-Authoritative Test Environment</span>
          </div>
        </CardHeader>
        <CardContent className="pt-4 space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Target Product SKU</label>
              <select
                value={selectedSku}
                onChange={(e) => setSelectedSku(e.target.value)}
                className="w-full bg-background border border-border rounded p-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              >
                <option value="RUN-PRO-01">RUN-PRO-01: Apex Carbon Pro (₹12,999)</option>
                <option value="AIR-VEST-02">AIR-VEST-02: AeroFlow Running Vest (₹4,499)</option>
                <option value="PACE-BAND-03">PACE-BAND-03: TempoPulse GPS Sensor (₹7,999)</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">Order Quantity</label>
              <input
                type="number"
                min={1}
                max={10}
                value={quantity}
                onChange={(e) => setQuantity(parseInt(e.target.value) || 1)}
                className="w-full bg-background border border-border rounded p-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary"
              />
            </div>
            <div>
              <label className="text-xs text-muted-foreground block mb-1">
                Requested Discount (%)
              </label>
              <input
                type="number"
                min={0}
                max={50}
                disabled={selectedScenario === 'HITL_ESCALATION_COMMERCE'}
                value={selectedScenario === 'HITL_ESCALATION_COMMERCE' ? '20' : customDiscount}
                onChange={(e) => setCustomDiscount(e.target.value)}
                className="w-full bg-background border border-border rounded p-2 text-xs text-foreground focus:outline-none focus:ring-1 focus:ring-primary disabled:opacity-60"
              />
            </div>
          </div>

          <div className="flex items-center justify-between pt-2">
            <div className="flex items-center gap-2 text-[11px] text-muted-foreground">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              <span>All mutations execute real backend FSMs and append to the immutable cryptographic audit chain.</span>
            </div>
            <Button
              variant="primary"
              size="sm"
              onClick={handleRunSimulation}
              disabled={isRunning}
              className="gap-2 px-6"
            >
              {isRunning ? (
                <>
                  <span className="h-3.5 w-3.5 border-2 border-primary-foreground border-t-transparent rounded-full animate-spin" />
                  Executing Simulation...
                </>
              ) : (
                <>
                  <Play className="h-3.5 w-3.5 fill-current" /> Run Simulation Scenario
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Execution Results & Live Trace */}
      {simulationResult && (
        <div className="space-y-4">
          {/* Summary Banner */}
          <div
            className={`p-4 rounded border text-xs flex flex-col md:flex-row md:items-center justify-between gap-4 ${
              simulationResult.status === 'SETTLED'
                ? 'bg-emerald-500/10 border-emerald-500/30'
                : 'bg-amber-500/10 border-amber-500/30'
            }`}
          >
            <div className="space-y-1">
              <div className="flex items-center gap-2">
                {simulationResult.status === 'SETTLED' ? (
                  <CheckCircle2 className="h-4 w-4 text-emerald-400" />
                ) : (
                  <AlertTriangle className="h-4 w-4 text-amber-400" />
                )}
                <span className="font-bold text-foreground">{simulationResult.message}</span>
              </div>
              <div className="flex flex-wrap items-center gap-3 text-muted-foreground text-[11px]">
                <span>Scenario: <strong className="text-foreground">{simulationResult.scenario}</strong></span>
                <span>•</span>
                <span>Subtotal: <strong className="text-foreground">{formatPaiseToINR(simulationResult.subtotal_paise)}</strong></span>
                <span>•</span>
                <span>Discount: <strong className="text-amber-400">-{formatPaiseToINR(simulationResult.discount_paise)}</strong></span>
                <span>•</span>
                <span>Final Settlement: <strong className="text-emerald-400">{formatPaiseToINR(simulationResult.total_paise)}</strong></span>
              </div>
            </div>

            <div className="flex items-center gap-2">
              {simulationResult.approval_id && (
                <a
                  href="/approvals"
                  className="px-3 py-1.5 bg-amber-500/20 text-amber-300 border border-amber-500/30 rounded text-xs font-semibold hover:bg-amber-500/30 transition flex items-center gap-1"
                >
                  Resolve in Approvals Queue <ExternalLink className="h-3 w-3" />
                </a>
              )}
              {simulationResult.order_id && (
                <a
                  href="/orders"
                  className="px-3 py-1.5 bg-primary/20 text-primary border border-primary/30 rounded text-xs font-semibold hover:bg-primary/30 transition flex items-center gap-1"
                >
                  View Order Ledger <ExternalLink className="h-3 w-3" />
                </a>
              )}
              <a
                href="/audit"
                className="px-3 py-1.5 bg-muted/60 text-muted-foreground border border-border rounded text-xs font-semibold hover:text-foreground transition flex items-center gap-1"
              >
                Inspect Audit Ledger <ExternalLink className="h-3 w-3" />
              </a>
            </div>
          </div>

          {/* Trace Steps Timeline */}
          <Card className="border-border bg-card/80">
            <CardHeader className="pb-3 border-b border-border">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <Hash className="h-4 w-4 text-primary" />
                  <h3 className="text-xs font-bold uppercase tracking-wider text-muted-foreground">
                    Deterministic Execution Trace ({simulationResult.steps.length} Steps)
                  </h3>
                </div>
                <span className="font-mono text-[10px] text-muted-foreground">
                  Policy Fingerprint: {simulationResult.policy_hash.slice(0, 16)}...
                </span>
              </div>
            </CardHeader>
            <CardContent className="pt-4">
              <div className="space-y-4">
                {simulationResult.steps.map((step: SimulationTraceStep) => (
                  <div key={step.step_number} className="flex items-start gap-3 relative pb-2 border-l-2 border-border/60 pl-4 ml-2 last:border-transparent">
                    <div className="absolute -left-[9px] top-0.5 h-4 w-4 rounded-full bg-background border-2 border-primary flex items-center justify-center text-[9px] font-bold text-primary">
                      {step.step_number}
                    </div>
                    <div className="w-full bg-muted/20 border border-border/80 rounded p-3 text-xs space-y-1.5">
                      <div className="flex items-center justify-between">
                        <div className="flex items-center gap-2">
                          <span className="font-semibold text-foreground">{step.actor}</span>
                          <span className="font-mono text-[10px] text-muted-foreground">[{step.action}]</span>
                        </div>
                        <Badge
                          variant={
                            step.status === 'SETTLED' || step.status === 'SUCCESS'
                              ? 'success'
                              : step.status === 'ESCALATED'
                              ? 'warning'
                              : 'secondary'
                          }
                          className="text-[9px]"
                        >
                          {step.status}
                        </Badge>
                      </div>
                      <p className="text-muted-foreground text-[11px]">{step.summary}</p>
                      {step.details && Object.keys(step.details).length > 0 && (
                        <pre className="text-[10px] font-mono bg-background/80 p-2 rounded border border-border text-muted-foreground overflow-x-auto">
                          {JSON.stringify(step.details, null, 2)}
                        </pre>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}

      {/* Confirmation Dialog for Resetting Demo State */}
      <Dialog
        isOpen={showResetModal}
        onClose={() => setShowResetModal(false)}
        title="Reset & Re-seed Demo Sandbox Data?"
        description="This will re-initialize standard test catalog products and restore baseline policy configurations for testing."
      >
        <div className="text-xs text-muted-foreground space-y-2 py-2">
          <p>
            Standard products (<strong className="text-foreground">RUN-PRO-01</strong>, <strong className="text-foreground">AIR-VEST-02</strong>, <strong className="text-foreground">PACE-BAND-03</strong>) and default autonomy bounds (15% max discount, 20% min margin) will be verified and ensured.
          </p>
        </div>
        <DialogFooter>
          <Button variant="outline" size="sm" onClick={() => setShowResetModal(false)}>
            Cancel
          </Button>
          <Button variant="primary" size="sm" onClick={handleResetDemoState} disabled={isResetting}>
            {isResetting ? 'Resetting...' : 'Confirm Reset'}
          </Button>
        </DialogFooter>
      </Dialog>
    </div>
  );
};
