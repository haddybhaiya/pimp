import React, { useEffect, useState } from 'react';
import { api } from '@/lib/api-client';
import {
  DiscoverabilityStatusResponse,
  DiscoverabilityState,
} from '@/types/portal';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
import {
  Globe,
  Lock,
  PauseCircle,
  AlertTriangle,
  Eye,
  CheckCircle2,
  Tag,
  MapPin,
  ShieldCheck,
  TrendingUp,
  Search,
  Activity,
  ArrowUpRight,
} from 'lucide-react';

export const DiscoverabilityPage: React.FC = () => {
  const [data, setData] = useState<DiscoverabilityStatusResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);

  // Form State
  const [customTags, setCustomTags] = useState<string>('');
  const [customDesc, setCustomDesc] = useState<string>('');
  const [deliveryRegions, setDeliveryRegions] = useState<string>('');

  const loadData = async () => {
    try {
      setIsLoading(true);
      setError(null);
      const res = await api.getDiscoverabilityStatus();
      setData(res);
      setCustomTags(res.profile?.discovery_tags?.join(', ') || '');
      setCustomDesc(res.profile?.description || '');
      setDeliveryRegions(res.profile?.safe_delivery_regions?.join(', ') || '');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load discoverability status');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  const handleStateChange = async (targetState: DiscoverabilityState) => {
    try {
      setIsSaving(true);
      setError(null);
      const updated = await api.updateDiscoverability({
        discoverability_state: targetState,
      });
      setData(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to update discoverability state');
    } finally {
      setIsSaving(false);
    }
  };

  const handleSaveMetadata = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsSaving(true);
      setError(null);
      const tagsList = customTags
        .split(',')
        .map((t) => t.trim())
        .filter(Boolean);
      const regionsList = deliveryRegions
        .split(',')
        .map((r) => r.trim().toUpperCase())
        .filter(Boolean);

      const updated = await api.updateDiscoverability({
        custom_tags: tagsList,
        custom_description: customDesc.trim() || undefined,
        delivery_regions: regionsList.length > 0 ? regionsList : undefined,
      });
      setData(updated);
      setSaveSuccess(true);
      setTimeout(() => setSaveSuccess(false), 3000);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to save metadata');
    } finally {
      setIsSaving(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-64 items-center justify-center text-text-muted">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  const currentState = data?.discoverability_state || 'PRIVATE';
  const metrics = data?.metrics || {};

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 border-b border-border/40 pb-6">
        <div>
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight text-text-primary">
              Discovery Network
            </h1>
            <Badge
              variant={
                currentState === 'DISCOVERABLE'
                  ? 'success'
                  : currentState === 'PAUSED'
                  ? 'warning'
                  : currentState === 'SUSPENDED'
                  ? 'destructive'
                  : 'secondary'
              }
              className="text-xs uppercase font-mono"
            >
              {currentState}
            </Badge>
          </div>
          <p className="text-sm text-text-muted mt-1">
            Governed discoverability, safe capability graph, and external AI buyer entry points.
          </p>
        </div>

        {/* State Transition Action Buttons */}
        <div className="flex items-center gap-2">
          {currentState !== 'DISCOVERABLE' && (
            <Button
              variant="primary"
              size="sm"
              disabled={isSaving}
              onClick={() => handleStateChange('DISCOVERABLE')}
              className="gap-1.5"
            >
              <Globe className="h-4 w-4" />
              Make Discoverable
            </Button>
          )}

          {currentState === 'DISCOVERABLE' && (
            <Button
              variant="outline"
              size="sm"
              disabled={isSaving}
              onClick={() => handleStateChange('PAUSED')}
              className="gap-1.5 text-amber-400 border-amber-400/30 hover:bg-amber-400/10"
            >
              <PauseCircle className="h-4 w-4" />
              Pause Listing
            </Button>
          )}

          {currentState !== 'PRIVATE' && (
            <Button
              variant="outline"
              size="sm"
              disabled={isSaving}
              onClick={() => handleStateChange('PRIVATE')}
              className="gap-1.5 text-text-muted hover:text-text-primary"
            >
              <Lock className="h-4 w-4" />
              Set Private
            </Button>
          )}
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-rose-500/30 bg-rose-500/10 p-4 text-sm text-rose-300 flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {saveSuccess && (
        <div className="rounded-md border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300 flex items-center gap-3">
          <CheckCircle2 className="h-5 w-5 shrink-0" />
          <span>Discoverability configuration updated successfully.</span>
        </div>
      )}

      {/* Discovery Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
        <Card className="bg-card/40 border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-text-muted">SEARCHES</span>
              <Search className="h-4 w-4 text-sky-400" />
            </div>
            <div className="text-2xl font-bold text-text-primary mt-2">
              {metrics['SEARCH_RECEIVED'] || 0}
            </div>
            <p className="text-[11px] text-text-muted mt-0.5">Queries evaluated</p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-text-muted">IMPRESSIONS</span>
              <Eye className="h-4 w-4 text-emerald-400" />
            </div>
            <div className="text-2xl font-bold text-text-primary mt-2">
              {metrics['MERCHANT_RETURNED'] || 0}
            </div>
            <p className="text-[11px] text-text-muted mt-0.5">Appeared in results</p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-text-muted">STORE CLICKS</span>
              <Activity className="h-4 w-4 text-purple-400" />
            </div>
            <div className="text-2xl font-bold text-text-primary mt-2">
              {metrics['MERCHANT_SELECTED'] || 0}
            </div>
            <p className="text-[11px] text-text-muted mt-0.5">Profile viewed</p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-text-muted">PRODUCT CLICKS</span>
              <TrendingUp className="h-4 w-4 text-amber-400" />
            </div>
            <div className="text-2xl font-bold text-text-primary mt-2">
              {metrics['PRODUCT_SELECTED'] || 0}
            </div>
            <p className="text-[11px] text-text-muted mt-0.5">Product selected</p>
          </CardContent>
        </Card>

        <Card className="bg-card/40 border-border/50">
          <CardContent className="p-4">
            <div className="flex items-center justify-between">
              <span className="text-xs font-mono text-text-muted">HANDOFFS</span>
              <ArrowUpRight className="h-4 w-4 text-brand-bright" />
            </div>
            <div className="text-2xl font-bold text-text-primary mt-2">
              {metrics['HANDOFF_INITIATED'] || 0}
            </div>
            <p className="text-[11px] text-text-muted mt-0.5">Sessions initiated</p>
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Metadata Editor */}
        <div className="lg:col-span-6 space-y-6">
          <Card className="border-border/60 bg-card/60">
            <CardHeader>
              <CardTitle className="text-base flex items-center gap-2">
                <Tag className="h-4 w-4 text-brand-bright" />
                Discovery Metadata Editor
              </CardTitle>
              <CardDescription>
                Configure public keywords, delivery regions, and store summary.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <form onSubmit={handleSaveMetadata} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-text-muted">
                    Custom Discovery Tags (comma-separated)
                  </label>
                  <Input
                    value={customTags}
                    onChange={(e) => setCustomTags(e.target.value)}
                    placeholder="apparel, running shoes, footwear, outdoor"
                    className="font-mono text-xs"
                  />
                  <p className="text-[11px] text-text-muted">
                    Keywords used by external AI buyer search algorithms (max 20 tags).
                  </p>
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-text-muted">
                    Store Summary Description
                  </label>
                  <textarea
                    value={customDesc}
                    onChange={(e) => setCustomDesc(e.target.value)}
                    placeholder="Official agent-ready store offering premium running gear..."
                    rows={3}
                    maxLength={1000}
                    className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-xs placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 transition-colors"
                  />
                </div>

                <div className="space-y-1.5">
                  <label className="text-xs font-medium text-text-muted">
                    Supported Delivery Regions (comma-separated)
                  </label>
                  <Input
                    value={deliveryRegions}
                    onChange={(e) => setDeliveryRegions(e.target.value)}
                    placeholder="INDIA, IN-MH, IN-DL, IN-KA"
                    className="font-mono text-xs"
                  />
                  <p className="text-[11px] text-text-muted">
                    State or regional codes for delivery compatibility matching.
                  </p>
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <span className="text-[11px] text-text-muted font-mono">
                    Profile v{data?.profile_version} • Updated{' '}
                    {data?.updated_at ? new Date(data.updated_at).toLocaleDateString() : 'N/A'}
                  </span>
                  <Button type="submit" variant="primary" size="sm" disabled={isSaving}>
                    {isSaving ? 'Saving...' : 'Save Metadata'}
                  </Button>
                </div>
              </form>
            </CardContent>
          </Card>

          {/* Supported Protocols Card */}
          <Card className="border-border/60 bg-card/60">
            <CardHeader className="pb-3">
              <CardTitle className="text-base flex items-center gap-2">
                <ShieldCheck className="h-4 w-4 text-emerald-400" />
                Supported Discovery Protocols
              </CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div className="flex items-center justify-between p-3 rounded-md bg-white/[0.03] border border-border/40">
                <div>
                  <span className="text-xs font-semibold text-text-primary block">
                    Agent Commerce Protocol (ACP)
                  </span>
                  <span className="text-[11px] text-text-muted">
                    Standard AI buyer JSON message protocol
                  </span>
                </div>
                <Badge variant="outline" className="font-mono text-[10px]">
                  ACP/1.0
                </Badge>
              </div>

              <div className="flex items-center justify-between p-3 rounded-md bg-white/[0.03] border border-border/40">
                <div>
                  <span className="text-xs font-semibold text-text-primary block">
                    Canonical REST API
                  </span>
                  <span className="text-[11px] text-text-muted">
                    Standard HTTPS endpoints with bounded schemas
                  </span>
                </div>
                <Badge variant="outline" className="font-mono text-[10px]">
                  REST/1.0
                </Badge>
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Safe Public Profile Preview */}
        <div className="lg:col-span-6 space-y-6">
          <Card className="border-border/60 bg-card/60">
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle className="text-base flex items-center gap-2">
                  <Eye className="h-4 w-4 text-sky-400" />
                  Public Profile Preview
                </CardTitle>
                <span className="text-[11px] font-mono text-emerald-400 bg-emerald-400/10 px-2 py-0.5 rounded">
                  SAFE ALLOWLIST
                </span>
              </div>
              <CardDescription>
                Exact representation visible to external AI buyers and aggregators.
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {data?.profile ? (
                <div className="space-y-4 p-4 rounded-lg bg-black/30 border border-white/10">
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="font-semibold text-sm text-text-primary">
                        {data.profile.display_name}
                      </h3>
                      <span className="text-xs font-mono text-text-muted">
                        slug: {data.profile.slug}
                      </span>
                    </div>
                    <Badge variant="outline" className="text-xs font-mono">
                      {data.profile.category || 'General'}
                    </Badge>
                  </div>

                  <p className="text-xs text-text-muted leading-relaxed">
                    {data.profile.description}
                  </p>

                  <div className="space-y-2">
                    <span className="text-[11px] font-mono text-text-muted uppercase block">
                      Discovery Tags
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {data.profile.discovery_tags.map((tag) => (
                        <span
                          key={tag}
                          className="px-2 py-0.5 rounded bg-white/[0.05] border border-white/10 text-[11px] font-mono text-text-secondary"
                        >
                          #{tag}
                        </span>
                      ))}
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-3 pt-2 border-t border-white/[0.07]">
                    <div>
                      <span className="text-[10px] uppercase font-mono text-text-muted block">
                        Non-binding Price Range
                      </span>
                      <span className="text-xs font-mono text-text-primary font-semibold">
                        ₹{(data.profile.price_range_paise.min / 100).toFixed(2)} – ₹
                        {(data.profile.price_range_paise.max / 100).toFixed(2)}
                      </span>
                    </div>

                    <div>
                      <span className="text-[10px] uppercase font-mono text-text-muted block">
                        Supported Delivery
                      </span>
                      <span className="text-xs font-mono text-text-primary flex items-center gap-1">
                        <MapPin className="h-3 w-3 text-amber-400" />
                        {data.profile.safe_delivery_regions.join(', ')}
                      </span>
                    </div>
                  </div>

                  <div className="pt-2 border-t border-white/[0.07]">
                    <span className="text-[10px] uppercase font-mono text-text-muted block mb-1.5">
                      Verified Trust Signals
                    </span>
                    <div className="flex flex-wrap gap-1.5">
                      {data.profile.verified_trust_signals.map((sig) => (
                        <span
                          key={sig}
                          className="px-1.5 py-0.5 rounded bg-emerald-500/10 border border-emerald-500/20 text-[10px] font-mono text-emerald-300"
                        >
                          ✓ {sig}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <div className="p-8 text-center border border-dashed border-white/10 rounded-lg text-text-muted text-xs">
                  Store is currently PRIVATE or PAUSED. No public discovery profile is active.
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>

      {/* Public Capability Graph Table */}
      <Card className="border-border/60 bg-card/60">
        <CardHeader>
          <div className="flex items-center justify-between">
            <CardTitle className="text-base flex items-center gap-2">
              <ShieldCheck className="h-4 w-4 text-emerald-400" />
              Public Capability Graph
            </CardTitle>
            <span className="text-[11px] font-mono text-text-muted">
              DESCRIPTIVE ONLY • ZERO PRIVILEGE GRANT
            </span>
          </div>
          <CardDescription>
            Exposed canonical capabilities discoverable by external buyer reasoning engines.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs border-collapse">
              <thead>
                <tr className="border-b border-border/50 text-text-muted font-mono">
                  <th className="py-2.5 px-3">CAPABILITY</th>
                  <th className="py-2.5 px-3">CLASSIFICATION</th>
                  <th className="py-2.5 px-3">SIDE EFFECTS</th>
                  <th className="py-2.5 px-3">MONETARY IMPACT</th>
                  <th className="py-2.5 px-3">APPROVAL REQ</th>
                  <th className="py-2.5 px-3">STATUS</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-border/30">
                {data?.public_capability_graph.map((cap) => (
                  <tr key={cap.name} className="hover:bg-white/[0.02]">
                    <td className="py-2.5 px-3 font-mono font-medium text-text-primary">
                      {cap.name}
                    </td>
                    <td className="py-2.5 px-3 font-mono">
                      <span
                        className={`px-1.5 py-0.5 rounded text-[10px] ${
                          cap.classification === 'PRIVILEGED_FINANCIAL'
                            ? 'bg-rose-500/10 text-rose-300 border border-rose-500/20'
                            : cap.classification === 'TRANSIENT_STATE'
                            ? 'bg-amber-500/10 text-amber-300 border border-amber-500/20'
                            : 'bg-sky-500/10 text-sky-300 border border-sky-500/20'
                        }`}
                      >
                        {cap.classification}
                      </span>
                    </td>
                    <td className="py-2.5 px-3 text-text-muted">
                      {cap.side_effect_classification}
                    </td>
                    <td className="py-2.5 px-3 text-text-muted">
                      {cap.monetary_impact_classification}
                    </td>
                    <td className="py-2.5 px-3 font-mono text-text-muted">
                      {cap.approval_requirement}
                    </td>
                    <td className="py-2.5 px-3 font-mono">
                      <span className="text-emerald-400 font-medium">
                        {cap.coarse_availability}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};
