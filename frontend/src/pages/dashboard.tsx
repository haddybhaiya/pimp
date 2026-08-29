import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { useAuth } from '@/lib/auth-store';
import { api } from '@/lib/api-client';
import { formatPaiseToINR } from '@/lib/utils';
import { Clock, ShieldCheck, ShoppingCart, Zap, AlertTriangle, ArrowRight } from 'lucide-react';

export interface DashboardPageProps {
  onNavigate: (path: string) => void;
}

export const DashboardPage: React.FC<DashboardPageProps> = ({ onNavigate }) => {
  const { merchant } = useAuth();
  const [pendingApprovalsCount, setPendingApprovalsCount] = useState<number>(0);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchSummary = async () => {
      try {
        const res = await api.executeGateway<{ total_count: number }>('list_approvals', { status: 'PENDING', limit: 1 });
        if (res.status === 'SUCCESS' && res.data) {
          setPendingApprovalsCount(res.data.total_count || 0);
        }
      } catch {
        // Fallback
      } finally {
        setIsLoading(false);
      }
    };
    fetchSummary();
  }, []);

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
              Autonomy Level {merchant?.policies.autonomyLevel ?? 1}
            </Badge>
            <Badge variant="success" className="text-xs">
              {merchant?.status ?? 'ACTIVE'}
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
            <CardDescription className="text-xs font-medium uppercase">Max Discount Cap</CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground flex items-center justify-between">
              <span>{merchant?.policies.maxDiscountPercentage}%</span>
              <Zap className="h-5 w-5 text-primary/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Enforced by DeterministicPolicyEngine</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase">Min Margin Guard</CardDescription>
            <CardTitle className="text-2xl font-bold text-emerald-400 flex items-center justify-between">
              <span>{merchant?.policies.minMarginPercentage}%</span>
              <ShieldCheck className="h-5 w-5 text-emerald-400/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Guaranteed mathematical floor</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardDescription className="text-xs font-medium uppercase">Single Tx Ceiling</CardDescription>
            <CardTitle className="text-2xl font-bold text-foreground flex items-center justify-between">
              <span>{formatPaiseToINR(merchant?.policies.maxSingleTransactionPaise ?? 5000000)}</span>
              <ShoppingCart className="h-5 w-5 text-muted-foreground/60" />
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-xs text-muted-foreground">Platform safety bound</p>
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

      {/* Policy Hash Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-base">Authoritative Policy Hash</CardTitle>
          <CardDescription>Deterministic SHA-256 fingerprint stamped onto every transaction audit record.</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="font-mono text-xs bg-muted/40 p-3 rounded border border-border text-foreground break-all">
            {merchant?.policies.policyHash || '0'.repeat(64)}
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
