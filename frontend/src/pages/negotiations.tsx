import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardContent } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { QuoteDetail } from '@/types/portal';
import { formatPaiseToINR, formatRelativeTime } from '@/lib/utils';
import { MessageSquareDiff, ArrowRight } from 'lucide-react';

export const NegotiationsPage: React.FC = () => {
  const [quotes, setQuotes] = useState<QuoteDetail[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);

  useEffect(() => {
    const fetchNegotiations = async () => {
      try {
        const data = await api.listQuotes();
        setQuotes(data.filter((q: QuoteDetail) => q.discount_paise > 0 || q.status === 'NEGOTIATING'));
      } finally {
        setIsLoading(false);
      }
    };
    fetchNegotiations();
  }, []);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Negotiations Trace</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Multi-round buyer agent price negotiations bounded by the 3-round limit and floor price.
        </p>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2].map((i) => <Skeleton key={i} className="h-28 w-full" />)}
        </div>
      ) : quotes.length === 0 ? (
        <EmptyState
          icon={<MessageSquareDiff className="h-10 w-10" />}
          title="No active negotiations"
          description="Negotiations initiated by external AI buyers will appear here with requested terms."
        />
      ) : (
        <div className="space-y-4">
          {quotes.map((q: QuoteDetail) => (
            <Card key={q.id} className="border-border bg-card/80">
              <CardHeader className="pb-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-mono text-xs text-primary font-semibold">{q.id.slice(0, 8)}...</span>
                    <Badge variant={q.status === 'ACCEPTED' ? 'success' : 'warning'} className="text-[9px]">
                      {q.status}
                    </Badge>
                  </div>
                  <span className="text-xs text-muted-foreground">{formatRelativeTime(q.created_at)}</span>
                </div>
              </CardHeader>
              <CardContent className="border-t border-border pt-3 text-xs space-y-2">
                <div className="flex items-center justify-between bg-muted/20 p-3 rounded">
                  <div>
                    <span className="text-muted-foreground">Catalog Subtotal:</span>
                    <p className="font-bold text-foreground">{formatPaiseToINR(q.subtotal_paise)}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <span className="text-muted-foreground">Granted Discount:</span>
                    <p className="font-bold text-amber-400">-{formatPaiseToINR(q.discount_paise)}</p>
                  </div>
                  <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  <div>
                    <span className="text-muted-foreground">Final Settlement:</span>
                    <p className="font-bold text-emerald-400">{formatPaiseToINR(q.total_paise)}</p>
                  </div>
                </div>
                {q.discount_reason && (
                  <p className="text-[11px] text-muted-foreground italic">Policy Verdict: {q.discount_reason}</p>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
};
