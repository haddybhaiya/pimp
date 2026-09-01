import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { StepIndicator } from '@/components/ui/step-indicator';
import { useAuth } from '@/lib/auth-store';
import { api } from '@/lib/api-client';
import { CheckCircle2, ArrowRight, ArrowLeft } from 'lucide-react';

export interface OnboardingPageProps {
  onNavigate: (path: string) => void;
}

export const OnboardingPage: React.FC<OnboardingPageProps> = ({ onNavigate }) => {
  const { merchant, updateProfile } = useAuth();
  const [step, setStep] = useState(1);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Form State
  const [name, setName] = useState(merchant?.name || '');
  const [rzpKeyId, setRzpKeyId] = useState(merchant?.rzpKeyId || 'rzp_test_placeholder');
  const [autonomyLevel, setAutonomyLevel] = useState(merchant?.policies.autonomyLevel ?? 1);
  const [maxDiscountPct, setMaxDiscountPct] = useState(merchant?.policies.maxDiscountPercentage ?? 15.0);
  const [minMarginPct, setMinMarginPct] = useState(merchant?.policies.minMarginPercentage ?? 20.0);
  const [maxTxRupees, setMaxTxRupees] = useState((merchant?.policies.maxSingleTransactionPaise ?? 5000000) / 100);

  const steps = [
    { id: 1, title: 'Identity' },
    { id: 2, title: 'Razorpay' },
    { id: 3, title: 'Policies' },
    { id: 4, title: 'Activate' },
  ];

  const handleNext = () => {
    if (step < 4) setStep(step + 1);
  };

  const handleBack = () => {
    if (step > 1) setStep(step - 1);
  };

  const handleComplete = async () => {
    if (maxTxRupees > 100000) {
      setError('The platform ceiling is ₹1,00,000 per transaction.');
      return;
    }
    setIsLoading(true);
    setError(null);
    try {
      const updated = await api.completeSetup({
        name,
        rzpKeyId,
        autonomyLevel,
        maxDiscountPercentage: maxDiscountPct,
        minMarginPercentage: minMarginPct,
        maxSingleTransactionPaise: Math.round(maxTxRupees * 100),
      });
      updateProfile(updated);
      onNavigate('/dashboard');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Unable to complete merchant setup.');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-xl border-border/80 bg-card/90 shadow-2xl">
        <CardHeader>
          <StepIndicator steps={steps} currentStep={step} className="mb-6" />
          <CardTitle className="text-xl">
            {step === 1 && 'Store Identity & Branding'}
            {step === 2 && 'Razorpay Settlement Gateway'}
            {step === 3 && 'Autonomous Policy Bounds'}
            {step === 4 && 'Review & Activate Control Plane'}
          </CardTitle>
          <CardDescription>
            {step === 1 && 'Confirm your store identity used by external buyer agents.'}
            {step === 2 && 'Configure testmode Razorpay credentials for payment capture.'}
            {step === 3 && 'Establish strict mathematical boundaries for AI negotiations.'}
            {step === 4 && 'Confirm your configuration and launch your agent-ready store.'}
          </CardDescription>
        </CardHeader>

        <CardContent className="space-y-4">
          {error && <div className="rounded-md border border-rose-400/30 bg-rose-400/10 p-3 text-xs text-rose-100">{error}</div>}
          {step === 1 && (
            <div className="space-y-4">
              <Input
                label="Store Name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="e.g. Apex Athletic"
              />
              <Input
                label="Store Slug"
                value={merchant?.slug || ''}
                disabled
                helperText="Store slug cannot be changed once created"
              />
              <Input
                label="Operating Currency"
                value={merchant?.currency || 'INR'}
                disabled
              />
            </div>
          )}

          {step === 2 && (
            <div className="space-y-4">
              <Input
                label="Razorpay API Key ID"
                value={rzpKeyId}
                onChange={(e) => setRzpKeyId(e.target.value)}
                placeholder="rzp_test_..."
              />
              <div className="rounded-md bg-secondary/60 p-3 text-xs text-muted-foreground space-y-1">
                <p className="font-semibold text-foreground">🔒 Zero Secret Leakage Invariant (INV-AGY-03)</p>
                <p>Key secrets and database credentials are strictly held in the server environment and never exposed to the browser.</p>
              </div>
            </div>
          )}

          {step === 3 && (
            <div className="space-y-4">
              <div>
                <label className="block text-xs font-medium text-muted-foreground mb-1.5">
                  Autonomy Level
                </label>
                <div className="grid grid-cols-3 gap-2">
                  {[
                    { level: 0, name: 'L0: Read-Only' },
                    { level: 1, name: 'L1: Bounded' },
                    { level: 2, name: 'L2: Supervised' },
                  ].map((item) => (
                    <button
                      key={item.level}
                      type="button"
                      onClick={() => setAutonomyLevel(item.level)}
                      className={`p-2.5 text-xs font-semibold rounded-md border text-center transition-colors ${
                        autonomyLevel === item.level
                          ? 'border-primary bg-primary/10 text-primary'
                          : 'border-border bg-card text-muted-foreground hover:bg-accent'
                      }`}
                    >
                      {item.name}
                    </button>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-2 gap-3">
                <Input
                  label="Max Discount (%)"
                  type="number"
                  value={maxDiscountPct}
                  onChange={(e) => setMaxDiscountPct(parseFloat(e.target.value) || 0)}
                  min={0}
                  max={50}
                  helperText="Platform cap: 50%"
                />
                <Input
                  label="Min Margin (%)"
                  type="number"
                  value={minMarginPct}
                  onChange={(e) => setMinMarginPct(parseFloat(e.target.value) || 0)}
                  min={0}
                  max={100}
                />
              </div>

              <Input
                label="Max Single Transaction (₹)"
                type="number"
                value={maxTxRupees}
                onChange={(e) => setMaxTxRupees(parseFloat(e.target.value) || 0)}
                max={100000}
                helperText="Platform ceiling: ₹1,00,000"
              />
            </div>
          )}

          {step === 4 && (
            <div className="space-y-3 font-mono text-xs rounded-lg border border-border bg-muted/30 p-4">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Store Name:</span>
                <span className="font-semibold text-foreground">{name}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Slug:</span>
                <span className="text-foreground">{merchant?.slug}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Autonomy Mode:</span>
                <span className="text-primary font-bold">Level {autonomyLevel}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Discount Ceiling:</span>
                <span className="text-foreground">{maxDiscountPct}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Min Margin:</span>
                <span className="text-foreground">{minMarginPct}%</span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Max Tx Limit:</span>
                <span className="text-foreground">₹{maxTxRupees.toLocaleString('en-IN')}</span>
              </div>
            </div>
          )}
        </CardContent>

        <CardFooter className="flex justify-between">
          {step > 1 ? (
            <Button onClick={handleBack} variant="outline" size="sm">
              <ArrowLeft className="h-4 w-4 mr-1" /> Back
            </Button>
          ) : <div />}

          {step < 4 ? (
            <Button onClick={handleNext} size="sm">
              Continue <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
          ) : (
            <Button onClick={handleComplete} isLoading={isLoading} size="sm">
              <CheckCircle2 className="h-4 w-4 mr-1" /> Complete & Launch
            </Button>
          )}
        </CardFooter>
      </Card>
    </div>
  );
};
