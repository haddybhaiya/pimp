import React from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardHeader, CardTitle, CardDescription } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { ShieldCheck, Zap, Lock, Cpu, ArrowRight, Terminal } from 'lucide-react';

export interface LandingPageProps {
  onNavigate: (path: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-20 pb-24 lg:pt-32 lg:pb-36">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 text-center relative z-10">
          <Badge variant="default" className="mb-6 px-3 py-1 font-mono text-xs">
            <Zap className="h-3 w-3 mr-1" /> Autonomous AI Commerce v2026-03-01
          </Badge>

          <h1 className="text-4xl sm:text-6xl lg:text-7xl font-extrabold tracking-tight max-w-4xl mx-auto leading-tight">
            The Autonomous AI Commerce{' '}
            <span className="bg-gradient-to-r from-primary via-indigo-400 to-purple-400 bg-clip-text text-transparent">
              Control Plane
            </span>
          </h1>

          <p className="mt-6 text-lg sm:text-xl text-muted-foreground max-w-2xl mx-auto font-normal">
            Turn your store into an agent-ready merchant on Razorpay infrastructure. Deterministic floor pricing, Human-In-The-Loop governance, and server-authoritative settlement.
          </p>

          <div className="mt-10 flex flex-col sm:flex-row items-center justify-center gap-4">
            <Button onClick={() => onNavigate('/signup')} size="lg" className="w-full sm:w-auto shadow-lg shadow-primary/25">
              Launch Merchant Control Plane
              <ArrowRight className="h-4 w-4 ml-1" />
            </Button>
            <Button onClick={() => onNavigate('/login')} variant="outline" size="lg" className="w-full sm:w-auto">
              Sign In to Dashboard
            </Button>
          </div>
        </div>
      </section>

      {/* Feature Grid */}
      <section className="py-16 border-t border-border bg-card/30">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <h2 className="text-3xl font-bold tracking-tight">Engineered for Autonomous Commerce</h2>
            <p className="mt-3 text-muted-foreground">Four non-negotiable architectural pillars keeping merchants safe.</p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            <Card className="border-border/80 bg-card/60">
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-primary/10 text-primary flex items-center justify-center mb-3">
                  <Cpu className="h-5 w-5" />
                </div>
                <CardTitle className="text-base">Agent Protocol Ready</CardTitle>
                <CardDescription>
                  Native support for ACP, structured intent negotiation, and autonomous buyer agent sessions.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/80 bg-card/60">
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-3">
                  <Lock className="h-5 w-5" />
                </div>
                <CardTitle className="text-base">Deterministic Policy</CardTitle>
                <CardDescription>
                  Mathematical floor price guards, 50% discount caps, and integer paise monetary representation.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/80 bg-card/60">
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-amber-500/10 text-amber-400 flex items-center justify-center mb-3">
                  <ShieldCheck className="h-5 w-5" />
                </div>
                <CardTitle className="text-base">HITL Approval Gates</CardTitle>
                <CardDescription>
                  Expiring human approval tickets for high-discount negotiations with optimistic locking.
                </CardDescription>
              </CardHeader>
            </Card>

            <Card className="border-border/80 bg-card/60">
              <CardHeader>
                <div className="h-10 w-10 rounded-lg bg-indigo-500/10 text-indigo-400 flex items-center justify-center mb-3">
                  <Zap className="h-5 w-5" />
                </div>
                <CardTitle className="text-base">Razorpay Settlement</CardTitle>
                <CardDescription>
                  HMAC SHA-256 verified webhooks, idempotent order creation, and tamper-evident audit ledger.
                </CardDescription>
              </CardHeader>
            </Card>
          </div>
        </div>
      </section>

      {/* Protocol Visualizer Section */}
      <section className="py-16 border-t border-border">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="rounded-xl border border-border bg-card/90 p-6 sm:p-8">
            <div className="flex items-center gap-2 mb-4">
              <Terminal className="h-5 w-5 text-primary" />
              <h3 className="font-mono text-sm font-semibold">Live Agent Commerce Pipeline</h3>
            </div>
            <div className="space-y-3 font-mono text-xs text-muted-foreground bg-background/90 p-4 rounded-lg border border-border">
              <div className="text-emerald-400">1. [BUYER_AGENT] POST /api/v1/gateway/discover-products → 8 SKUs available</div>
              <div className="text-indigo-400">2. [GATEWAY] PolicyEngine.evaluate_quote(proposal) → VERDICT: ALLOW (Floor: ₹4,000, Proposed: ₹4,500)</div>
              <div className="text-amber-400">3. [FSM] PriceQuoteStateMachine(PROPOSED → ACCEPTED) [version: 1]</div>
              <div className="text-blue-400">4. [RAZORPAY] PaymentService.create_order() → rzp_order_1001 (₹4500.00 locked)</div>
              <div className="text-purple-400">5. [AUDIT] AuditEvent(hash: 8f9b...e21) committed to immutable SHA-256 chain</div>
            </div>
          </div>
        </div>
      </section>
    </div>
  );
};
