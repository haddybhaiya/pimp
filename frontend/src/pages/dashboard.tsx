import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/lib/auth-store';
import { api } from '@/lib/api-client';
import { DashboardSummary } from '@/types/portal';
import { formatPaiseToINR } from '@/lib/utils';
import {
  Clock,
  ShieldCheck,
  ShoppingCart,
  AlertTriangle,
  ArrowRight,
  Package,
  Boxes,
  FileSpreadsheet,
  FileText,
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
      {/* Welcome Banner */}
      <div className="rounded-xl border border-border bg-gradient-to-r from-card to-secondary/30 p-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold tracking-tight">{merchant?.name}</h2>
            <p className="text-sm text-muted-foreground mt-1">
              Autonomous AI Control Plane is active on Razorpay infrastructure.
            </p>
          </div>
          <div className="flex items-center gap-3">
            <Badge variant="default" className="font-mono text-xs">
              Autonomy Level {summary?.autonomy_level ?? merchant?.policies.autonomyLevel ?? 1}
            </Badge>
            <Badge variant="success" className="text-xs">
              {summary?.status ?? merchant?.status ?? 'ACTIVE'}
            </Badge>
          </div>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase">Pending Approvals</CardDescription>
            <CardTitle className="text-2xl font-bold text-amber-400 flex items-center justify-between">
              <span>{isLoading ? '...' : pendingApprovalsCount}</span>
              <Clock className="h-5 w-5 text-amber-400/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Human-In-The-Loop gate tickets</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase">Total Revenue</CardDescription>
            <CardTitle className="text-2xl font-bold text-emerald-400 flex items-center justify-between">
              <span>{isLoading ? '...' : formatPaiseToINR(summary?.total_revenue_paise ?? 0)}</span>
              <ShoppingCart className="h-5 w-5 text-emerald-400/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">{summary?.total_orders ?? 0} committed order(s)</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase">Catalog Products</CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground flex items-center justify-between">
              <span>{isLoading ? '...' : summary?.total_products ?? 0}</span>
              <Package className="h-5 w-5 text-primary/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Active discoverable SKUs</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase">Active Quotes</CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground flex items-center justify-between">
              <span>{isLoading ? '...' : summary?.active_quotes_count ?? 0}</span>
              <FileSpreadsheet className="h-5 w-5 text-muted-foreground/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Live buyer agent sessions</p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Action Banner */}
      {pendingApprovalsCount > 0 && (
        <div className="flex items-center justify-between rounded-lg border border-amber-500/40 bg-amber-500/10 p-4">
          <div className="flex items-center gap-3">
            <AlertTriangle className="h-5 w-5 text-amber-400" />
            <div>
              <p className="text-sm font-semibold text-amber-300">Action Required: {pendingApprovalsCount} Pending Approval Ticket(s)</p>
              <p className="text-xs text-muted-foreground">Buyer negotiations escalated for merchant review.</p>
            </div>
          </div>
          <Button onClick={() => onNavigate('/approvals')} variant="secondary" size="sm">
            Review Queue <ArrowRight className="h-4 w-4 ml-1" />
          </Button>
        </div>
      )}

      {/* Quick Navigation Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card onClick={() => onNavigate('/catalog')} className="cursor-pointer hover:border-primary transition-colors bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Package className="h-4 w-4 text-primary" /> Catalog & Products
            </CardTitle>
            <CardDescription className="text-xs">Manage product SKUs, prices & floor price guarantees.</CardDescription>
          </CardHeader>
        </Card>

        <Card onClick={() => onNavigate('/inventory')} className="cursor-pointer hover:border-primary transition-colors bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <Boxes className="h-4 w-4 text-primary" /> Stock & Reservations
            </CardTitle>
            <CardDescription className="text-xs">View stock quantities and adjust inventory with optimistic locking.</CardDescription>
          </CardHeader>
        </Card>

        <Card onClick={() => onNavigate('/audit')} className="cursor-pointer hover:border-primary transition-colors bg-card/60">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-semibold flex items-center gap-2">
              <FileText className="h-4 w-4 text-primary" /> Cryptographic Ledger
            </CardTitle>
            <CardDescription className="text-xs">Inspect SHA-256 hash-chained immutable audit events.</CardDescription>
          </CardHeader>
        </Card>
      </div>

      {/* Policy Hash Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base flex items-center gap-2">
            <ShieldCheck className="h-4 w-4 text-primary" /> Authoritative Policy Hash
          </CardTitle>
          <CardDescription>Deterministic SHA-256 fingerprint stamped onto every transaction audit record.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="font-mono text-xs bg-muted/40 p-3 rounded border border-border text-foreground break-all">
            {summary?.policy_hash || merchant?.policies.policyHash || '0'.repeat(64)}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

