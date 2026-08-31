import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/lib/auth-store';

export interface LoginPageProps {
  onNavigate: (path: string) => void;
}

export const LoginPage: React.FC<LoginPageProps> = ({ onNavigate }) => {
  const { login, isLoading } = useAuth();
  const [slug, setSlug] = useState('');
  const [rzpKeyId, setRzpKeyId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
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
    <div className="auth-page">
      <div className="auth-shell">
        <main className="auth-form-side">
          <div className="auth-form-wrap auth-reveal">
            <button type="button" onClick={() => onNavigate('/')} className="auth-back">
              <ArrowLeft className="h-4 w-4" /> Home
            </button>
            <div className="mt-9"><span className="auth-brand">pimp</span></div>
            <div className="mt-12">
              <h1 className="text-3xl font-semibold tracking-[-0.055em] text-slate-50">Merchant Sign In</h1>
              <p className="mt-3 text-sm text-slate-400">Access your governed commerce workspace.</p>
            </div>

            <form onSubmit={handleSubmit} className="mt-8 space-y-5">
              {error && <div className="flex items-center gap-2 rounded-md border border-rose-400/25 bg-rose-400/10 p-3 text-xs font-medium text-rose-200"><AlertCircle className="h-4 w-4 shrink-0" />{error}</div>}
              <Input className="auth-input" label="Store Slug" placeholder="e.g. acme-shoes" value={slug} onChange={(event) => setSlug(event.target.value)} required />
              <Input className="auth-input" label="Razorpay Key ID (Optional)" placeholder="rzp_test_..." value={rzpKeyId} onChange={(event) => setRzpKeyId(event.target.value)} />
              <Button type="button" onClick={handleDemoFill} variant="ghost" size="sm" className="w-full text-xs text-slate-400 hover:bg-slate-800 hover:text-slate-100">Quick fill demo store (acme-shoes)</Button>
              <Button type="submit" className="mt-2 w-full rounded-md bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200" isLoading={isLoading}>Sign In <ArrowRight className="h-4 w-4" /></Button>
            </form>
            <p className="mt-8 text-center text-sm text-slate-400">Don&apos;t have a store? <button type="button" onClick={() => onNavigate('/signup')} className="font-medium text-slate-100 hover:underline">Sign Up Now</button></p>
          </div>
        </main>
        <aside className="auth-visual-side" aria-hidden="true"><div className="auth-dot-field" /><div className="auth-visual-copy">Operate commerce with <span>certainty.</span></div></aside>
      </div>
    </div>
  );
};
