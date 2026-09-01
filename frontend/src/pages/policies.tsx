import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { useAuth } from '@/lib/auth-store';
import { PolicyGovernance } from '@/types/portal';
import { ShieldCheck, CheckCircle2, AlertTriangle } from 'lucide-react';

export const PoliciesPage: React.FC = () => {
  const { updateProfile } = useAuth();
  const [policyData, setPolicyData] = useState<PolicyGovernance | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [isSaving, setIsSaving] = useState<boolean>(false);
  const [successMsg, setSuccessMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const [autonomyLevel, setAutonomyLevel] = useState<number>(1);
  const [maxDiscountPct, setMaxDiscountPct] = useState<number>(15);
  const [minMarginPct, setMinMarginPct] = useState<number>(20);
  const [maxTxRupees, setMaxTxRupees] = useState<number>(50000);

  const fetchPolicies = async () => {
    setIsLoading(true);
    try {
      const data = await api.getPolicies();
      setPolicyData(data);
      setAutonomyLevel(data.autonomy_level);
      setMaxDiscountPct(data.max_discount_percentage);
      setMinMarginPct(data.min_margin_percentage);
      setMaxTxRupees(data.max_single_transaction_paise / 100);
      setError(null);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to load policy rules.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPolicies();
  }, []);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSaving(true);
    setError(null);
    setSuccessMsg(null);
    try {
      const updated = await api.updatePolicies({
        autonomy_level: autonomyLevel,
        max_discount_percentage: maxDiscountPct,
        min_margin_percentage: minMarginPct,
        max_single_transaction_paise: Math.round(maxTxRupees * 100),
      });
      setPolicyData(updated);
      updateProfile({
        policies: {
          autonomyLevel: updated.autonomy_level,
          maxDiscountPercentage: updated.max_discount_percentage,
          minMarginPercentage: updated.min_margin_percentage,
          maxSingleTransactionPaise: updated.max_single_transaction_paise,
          policyHash: updated.policy_hash,
          protocolVersion: updated.protocol_version,
        },
      });
      setSuccessMsg('Policy rules and deterministic SHA-256 hash updated successfully.');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update policy rules.');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Policy Rules & Autonomy Governance</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Deterministic mathematical safety boundaries enforced on all AI agent interactions.
        </p>
      </div>

      {successMsg && (
        <div className="flex items-center gap-2 rounded bg-emerald-500/15 border border-emerald-500/30 p-3 text-xs text-emerald-400 font-medium">
          <CheckCircle2 className="h-4 w-4 shrink-0" />
          <span>{successMsg}</span>
        </div>
      )}

      {error && (
        <div className="flex items-center gap-2 rounded bg-destructive/15 p-3 text-xs text-destructive font-medium">
          <AlertTriangle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <Skeleton className="h-96 w-full" />
      ) : policyData ? (
        <form onSubmit={handleSave} className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <Card className="lg:col-span-2 border-border bg-card/90">
            <CardHeader>
              <CardTitle className="text-base">Merchant Autonomy & Financial Bounds</CardTitle>
              <CardDescription>Adjust discount ceilings, minimum profit margins, and single transaction caps.</CardDescription>
            </CardHeader>

            <CardContent className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">
                  Autonomy Level
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { level: 0, label: 'Level 0', desc: 'Read-Only (No Negotiation)' },
                    { level: 1, label: 'Level 1', desc: 'Bounded Auto-Acceptance' },
                    { level: 2, label: 'Level 2', desc: 'Supervised HITL Escalation' },
                  ].map((item) => (
                    <button
                      key={item.level}
                      type="button"
                      onClick={() => setAutonomyLevel(item.level)}
                      className={`p-3 text-left rounded-md border transition-all ${
                        autonomyLevel === item.level
                          ? 'border-primary bg-primary/10 text-primary ring-1 ring-primary'
                          : 'border-border bg-card text-muted-foreground hover:bg-accent'
                      }`}
                    >
                      <p className="font-bold text-xs">{item.label}</p>
                      <p className="text-[10px] text-muted-foreground mt-0.5">{item.desc}</p>
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                <Input
                  label="Max Discount Percentage (%)"
                  type="number"
                  value={maxDiscountPct}
                  onChange={(e) => setMaxDiscountPct(parseFloat(e.target.value) || 0)}
                  min={0}
                  max={50}
                  helperText="Platform ceiling: 50%"
                  required
                />
                <Input
                  label="Minimum Margin Percentage (%)"
                  type="number"
                  value={minMarginPct}
                  onChange={(e) => setMinMarginPct(parseFloat(e.target.value) || 0)}
                  min={0}
                  max={100}
                  required
                />
              </div>

              <Input
                label="Max Single Transaction Limit (₹)"
                type="number"
                value={maxTxRupees}
                onChange={(e) => setMaxTxRupees(parseFloat(e.target.value) || 0)}
                min={1}
                max={100000}
                helperText="Platform transaction ceiling: ₹1,00,000"
                required
              />
            </CardContent>

            <CardFooter className="flex justify-end border-t border-border pt-4">
              <Button type="submit" isLoading={isSaving} size="sm">
                <CheckCircle2 className="h-4 w-4 mr-1" /> Save Policy Rules
              </Button>
            </CardFooter>
          </Card>

          {/* Policy Hash Card */}
          <div className="space-y-4">
            <Card className="border-border bg-card/90">
              <CardHeader>
                <div className="flex items-center gap-2 text-primary">
                  <ShieldCheck className="h-5 w-5" />
                  <CardTitle className="text-base">Policy Hash</CardTitle>
                </div>
                <CardDescription>SHA-256 fingerprint generated over normalized governance rules.</CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                <div className="font-mono text-xs bg-muted/40 p-3 rounded border border-border text-foreground break-all">
                  {policyData?.policy_hash}
                </div>
                <p className="text-[11px] text-muted-foreground">
                  Stamping this hash onto all transactions guarantees cryptographic non-repudiation of policy state.
                </p>
              </CardContent>
            </Card>
          </div>
        </form>
      ) : (
        <div className="rounded-lg border border-rose-400/30 bg-rose-400/10 p-4 text-sm text-rose-100">
          Policy controls are unavailable until the current server policy can be loaded.
          <Button onClick={fetchPolicies} variant="outline" size="sm" className="ml-3 border-rose-300/30 text-rose-100">Retry</Button>
        </div>
      )}
    </div>
  );
};
