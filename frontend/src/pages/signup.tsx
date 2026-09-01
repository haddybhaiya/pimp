import React, { useState } from 'react';
import { ArrowLeft, ArrowRight, AlertCircle } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { useAuth } from '@/lib/auth-store';
import { requireInsforge } from '@/lib/insforge';

export interface SignupPageProps {
  onNavigate: (path: string) => void;
}

export const SignupPage: React.FC<SignupPageProps> = ({ onNavigate }) => {
  const { signup, isLoading } = useAuth();
  const [name, setName] = useState('');
  const [slug, setSlug] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [verificationCode, setVerificationCode] = useState('');
  const [awaitingVerification, setAwaitingVerification] = useState(false);
  const [rzpKeyId, setRzpKeyId] = useState('');
  const [error, setError] = useState<string | null>(null);

  const handleNameChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const value = event.target.value;
    setName(value);
    if (!slug || slug === name.toLowerCase().replace(/[^a-z0-9]+/g, '-')) {
      setSlug(value.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, ''));
    }
  };

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!name || !slug || !email || !password) {
      setError('Please fill in all required fields.');
      return;
    }
    setError(null);
    try {
      const auth = requireInsforge();
      const { data, error: authError } = await auth.auth.signUp({
        email: email.trim(), password, name: name.trim(),
      });
      if (authError) throw new Error(authError.message);
      if (data?.requireEmailVerification) {
        setAwaitingVerification(true);
        return;
      }
      if (!data?.accessToken) throw new Error('Account creation did not establish a session.');
      await signup({ name: name.trim(), slug: slug.trim().toLowerCase(), email: email.trim(), rzpKeyId: rzpKeyId.trim() || 'rzp_test_placeholder' }, data.accessToken);
      onNavigate('/onboarding');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Registration failed.');
    }
  };

  const handleVerify = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);
    try {
      const { data, error: authError } = await requireInsforge().auth.verifyEmail({ email: email.trim(), otp: verificationCode });
      if (authError || !data?.accessToken) throw new Error(authError?.message || 'Invalid verification code.');
      await signup({ name: name.trim(), slug: slug.trim().toLowerCase(), email: email.trim(), rzpKeyId: rzpKeyId.trim() || 'rzp_test_placeholder' }, data.accessToken);
      onNavigate('/onboarding');
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : 'Verification failed.');
    }
  };

  return (
    <div className="auth-page">
      <div className="auth-shell">
        <main className="auth-form-side">
          <div className="auth-form-wrap auth-reveal">
            <button type="button" onClick={() => onNavigate('/')} className="auth-back"><ArrowLeft className="h-4 w-4" /> Home</button>
            <div className="mt-9"><span className="auth-brand">pimp</span></div>
            <div className="mt-10"><h1 className="text-3xl font-semibold tracking-[-0.055em] text-slate-50">Register Merchant</h1><p className="mt-3 text-sm text-slate-400">Create a governed workspace for your store.</p></div>

            <form onSubmit={awaitingVerification ? handleVerify : handleSubmit} className="mt-7 space-y-4">
              {error && <div className="flex items-center gap-2 rounded-md border border-rose-400/25 bg-rose-400/10 p-3 text-xs font-medium text-rose-200"><AlertCircle className="h-4 w-4 shrink-0" />{error}</div>}
              {awaitingVerification ? <><p className="text-sm text-slate-400">Enter the six-digit verification code sent to {email}.</p><Input className="auth-input" label="Verification code" inputMode="numeric" value={verificationCode} onChange={(event) => setVerificationCode(event.target.value)} required /><Button type="submit" className="mt-2 w-full rounded-md bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200" isLoading={isLoading}>Verify & Create Store <ArrowRight className="h-4 w-4" /></Button></> : <><Input className="auth-input" label="Store / Business Name" placeholder="Apex Athletic" value={name} onChange={handleNameChange} required /><Input className="auth-input" label="Store Slug" placeholder="apex-athletic" value={slug} onChange={(event) => setSlug(event.target.value.toLowerCase())} helperText="Unique identifier for AI buyers" required /><Input className="auth-input" label="Admin Email" type="email" placeholder="admin@apex-athletic.com" value={email} onChange={(event) => setEmail(event.target.value)} required /><Input className="auth-input" label="Password" type="password" placeholder="At least 6 characters" value={password} onChange={(event) => setPassword(event.target.value)} required /><Input className="auth-input" label="Razorpay Test Key ID" placeholder="rzp_test_..." value={rzpKeyId} onChange={(event) => setRzpKeyId(event.target.value)} helperText="Test mode API key" /><Button type="submit" className="mt-2 w-full rounded-md bg-emerald-300 font-semibold text-slate-950 hover:bg-emerald-200" isLoading={isLoading}>Create Store & Continue <ArrowRight className="h-4 w-4" /></Button></>}
            </form>
            <p className="mt-7 text-center text-sm text-slate-400">Already registered? <button type="button" onClick={() => onNavigate('/login')} className="font-medium text-slate-100 hover:underline">Sign In</button></p>
          </div>
        </main>
        <aside className="auth-visual-side" aria-hidden="true"><div className="auth-dot-field" /><div className="auth-visual-copy">Set your rules. <span>Keep control.</span></div></aside>
      </div>
    </div>
  );
};
