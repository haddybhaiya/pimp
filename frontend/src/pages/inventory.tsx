import React, { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { InventoryItem } from '@/types/portal';
import { Boxes, Edit3, AlertTriangle, CheckCircle2 } from 'lucide-react';

export const InventoryPage: React.FC = () => {
  const [inventory, setInventory] = useState<InventoryItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [selectedItem, setSelectedItem] = useState<InventoryItem | null>(null);
  const [delta, setDelta] = useState<number>(0);
  const [reason, setReason] = useState<string>('RESTOCK');
  const [isAdjusting, setIsAdjusting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [loadError, setLoadError] = useState<string | null>(null);

  const fetchInventory = async () => {
    setIsLoading(true);
    try {
      const data = await api.listInventory();
      setInventory(data);
      setLoadError(null);
    } catch (err: unknown) {
      setLoadError(err instanceof Error ? err.message : 'Unable to load inventory.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchInventory();
  }, []);

  const handleAdjust = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedItem) return;
    setIsAdjusting(true);
    setError(null);
    try {
      await api.adjustInventory({
        sku: selectedItem.sku,
        quantity_delta: delta,
        reason,
      });
      setSelectedItem(null);
      setDelta(0);
      fetchInventory();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Adjustment failed.');
    } finally {
      setIsAdjusting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-xl font-bold tracking-tight">Inventory Stocks</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Optimistic locking and atomic stock reservations for agent checkout.
          </p>
        </div>
      </div>

      {isLoading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => <Skeleton key={i} className="h-16 w-full" />)}
        </div>
      ) : loadError ? (
        <EmptyState icon={<Boxes className="h-10 w-10" />} title="Inventory unavailable" description={loadError} />
      ) : inventory.length === 0 ? (
        <EmptyState
          icon={<Boxes className="h-10 w-10" />}
          title="No inventory records found"
          description="Create catalog products to establish authoritative inventory stock tracking."
        />
      ) : (
        <div className="rounded-lg border border-border bg-card overflow-hidden">
          <table className="w-full text-xs text-left">
            <thead className="bg-muted/40 text-muted-foreground uppercase text-[10px] border-b border-border">
              <tr>
                <th className="p-3.5">SKU</th>
                <th className="p-3.5">Product Title</th>
                <th className="p-3.5 text-right">Available</th>
                <th className="p-3.5 text-right">Reserved</th>
                <th className="p-3.5 text-right">Safety Threshold</th>
                <th className="p-3.5 text-center">Status</th>
                <th className="p-3.5 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y border-border font-medium">
              {inventory.map((item) => {
                const isLow = item.available_quantity <= item.safety_threshold;
                return (
                  <tr key={item.id} className="hover:bg-accent/30 transition-colors">
                    <td className="p-3.5 font-mono text-primary">{item.sku}</td>
                    <td className="p-3.5 font-semibold text-foreground">{item.product_title}</td>
                    <td className="p-3.5 text-right font-bold text-foreground">{item.available_quantity}</td>
                    <td className="p-3.5 text-right text-muted-foreground">{item.reserved_quantity}</td>
                    <td className="p-3.5 text-right text-muted-foreground">{item.safety_threshold}</td>
                    <td className="p-3.5 text-center">
                      <Badge variant={isLow ? 'warning' : 'success'} className="text-[9px]">
                        {isLow ? 'LOW STOCK' : 'IN STOCK'}
                      </Badge>
                    </td>
                    <td className="p-3.5 text-right">
                      <Button onClick={() => { setSelectedItem(item); setDelta(0); }} variant="outline" size="sm" className="h-7 text-xs gap-1">
                        <Edit3 className="h-3 w-3" /> Adjust
                      </Button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Adjust Inventory Modal */}
      <Dialog
        isOpen={!!selectedItem}
        onClose={() => setSelectedItem(null)}
        title={`Adjust Stock for ${selectedItem?.sku}`}
        description="Add or remove available stock units with server-authoritative optimistic locking."
      >
        <form onSubmit={handleAdjust} className="space-y-4">
          {error && (
            <div className="flex items-center gap-2 rounded bg-destructive/15 p-2.5 text-xs text-destructive">
              <AlertTriangle className="h-4 w-4 shrink-0" />
              <span>{error}</span>
            </div>
          )}

          <div className="rounded bg-muted/40 p-3 text-xs space-y-1">
            <div className="flex justify-between">
              <span className="text-muted-foreground">Current Available:</span>
              <span className="font-bold text-foreground">{selectedItem?.available_quantity} units</span>
            </div>
            <div className="flex justify-between">
              <span className="text-muted-foreground">Projected New Stock:</span>
              <span className="font-bold text-primary">{(selectedItem?.available_quantity || 0) + delta} units</span>
            </div>
          </div>

          <Input
            label="Quantity Delta (+ to add, - to subtract)"
            type="number"
            value={delta}
            onChange={(e) => setDelta(parseInt(e.target.value) || 0)}
            required
          />

          <Input
            label="Reason"
            value={reason}
            onChange={(e) => setReason(e.target.value)}
            placeholder="RESTOCK / CORRECTION"
            required
          />

          <div className="flex justify-end gap-2 pt-2">
            <Button type="button" onClick={() => setSelectedItem(null)} variant="outline" size="sm">
              Cancel
            </Button>
            <Button type="submit" isLoading={isAdjusting} size="sm">
              <CheckCircle2 className="h-4 w-4 mr-1" /> Commit Adjustment
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
