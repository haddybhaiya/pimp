import React, { useEffect, useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import { EmptyState } from '@/components/ui/empty-state';
import { Skeleton } from '@/components/ui/skeleton';
import { api } from '@/lib/api-client';
import { ProductItem } from '@/types/portal';
import { formatPaiseToINR } from '@/lib/utils';
import { Package, Plus, AlertCircle, CheckCircle2 } from 'lucide-react';

export const CatalogPage: React.FC = () => {
  const [products, setProducts] = useState<ProductItem[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Add Product Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [sku, setSku] = useState('');
  const [title, setTitle] = useState('');
  const [category, setCategory] = useState('FOOTWEAR');
  const [basePriceRupees, setBasePriceRupees] = useState(4999);
  const [floorPriceRupees, setFloorPriceRupees] = useState(3999);
  const [initialStock, setInitialStock] = useState(25);
  const [formError, setFormError] = useState<string | null>(null);

  const fetchProducts = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const data = await api.listProducts();
      setProducts(data);
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Failed to load catalog products.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  const handleCreateProduct = async (e: React.FormEvent) => {
    e.preventDefault();
    if (floorPriceRupees > basePriceRupees) {
      setFormError('Floor price cannot exceed base price.');
      return;
    }
    setFormError(null);
    setIsSubmitting(true);
    try {
      await api.createProduct({
        sku: sku.trim(),
        title: title.trim(),
        category: category.trim(),
        base_price_paise: Math.round(basePriceRupees * 100),
        floor_price_paise: Math.round(floorPriceRupees * 100),
        initial_stock: initialStock,
      });
      setIsModalOpen(false);
      setSku('');
      setTitle('');
      fetchProducts();
    } catch (err: unknown) {
      setFormError(err instanceof Error ? err.message : 'Failed to create product.');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl font-bold tracking-tight">Catalog & Products</h2>
          <p className="text-xs text-muted-foreground mt-0.5">
            Authoritative catalog with deterministic floor prices and inventory binding.
          </p>
        </div>
        <Button onClick={() => setIsModalOpen(true)} size="sm" className="gap-1.5">
          <Plus className="h-4 w-4" /> Add Product
        </Button>
      </div>

      {error && (
        <div className="flex items-center gap-2 rounded-md bg-destructive/15 p-3 text-xs text-destructive font-medium">
          <AlertCircle className="h-4 w-4 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3].map((i) => (
            <Skeleton key={i} className="h-44 w-full" />
          ))}
        </div>
      ) : products.length === 0 ? (
        <EmptyState
          icon={<Package className="h-10 w-10" />}
          title="No products in catalog"
          description="Create your first catalog item to enable AI buyer discovery and automated pricing."
          actionLabel="Add Product"
          onAction={() => setIsModalOpen(true)}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {products.map((p) => (
            <Card key={p.id} className="border-border bg-card/80">
              <CardHeader className="pb-3">
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <Badge variant="outline" className="text-[10px] mb-1 font-mono">{p.sku}</Badge>
                    <CardTitle className="text-base font-semibold">{p.title}</CardTitle>
                  </div>
                  <Badge variant={p.is_active ? 'success' : 'secondary'} className="text-[10px]">
                    {p.is_active ? 'ACTIVE' : 'INACTIVE'}
                  </Badge>
                </div>
                <CardDescription className="text-xs line-clamp-2">{p.description || p.category}</CardDescription>
              </CardHeader>
              <CardContent className="space-y-2 text-xs border-t border-border pt-3">
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Base Price:</span>
                  <span className="font-semibold text-foreground">{formatPaiseToINR(p.base_price_paise)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Floor Guard:</span>
                  <span className="font-mono text-emerald-400 font-medium">{formatPaiseToINR(p.floor_price_paise)}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-muted-foreground">Available Stock:</span>
                  <span className={`font-semibold ${p.available_stock <= 2 ? 'text-amber-400' : 'text-foreground'}`}>
                    {p.available_stock} units
                  </span>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Add Product Modal */}
      <Dialog
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        title="Add New Catalog Product"
        description="Configure product details, base price, and guaranteed floor price margin."
      >
        <form onSubmit={handleCreateProduct} className="space-y-3.5">
          {formError && (
            <div className="flex items-center gap-2 rounded-md bg-destructive/15 p-2.5 text-xs text-destructive font-medium">
              <AlertCircle className="h-4 w-4 shrink-0" />
              <span>{formError}</span>
            </div>
          )}

          <div className="grid grid-cols-2 gap-3">
            <Input label="SKU" placeholder="RUN-AIR-01" value={sku} onChange={(e) => setSku(e.target.value)} required />
            <Input label="Category" placeholder="FOOTWEAR" value={category} onChange={(e) => setCategory(e.target.value)} required />
          </div>

          <Input label="Product Title" placeholder="Air Velocity Running Shoes" value={title} onChange={(e) => setTitle(e.target.value)} required />

          <div className="grid grid-cols-2 gap-3">
            <Input
              label="Base Price (₹)"
              type="number"
              value={basePriceRupees}
              onChange={(e) => setBasePriceRupees(parseFloat(e.target.value) || 0)}
              min={1}
              required
            />
            <Input
              label="Floor Price (₹)"
              type="number"
              value={floorPriceRupees}
              onChange={(e) => setFloorPriceRupees(parseFloat(e.target.value) || 0)}
              min={1}
              helperText="Must be <= Base Price"
              required
            />
          </div>

          <Input
            label="Initial Stock Units"
            type="number"
            value={initialStock}
            onChange={(e) => setInitialStock(parseInt(e.target.value) || 0)}
            min={0}
            required
          />

          <div className="flex justify-end gap-2 pt-3">
            <Button type="button" onClick={() => setIsModalOpen(false)} variant="outline" size="sm">
              Cancel
            </Button>
            <Button type="submit" isLoading={isSubmitting} size="sm">
              <CheckCircle2 className="h-4 w-4 mr-1" /> Save Product
            </Button>
          </div>
        </form>
      </Dialog>
    </div>
  );
};
