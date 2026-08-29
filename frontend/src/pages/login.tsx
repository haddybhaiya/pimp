import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { useAuth } from '@/lib/auth-store';
import { ShieldCheck, AlertCircle } from 'lucide-react';

export interface LoginPageProps {
  onNavigate: (path: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onNavigate }) => {
  const { login, isLoading } = useAuth();
  const [slug, setSlug] = useState('');
  const [rzpKeyId, setRzpKeyId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!slug) {
      setError('Please enter your merchant slug.');
      return;
    }
    setError(null);
    try {
      await login({ slug: slug.trim().toLowerCase(), rzpKeyId: rzpKeyId.trim() || undefined });
      onNavigate('/dashboard');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Invalid credentials or store not found.');
    }
  };

  const handleDemoFill = () => {
    setSlug('acme-shoes');
    setRzpKeyId('rzp_test_acme123');
  };

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md border-border/80 bg-card/80 backdrop-blur-md shadow-xl">
        <CardHeader className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground mb-2">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <CardTitle className="text-2xl font-bold">Merchant Sign In</CardTitle>
          <CardDescription>Enter your store slug to access your autonomous control plane.</CardDescription>
        </CardHeader>

        <form onSubmit={handleSubmit}>
          <CardContent className="space-y-4">
            {error && (
              <div className="flex items-center gap-2 rounded-md bg-destructive/15 p-3 text-xs text-destructive font-medium">
                <AlertCircle className="h-4 w-4 shrink-0" />
                <span>{error}</span>
              </div>
            )}

            <Input
              label="Store Slug"
              placeholder="e.g. acme-shoes"
              value={slug}
              onChange={(e) => setSlug(e.target.value)}
              required
            />

            <Input
              label="Razorpay Key ID (Optional)"
              placeholder="rzp_test_..."
              value={rzpKeyId}
              onChange={(e) => setRzpKeyId(e.target.value)}
            />

            <div className="pt-2">
              <Button type="button" onClick={handleDemoFill} variant="ghost" size="sm" className="w-full text-xs text-muted-foreground">
                ⚡ Quick Fill Demo Store (acme-shoes)
              </Button>
            </div>
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Sign In
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              Don't have a store yet?{' '}
              <button type="button" onClick={() => onNavigate('/signup')} className="text-primary hover:underline font-medium">
                Register Store
              </button>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};
