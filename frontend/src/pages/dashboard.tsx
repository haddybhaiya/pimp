import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth-store';
import { api } from '@/lib/api-client';
import { DashboardSummary } from '@/types/portal';
import { formatPaiseToINR } from '@/lib/utils';
import {
  Clock,
  ShieldCheck,
  AlertTriangle,
  ArrowRight,
  Package,
  Boxes,
  FileText,
  Sparkles,
  Sliders,
  TrendingUp,
  Activity,
  Layers,
  Lock,
} from 'lucide-react';

export interface DashboardPageProps {
  onNavigate: (path: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { merchant } = useAuth();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const data = await api.getDashboardSummary();
        setSummary(data);
      } catch {
        // Fallback
      } finally {
        setIsLoading(false);
      }
    };
    fetchSummary();
  }, []);

  const pendingApprovalsCount = summary?.pending_approvals_count ?? 0;

  return (
    <div className="space-y-6">
      {/* Action Required Alert (if pending approvals) */}
      {pendingApprovalsCount > 0 && (
        <div className="flex items-center justify-between rounded-xl border border-amber-500/40 bg-amber-500/10 p-4 shadow-glow-warning">
          <div className="flex items-center gap-3">
            <div className="p-2 rounded-lg bg-amber-500/20 text-amber-400">
              <AlertTriangle className="h-5 w-5" />
            </div>
            <div>
              <p className="text-xs font-mono uppercase text-amber-400 font-bold tracking-wide">
                Decision Required
              </p>
              <h3 className="text-sm font-semibold text-text-primary">
                {pendingApprovalsCount} Escalated Buyer Proposal(s) Awaiting Review
              </h3>
              <p className="text-xs text-text-secondary">
                Discounts exceeding autonomous policy thresholds have been halted and escalated for merchant authority.
              </p>
            </div>
          </div>
          <Button
            onClick={() => onNavigate('/approvals')}
            className="bg-amber-500 hover:bg-amber-600 text-[#070B14] font-semibold text-xs shadow-sm"
            size="sm"
          >
            Review Queue <ArrowRight className="h-3.5 w-3.5 ml-1" />
          </Button>
        </div>
      )}

      {/* Merchant Welcome & Live Autonomy Banner */}
      <div className="glass-panel rounded-2xl p-6 border border-[#24314A] bg-[#0D1424]/90 relative overflow-hidden">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-6 relative z-10">
          <div className="space-y-1">
            <div className="inline-flex items-center gap-2 px-2.5 py-0.5 rounded-full bg-brand/10 border border-brand/25 text-brand-bright text-[11px] font-mono">
              <Activity className="h-3 w-3" />
              Store Autonomy Level {summary?.autonomy_level ?? merchant?.policies.autonomyLevel ?? 1}
            </div>
            <h2 className="text-2xl sm:text-3xl font-extrabold text-text-primary tracking-tight">
              {merchant?.name || 'Autonomous Store'}
            </h2>
            <p className="text-xs text-text-secondary">
              Server-authoritative commerce gateway actively securing buyer agent transactions on Razorpay.
            </p>
          </div>

          <div className="flex flex-wrap items-center gap-3">
            <Button
              onClick={() => onNavigate('/demo')}
              className="bg-brand hover:bg-brand-deep text-white text-xs font-semibold shadow-glow-sm"
              size="sm"
            >
              <Sparkles className="h-3.5 w-3.5 mr-1 text-brand-bright" />
              Launch Simulation Sandbox
            </Button>
            <Button
              onClick={() => onNavigate('/policies')}
              variant="outline"
              size="sm"
              className="text-xs bg-[#141D31] border-[#24314A] text-text-secondary hover:text-text-primary"
            >
              <Sliders className="h-3.5 w-3.5 mr-1" />
              Policy Bounds
            </Button>
          </div>
        </div>
      </div>

      {/* 4 Core Financial & Operational KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Pending Approvals */}
        <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
          <div className="flex items-center justify-between text-xs font-mono text-text-muted mb-2">
            <span>PENDING APPROVALS</span>
            <Clock className="h-4 w-4 text-amber-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-amber-400">
            {isLoading ? '...' : pendingApprovalsCount}
          </div>
          <p className="text-[11px] text-text-secondary mt-1">
            Human-In-The-Loop tickets
          </p>
        </div>

        {/* Total Settled Revenue */}
        <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
          <div className="flex items-center justify-between text-xs font-mono text-text-muted mb-2">
            <span>SETTLED REVENUE</span>
            <TrendingUp className="h-4 w-4 text-emerald-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-emerald-400">
            {isLoading ? '...' : formatPaiseToINR(summary?.total_revenue_paise ?? 0)}
          </div>
          <p className="text-[11px] text-text-secondary mt-1">
            {summary?.total_orders ?? 0} settled order(s) via Razorpay
          </p>
        </div>

        {/* Active Catalog SKUs */}
        <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
          <div className="flex items-center justify-between text-xs font-mono text-text-muted mb-2">
            <span>CATALOG PRODUCTS</span>
            <Package className="h-4 w-4 text-brand-bright" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-text-primary">
            {isLoading ? '...' : summary?.total_products ?? 0}
          </div>
          <p className="text-[11px] text-text-secondary mt-1">
            Floor price protected items
          </p>
        </div>

        {/* Active Negotiated Quotes */}
        <div className="glass-card p-5 rounded-xl border border-[#24314A] card-hover">
          <div className="flex items-center justify-between text-xs font-mono text-text-muted mb-2">
            <span>ACTIVE QUOTES</span>
            <Layers className="h-4 w-4 text-blue-400" />
          </div>
          <div className="text-2xl sm:text-3xl font-bold text-text-primary">
            {isLoading ? '...' : summary?.active_quotes_count ?? 0}
          </div>
          <p className="text-[11px] text-text-secondary mt-1">
            In-flight buyer agent sessions
          </p>
        </div>
      </div>

      {/* Quick Access Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div
          onClick={() => onNavigate('/catalog')}
          className="glass-card p-5 rounded-xl border border-[#24314A] card-hover cursor-pointer"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-brand/10 text-brand-bright">
              <Package className="h-4 w-4" />
            </div>
            <h4 className="text-xs font-bold text-text-primary">Products & Floor Margins</h4>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Manage product catalog, base pricing, and guaranteed floor price margins.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/inventory')}
          className="glass-card p-5 rounded-xl border border-[#24314A] card-hover cursor-pointer"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-emerald-500/10 text-emerald-400">
              <Boxes className="h-4 w-4" />
            </div>
            <h4 className="text-xs font-bold text-text-primary">Inventory & Row Locks</h4>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Track stock levels and adjust reserves with PostgreSQL optimistic concurrency.
          </p>
        </div>

        <div
          onClick={() => onNavigate('/audit')}
          className="glass-card p-5 rounded-xl border border-[#24314A] card-hover cursor-pointer"
        >
          <div className="flex items-center gap-3 mb-2">
            <div className="p-2 rounded-lg bg-purple-500/10 text-purple-400">
              <FileText className="h-4 w-4" />
            </div>
            <h4 className="text-xs font-bold text-text-primary">Cryptographic Audit Chain</h4>
          </div>
          <p className="text-xs text-text-secondary leading-relaxed">
            Inspect SHA-256 chained audit logs and verify real-time tamper resistance.
          </p>
        </div>
      </div>

      {/* Authoritative Policy Fingerprint Card */}
      <div className="glass-panel p-5 rounded-xl border border-[#24314A] bg-[#0D1424]">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 mb-3">
          <div className="flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-brand-bright" />
            <h4 className="text-xs font-bold text-text-primary uppercase tracking-wider font-mono">
              Live Governance Policy Fingerprint
            </h4>
          </div>
          <span className="text-[11px] font-mono text-emerald-400 flex items-center gap-1">
            <Lock className="h-3 w-3" />
            Server Authoritative
          </span>
        </div>
        <div className="font-mono text-xs bg-[#070B14] p-3 rounded-lg border border-[#24314A] text-brand-bright break-all">
          {summary?.policy_hash || merchant?.policies.policyHash || '0'.repeat(64)}
        </div>
        <p className="text-[11px] text-text-muted mt-2">
          This deterministic SHA-256 hash guarantees that merchant bounds (floor prices, max discounts, transaction caps) are cryptographically fixed onto every order and audit record.
        </p>
      </div>
    </div>
  );
};


