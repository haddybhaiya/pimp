import React, { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';
import { useAuth } from '@/lib/auth-store';
import { ShieldCheck, AlertCircle } from 'lucide-react';

export interface SignupPageProps {
  onNavigate: (path: string) => void;
}

export const SignupPage: React.FC<SignupPageProps> = ({ onNavigate }) => {
  const { signup, isLoading } = useAuth();
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [email, setEmail] = useState('');
  const [rzpKeyId, setRzpKeyId] = useState('rzp_test_key_123');
  const [error, setError] = useState<string | null>(null);

  const handleNameChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const val = e.target.value;
    setName(val);
    if (!slug || slug === name.toLowerCase().replace(/[^a-z0-9]+/g, '-')) {
      setSlug(val.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!name || !slug || !email) {
      setError('Please fill in all required fields.');
      return;
    }
    setError(null);
    try {
      await signup({
        name: name.trim(),
        slug: slug.trim().toLowerCase(),
        email: email.trim(),
        rzpKeyId: rzpKeyId.trim() || 'rzp_test_placeholder',
      });
      onNavigate('/onboarding');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed.');
    }
  };

  return (
    <div className="flex min-h-[calc(100vh-8rem)] items-center justify-center px-4 py-12">
      <Card className="w-full max-w-md border-border/80 bg-card/80 backdrop-blur-md shadow-xl">
        <CardHeader className="text-center">
          <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-xl bg-primary text-primary-foreground mb-2">
            <ShieldCheck className="h-6 w-6" />
          </div>
          <CardTitle className="text-2xl font-bold">Register Merchant</CardTitle>
          <CardDescription>Set up your autonomous commerce store on Razorpay in seconds.</CardDescription>
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
              label="Store / Business Name"
              placeholder="Apex Athletic"
              value={name}
              onChange={handleNameChange}
              required
            />

            <Input
              label="Store Slug"
              placeholder="apex-athletic"
              value={slug}
              onChange={(e) => setSlug(e.target.value.toLowerCase())}
              helperText="Unique identifier for AI buyers"
              required
            />

            <Input
              label="Admin Email"
              type="email"
              placeholder="admin@apex-athletic.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
            />

            <Input
              label="Razorpay Test Key ID"
              placeholder="rzp_test_..."
              value={rzpKeyId}
              onChange={(e) => setRzpKeyId(e.target.value)}
              helperText="Test mode API key"
            />
          </CardContent>

          <CardFooter className="flex flex-col gap-3">
            <Button type="submit" className="w-full" isLoading={isLoading}>
              Create Store & Continue
            </Button>
            <p className="text-xs text-center text-muted-foreground">
              Already registered?{' '}
              <button type="button" onClick={() => onNavigate('/login')} className="text-primary hover:underline font-medium">
                Sign In
              </button>
            </p>
          </CardFooter>
        </form>
      </Card>
    </div>
  );
};
