import React from 'react';
import { Button } from '@/components/ui/button';
import { useAuth } from '@/lib/auth-store';
import { ShieldCheck, ArrowRight, LayoutDashboard } from 'lucide-react';

export interface NavbarProps {
  onNavigate: (path: string) => void;
}

export const Navbar: React.FC<NavbarProps> = ({ onNavigate }) => {
  const { isAuthenticated, merchant } = useAuth();

  return (
    <header className="sticky top-0 z-40 w-full border-b border-border/60 bg-background/80 backdrop-blur-md">
      <div className="container mx-auto flex h-16 max-w-7xl items-center justify-between px-4 sm:px-6 lg:px-8">
        <div className="flex items-center gap-3 cursor-pointer" onClick={() => onNavigate('/')}>
          <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-primary text-primary-foreground shadow-sm">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <span className="font-bold text-lg tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent">
            Agent-Ready Merchant
          </span>
        </div>

        <nav className="flex items-center gap-3">
          {isAuthenticated ? (
            <Button onClick={() => onNavigate('/dashboard')} variant="primary" size="sm">
              <LayoutDashboard className="h-4 w-4" />
              <span>{merchant?.name || 'Dashboard'}</span>
            </Button>
          ) : (
            <>
              <Button onClick={() => onNavigate('/login')} variant="ghost" size="sm">
                Log In
              </Button>
              <Button onClick={() => onNavigate('/signup')} variant="primary" size="sm">
                Get Started
                <ArrowRight className="h-4 w-4" />
              </Button>
            </>
          )}
        </nav>
      </div>
    </header>
  );
};
