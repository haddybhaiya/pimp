import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/lib/auth-store';
import { Check, Copy } from 'lucide-react';

export const SettingsPage: React.FC = () => {
  const { merchant } = useAuth();
  const [copiedKey, setCopiedKey] = useState<string | null>(null);

  const copyToClipboard = (text: string, keyName: string) => {
    navigator.clipboard.writeText(text);
    setCopiedKey(keyName);
    setTimeout(() => setCopiedKey(null), 2000);
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Merchant Settings</h2>
        <p className="text-xs text-muted-foreground mt-0.5">
          Store identity, Razorpay integration keys, and public ACP agent endpoint URLs.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="border-border bg-card/90">
          <CardHeader>
            <CardTitle className="text-base">Store Identity</CardTitle>
            <CardDescription>Authoritative merchant profile configured in ARM.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3 text-xs">
            <Input label="Store Name" value={merchant?.name || ''} disabled />
            <Input label="Store Slug" value={merchant?.slug || ''} disabled />
            <Input label="Operating Currency" value={merchant?.currency || 'INR'} disabled />
            <Input label="Merchant UUID" value={merchant?.merchantId || ''} disabled />
          </CardContent>
        </Card>

        <Card className="border-border bg-card/90">
          <CardHeader>
            <CardTitle className="text-base">Agent Commerce Protocol (ACP) Endpoints</CardTitle>
            <CardDescription>Public endpoints exposed to external AI buyer agents.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4 text-xs">
            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1">ACP Wire Endpoint</label>
              <div className="flex gap-2">
                <input
                  readOnly
                  value="https://api.agentready.merchant/api/v1/protocol/acp"
                  className="flex h-9 w-full rounded border border-input bg-muted/40 px-3 font-mono text-xs text-muted-foreground"
                />
                <Button onClick={() => copyToClipboard('https://api.agentready.merchant/api/v1/protocol/acp', 'acp')} variant="outline" size="sm">
                  {copiedKey === 'acp' ? <Check className="h-4 w-4 text-emerald-400" /> : <Copy className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            <div>
              <label className="block text-xs font-medium text-muted-foreground mb-1">Razorpay Key Identifier</label>
              <input
                readOnly
                value={merchant?.rzpKeyId || 'rzp_test_placeholder'}
                className="flex h-9 w-full rounded border border-input bg-muted/40 px-3 font-mono text-xs text-muted-foreground"
              />
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};
