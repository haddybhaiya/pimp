import React, { useEffect, useState } from 'react';
import { Card, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { AuditLedger, AuditEventItem } from '@/types/portal';
import { formatRelativeTime } from '@/lib/utils';
import { FileText, ShieldCheck, ShieldAlert } from 'lucide-react';

export const AuditPage: React.FC = () => {
  const [ledger, setLedger] = useState<AuditLedger | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchAudit = async () => {
      try {
        const data = await api.getAuditLedger(50);
        setLedger(data);
      } finally {
        setIsLoading(false);
      }
    };
    fetchAudit();
  }, []);

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight">Audit Trail & Cryptographic Ledger</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Immutable, SHA-256 hash-chained record of all domain mutations and financial events.
          </p>
        </div>

        {ledger && (
          <div className="flex items-center gap-2">
            {ledger.chain_valid ? (
              <Badge variant="success" className="gap-1 px-3 py-1">
                <ShieldCheck className="h-3.5 w-3.5" /> Chain Verified: 100% Intact
              </Badge>
            ) : (
              <Badge variant="destructive" className="gap-1 px-3 py-1">
                <ShieldAlert className="h-3.5 w-3.5" /> Hash Mismatch Detected
              </Badge>
            )}
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-20 w-full" />)}
        </div>
      ) : !ledger || ledger.events.length === 0 ? (
        <EmptyState
          icon={<FileText className="h-10 w-10" />}
          title="No audit events logged"
          description="System mutations and financial events will append to this immutable ledger."
        />
      ) : (
        <div className="space-y-3">
          {ledger.events.map((e: AuditEventItem) => (
            <Card key={e.id} className="border-border bg-card/80">
              <CardContent className="p-4 space-y-2">
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 text-xs">
                  <div className="flex items-center gap-2">
                    <Badge variant="default" className="text-[10px] font-mono">{e.event_type}</Badge>
                    <span className="font-semibold text-foreground">{e.actor_type}</span>
                  </div>
                  <div className="flex items-center gap-3 text-muted-foreground font-mono text-[11px]">
                    <span>Hash: {e.event_hash.slice(0, 12)}...</span>
                    <span>{formatRelativeTime(e.created_at)}</span>
                  </div>
                </div>

                <div className="bg-background/80 p-2.5 rounded border border-border font-mono text-[11px] text-muted-foreground overflow-x-auto">
                  <pre>{JSON.stringify(e.payload, null, 2)}</pre>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
