import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import {
  ShieldCheck,
  Lock,
  Cpu,
  ArrowRight,
  Scale,
  KeyRound,
  FileCheck,
  Zap,
  Bot,
  Orbit,
  Check,
  BarChart3,
  BadgeCheck,
  Webhook,
  Network,
} from 'lucide-react';
import { CommerceOrbit } from '@/components/landing/commerce-orbit';
import { Reveal } from '@/components/ui/reveal';

export interface LandingPageProps {
  onNavigate: (path: string) => void;
}

export const LandingPage: React.FC<LandingPageProps> = ({ onNavigate }) => {
  const [activeStep, setActiveStep] = useState<number>(0);

  const pipelineSteps = [
    {
      id: 0,
      badge: 'Step 1: Inbound Discovery',
      title: 'Untrusted Buyer Agent',
      desc: 'Autonomous buyer agents discover products, negotiate quotes, and submit structured commerce intents under strict token constraints.',
      invariant: 'INV-AGY-01: Separation of Intelligence & Authority',
      details: 'All LLM proposals are wrapped in typed schemas and treated as completely untrusted input.',
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-300',
    },
    {
      id: 1,
      badge: 'Step 2: Deterministic Governance',
      title: 'Policy Engine Validation',
      desc: 'Pre-flight mathematical checks verify floor price margin, discount ceilings, max items, and merchant autonomy rules before any mutation.',
      invariant: 'INV-FIN-02: Strict Merchant Floor Price Guarantee',
      details: 'Evaluates ALLOW, ESCALATE_APPROVAL, or DENY with zero possibility of LLM override.',
      color: 'from-brand/20 to-emerald-500/20 border-brand/40 text-brand-bright',
    },
    {
      id: 2,
      badge: 'Step 3: Human-In-The-Loop',
      title: 'HITL Approval Queue',
      desc: 'High-discount negotiations or abnormal buyer proposals are escalated into expiring decision tickets for merchant review.',
      invariant: 'INV-AGY-02: Capability Boundary Enforcement',
      details: 'Optimistic concurrency locking ensures tickets cannot be double-resolved or bypassed.',
      color: 'from-amber-500/20 to-orange-500/20 border-amber-500/40 text-amber-400',
    },
    {
      id: 3,
      badge: 'Step 4: Financial Settlement',
      title: 'Razorpay Gateway & Webhooks',
      desc: 'Idempotent order generation and server-authoritative HMAC SHA-256 webhook capture guarantee exact 64-bit integer paise settlement.',
      invariant: 'INV-FIN-01 & INV-FIN-05: Server-Authoritative Settlement',
      details: 'Webhooks are deduplicated durably; stock is deducted atomically upon verified payment.',
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-400',
    },
    {
      id: 4,
      badge: 'Step 5: Cryptographic Assurance',
      title: 'Immutable SHA-256 Audit Trail',
      desc: 'Every session, quote, policy decision, approval, and settlement is chained with SHA-256 hashes for instant tamper detection.',
      invariant: 'INV-AGY-04: Tamper-Evident Cryptographic Ledger',
      details: 'Any out-of-band database mutation breaks the cryptographic link and alerts operators.',
      color: 'from-emerald-500/20 to-teal-500/20 border-emerald-500/40 text-emerald-300',
    },
  ];

  return (
    <div className="landing-theme flex min-h-screen flex-col overflow-hidden bg-[#080c0b] text-[#f8fafc] selection:bg-emerald-300/30">
      {/* Hero: the scene is decorative only; all commerce authority remains server-side. */}
      <section className="relative isolate overflow-hidden border-b border-white/[0.07] bg-[#080c0b] pb-20 pt-16 lg:pb-28 lg:pt-24">
        <div className="hero-grid absolute inset-0 -z-20 opacity-70" />
        <div className="absolute -left-28 top-0 -z-10 h-[34rem] w-[34rem] rounded-full bg-emerald-400/[0.08] blur-[130px]" />
        <div className="absolute bottom-0 right-[12%] -z-10 h-72 w-72 rounded-full bg-emerald-300/[0.06] blur-[110px]" />
        <CommerceOrbit />

        <div className="container relative z-10 mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="max-w-3xl text-left">
            <div className="mb-8 inline-flex items-center gap-2 rounded-full border border-emerald-300/20 bg-slate-950/50 px-3.5 py-1.5 backdrop-blur">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-300 shadow-[0_0_10px_#6ee7b7]" />
              <span className="text-[10px] font-mono uppercase tracking-[0.16em] text-slate-300">
                Agent commerce, constrained by design
              </span>
            </div>

            <h1 className="max-w-3xl font-display text-5xl font-bold tracking-[-0.065em] text-slate-50 sm:text-6xl lg:text-7xl lg:leading-[0.98]">
              The Autonomous AI Commerce{' '}
              <span className="text-emerald-300">control layer</span> for merchants who mean business.
            </h1>

            <p className="mt-7 max-w-2xl text-base leading-relaxed text-slate-300 sm:text-lg">
              pimp gives AI agents a governed way to buy from your store—with immutable policy, human escalation, and settlement that is verified before it moves a single paise.
            </p>

            <div className="mt-9 flex flex-col items-stretch gap-3 sm:flex-row sm:items-center">
            <Button
              onClick={() => onNavigate('/signup')}
              size="lg"
              className="w-full rounded-xl bg-emerald-300 px-7 py-3 text-sm font-bold text-slate-950 shadow-[0_12px_40px_rgba(52,211,153,0.16)] hover:bg-emerald-200 sm:w-auto"
            >
              Build your control plane
              <ArrowRight className="h-4 w-4 ml-2" />
            </Button>

            <Button
              onClick={() => onNavigate('/demo')}
              variant="outline"
              size="lg"
              className="w-full rounded-xl border-slate-600/70 bg-slate-950/30 px-6 py-3 text-sm font-medium text-slate-100 hover:border-emerald-300/60 hover:bg-slate-900/80 sm:w-auto"
            >
              <Orbit className="h-4 w-4 mr-2 text-emerald-300" />
              Explore the sandbox
            </Button>
          </div>

            <div className="mt-12 flex flex-wrap gap-x-5 gap-y-2 text-xs font-medium text-slate-300">
              {['No below-floor pricing', 'Human approval when it matters', 'HMAC-verified settlement'].map((item) => (
                <span key={item} className="inline-flex items-center gap-1.5">
                  <Check className="h-3.5 w-3.5 text-emerald-300" />
                  {item}
                </span>
              ))}
            </div>
          </div>

          <div className="relative mt-16 grid max-w-5xl grid-cols-2 gap-3 lg:mt-20 lg:grid-cols-4">
            <div className="hero-proof-card p-3.5 rounded-2xl text-left">
              <div className="flex items-center gap-2 mb-1">
                <Lock className="h-4 w-4 text-emerald-300" />
                <span className="text-[11px] font-mono font-bold text-slate-100">INV-FIN-02</span>
              </div>
              <p className="text-xs text-slate-400">Strict floor price margin guarantee</p>
            </div>

            <div className="hero-proof-card p-3.5 rounded-2xl text-left">
              <div className="flex items-center gap-2 mb-1">
                <Scale className="h-4 w-4 text-emerald-300" />
                <span className="text-[11px] font-mono font-bold text-slate-100">INV-FIN-01</span>
              </div>
              <p className="text-xs text-slate-400">64-bit integer paise, never float math</p>
            </div>

            <div className="hero-proof-card p-3.5 rounded-2xl text-left">
              <div className="flex items-center gap-2 mb-1">
                <Bot className="h-4 w-4 text-violet-300" />
                <span className="text-[11px] font-mono font-bold text-slate-100">INV-AGY-01</span>
              </div>
              <p className="text-xs text-slate-400">Intelligence is never authority</p>
            </div>

            <div className="hero-proof-card p-3.5 rounded-2xl text-left">
              <div className="flex items-center gap-2 mb-1">
                <FileCheck className="h-4 w-4 text-emerald-300" />
                <span className="text-[11px] font-mono font-bold text-slate-100">INV-AGY-04</span>
              </div>
              <p className="text-xs text-slate-400">Immutable SHA-256 audit chain</p>
            </div>
          </div>
        </div>
      </section>

      {/* Interactive Architecture Pipeline Section */}
      <section className="py-20 border-t border-[#24314A]/80 bg-[#0D1424]/40 relative">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <span className="text-xs font-mono font-semibold tracking-wider text-brand-bright uppercase">
              System Architecture
            </span>
            <h2 className="text-2xl sm:text-3xl font-bold tracking-tight text-text-primary mt-2">
              Server-Authoritative Agent Commerce Pipeline
            </h2>
            <p className="mt-3 text-sm text-text-secondary">
              Click any node in the pipeline to inspect its deterministic safety boundaries and security invariants.
            </p>
          </div>

          {/* Interactive Pipeline Node Bar */}
          <div className="grid grid-cols-2 sm:grid-cols-5 gap-2 mb-8">
            {pipelineSteps.map((step) => {
              const isSelected = activeStep === step.id;
              return (
                <button
                  key={step.id}
                  onClick={() => setActiveStep(step.id)}
                  className={`p-3 rounded-xl text-left transition-all border ${
                    isSelected
                      ? 'bg-[#141D31] border-brand shadow-glow-sm scale-[1.02]'
                      : 'bg-[#0D1424]/80 border-[#24314A] hover:border-brand/40 opacity-75 hover:opacity-100'
                  }`}
                >
                  <span className="text-[10px] font-mono text-text-muted block">{step.badge}</span>
                  <span className="font-semibold text-xs text-text-primary block mt-0.5 truncate">
                    {step.title}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Active Node Detail Card */}
          <div className="glass-panel rounded-2xl p-6 sm:p-8 border border-[#24314A] bg-[#0D1424]/90 relative overflow-hidden">
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 items-center">
              <div className="lg:col-span-2 space-y-3">
                <div className="inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-brand/10 border border-brand/30 text-brand-bright text-xs font-mono">
                  <KeyRound className="h-3.5 w-3.5" />
                  {pipelineSteps[activeStep].invariant}
                </div>
                <h3 className="text-xl font-bold text-text-primary">
                  {pipelineSteps[activeStep].title}
                </h3>
                <p className="text-sm text-text-secondary leading-relaxed">
                  {pipelineSteps[activeStep].desc}
                </p>
                <div className="p-3.5 rounded-xl bg-[#070B14] border border-[#24314A] font-mono text-xs text-text-secondary">
                  <span className="text-emerald-400 font-bold block mb-1">Server Guarantee:</span>
                  {pipelineSteps[activeStep].details}
                </div>
              </div>

              <div className="p-5 rounded-xl bg-[#070B14]/80 border border-[#24314A] space-y-3">
                <div className="flex items-center justify-between text-xs font-mono text-text-muted">
                  <span>Engine Status</span>
                  <span className="text-emerald-400">ACTIVE</span>
                </div>
                <div className="flex items-center justify-between text-xs font-mono text-text-muted">
                  <span>Target Database</span>
                  <span className="text-text-primary">PostgreSQL</span>
                </div>
                <div className="flex items-center justify-between text-xs font-mono text-text-muted">
                  <span>Payment Gateway</span>
                  <span className="text-brand-bright">Razorpay v1</span>
                </div>
                <Button
                  onClick={() => onNavigate('/demo')}
                  size="sm"
                  className="w-full mt-2 bg-brand/15 hover:bg-brand/25 border border-brand/40 text-brand-bright text-xs"
                >
                  Simulate in Sandbox
                </Button>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Product operations preview */}
      <section className="border-t border-white/[0.07] bg-[#0a0e11] py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <Reveal className="grid items-center gap-12 lg:grid-cols-[0.82fr_1.18fr]">
            <div>
              <span className="text-[10px] font-mono font-semibold uppercase tracking-[0.18em] text-emerald-300">One operating view</span>
              <h2 className="mt-4 max-w-lg font-display text-3xl font-semibold tracking-[-0.045em] text-slate-50 sm:text-4xl">
                See the decision before it becomes a transaction.
              </h2>
              <p className="mt-5 max-w-lg text-sm leading-7 text-slate-400">
                Follow buyer intent from discovery through policy evaluation, merchant approval, and verified settlement—without giving the agent authority it should not have.
              </p>
              <div className="mt-8 grid grid-cols-2 gap-5 border-t border-white/10 pt-6">
                <div><p className="font-display text-2xl font-semibold text-slate-100">5</p><p className="mt-1 text-xs text-slate-500">bounded tool steps</p></div>
                <div><p className="font-display text-2xl font-semibold text-slate-100">15s</p><p className="mt-1 text-xs text-slate-500">maximum agent turn</p></div>
              </div>
            </div>

            <div className="operations-preview">
              <div className="flex items-center justify-between border-b border-white/10 px-5 py-3.5">
                <div className="flex items-center gap-2"><span className="h-2 w-2 rounded-full bg-emerald-300" /><span className="text-xs font-medium text-slate-200">Live commerce trace</span></div>
                <span className="rounded border border-white/10 px-2 py-1 font-mono text-[9px] text-slate-500">REQ_8F21</span>
              </div>
              <div className="divide-y divide-white/[0.07]">
                {[
                  ['01', 'Buyer intent received', 'UNTRUSTED', Network],
                  ['02', 'Floor and discount policy checked', 'ALLOWED', BadgeCheck],
                  ['03', 'Inventory version locked', 'RESERVED', BarChart3],
                  ['04', 'Settlement webhook verified', 'CAPTURED', Webhook],
                ].map(([step, title, status, Icon]) => {
                  const RowIcon = Icon as typeof Network;
                  return (
                    <div key={step as string} className="group flex items-center gap-4 px-5 py-4 transition-colors hover:bg-white/[0.025]">
                      <span className="font-mono text-[10px] text-slate-600">{step as string}</span>
                      <span className="flex h-8 w-8 items-center justify-center rounded-md border border-white/10 bg-white/[0.025] text-slate-400"><RowIcon className="h-4 w-4" /></span>
                      <span className="min-w-0 flex-1 text-sm text-slate-300">{title as string}</span>
                      <span className="font-mono text-[9px] font-semibold tracking-[0.1em] text-emerald-300">{status as string}</span>
                    </div>
                  );
                })}
              </div>
            </div>
          </Reveal>
        </div>
      </section>

      {/* Feature Grid Section */}
      <section className="py-20 border-t border-[#24314A]/60">
        <div className="container mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-2xl mx-auto mb-16">
            <span className="text-xs font-mono text-brand-bright uppercase tracking-wider">Merchant Governance</span>
            <h2 className="text-3xl font-bold tracking-tight text-text-primary mt-1">
              Engineered for Complete Autonomous Reliability
            </h2>
            <p className="mt-3 text-sm text-text-secondary">
              Four fundamental architectural pillars ensuring autonomous commerce operates with zero financial risk.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
            <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
              <div className="h-10 w-10 rounded-xl bg-brand/10 text-brand-bright flex items-center justify-center mb-4">
                <Cpu className="h-5 w-5" />
              </div>
              <h3 className="text-sm font-bold text-text-primary mb-1">Agent Protocol Native</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Seamless support for autonomous buyer sessions, structured quote negotiations, and product discovery RPCs.
              </p>
            </div>

            <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
              <div className="h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-400 flex items-center justify-center mb-4">
                <Lock className="h-5 w-5" />
              </div>
              <h3 className="text-sm font-bold text-text-primary mb-1">Deterministic Policy</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Mathematical floor price guarantees, 50% max discount caps, and integer paise monetary precision.
              </p>
            </div>

            <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
              <div className="h-10 w-10 rounded-xl bg-amber-500/10 text-amber-400 flex items-center justify-center mb-4">
                <ShieldCheck className="h-5 w-5" />
              </div>
              <h3 className="text-sm font-bold text-text-primary mb-1">HITL Approval Queue</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                Expiring decision tickets for high-discount negotiations with optimistic concurrency locking.
              </p>
            </div>

            <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
              <div className="h-10 w-10 rounded-xl bg-emerald-500/10 text-emerald-300 flex items-center justify-center mb-4">
                <Zap className="h-5 w-5" />
              </div>
              <h3 className="text-sm font-bold text-text-primary mb-1">Razorpay Settlement</h3>
              <p className="text-xs text-text-secondary leading-relaxed">
                HMAC SHA-256 verified webhooks, idempotent orders, and tamper-evident cryptographic audit ledger.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="border-t border-white/[0.07] bg-[#080b0d] py-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8">
          <Reveal>
            <div className="grid gap-px overflow-hidden rounded-2xl border border-white/10 bg-white/10 sm:grid-cols-3">
              {[
                ['Integer paise', 'Precise money by default', 'No floating-point pricing anywhere in the transaction path.'],
                ['Fail closed', 'Ambiguity never ships', 'Invalid state, policy, or capability checks stop before mutation.'],
                ['Audit chained', 'Every decision has a history', 'SHA-256 links policy decisions, approvals, and settlement events.'],
              ].map(([eyebrow, title, description]) => (
                <div key={eyebrow} className="bg-[#0c1114] p-7 sm:p-8">
                  <p className="font-mono text-[9px] font-semibold uppercase tracking-[0.16em] text-emerald-300">{eyebrow}</p>
                  <h3 className="mt-4 text-lg font-semibold tracking-[-0.025em] text-slate-100">{title}</h3>
                  <p className="mt-3 text-sm leading-6 text-slate-500">{description}</p>
                </div>
              ))}
            </div>
          </Reveal>

          <Reveal className="mt-20 flex flex-col items-start justify-between gap-8 border-t border-white/10 pt-12 sm:flex-row sm:items-end">
            <div><p className="text-[10px] font-mono uppercase tracking-[0.18em] text-emerald-300">Ready when you are</p><h2 className="mt-3 max-w-2xl font-display text-3xl font-semibold tracking-[-0.045em] text-slate-50 sm:text-4xl">Give agents access to commerce. Keep authority with the merchant.</h2></div>
            <Button onClick={() => onNavigate('/signup')} size="lg" className="shrink-0 bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200">Create your store <ArrowRight className="h-4 w-4" /></Button>
          </Reveal>
        </div>
      </section>

    </div>
  );
};

