import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-store';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import {
  ShieldCheck,
  LayoutDashboard,
  Clock,
  Package,
  ShoppingCart,
  Sliders,
  FileText,
  LogOut,
  Menu,
  X,
} from 'lucide-react';

export interface AppShellProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ currentPath, onNavigate, children }) => {
  const { merchant, logout, sessionExpired, dismissExpiredDialog } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navItems = [
    { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
    { label: 'Approval Queue', path: '/approvals', icon: Clock },
    { label: 'Products & Catalog', path: '/catalog', icon: Package },
    { label: 'Orders & Settlement', path: '/orders', icon: ShoppingCart },
    { label: 'Policy Rules', path: '/policies', icon: Sliders },
    { label: 'Audit Trail', path: '/audit', icon: FileText },
  ];

  return (
    <div className="flex min-h-screen bg-background text-foreground">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 flex-col border-r border-border bg-card/40">
        <div className="flex h-16 items-center gap-3 border-b border-border px-6 cursor-pointer" onClick={() => onNavigate('/')}>
          <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-primary text-primary-foreground">
            <ShieldCheck className="h-4 w-4" />
          </div>
          <span className="font-bold text-sm tracking-tight">ARM Control Plane</span>
        </div>

        {/* Merchant Context */}
        <div className="border-b border-border p-4">
          <div className="flex items-center justify-between">
            <div className="truncate">
              <p className="font-semibold text-sm truncate">{merchant?.name || 'My Store'}</p>
              <p className="text-xs text-muted-foreground font-mono truncate">{merchant?.slug}</p>
            </div>
            <Badge variant="success" className="text-[10px]">
              {merchant?.status || 'ACTIVE'}
            </Badge>
          </div>
        </div>

        {/* Nav list */}
        <nav className="flex-1 space-y-1 p-4">
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = currentPath === item.path;
            return (
              <button
                key={item.path}
                onClick={() => onNavigate(item.path)}
                className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-primary text-primary-foreground shadow-sm'
                    : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                }`}
              >
                <Icon className="h-4 w-4" />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>

        {/* Footer info & Logout */}
        <div className="border-t border-border p-4 space-y-2">
          <div className="flex items-center justify-between text-xs text-muted-foreground">
            <span>Protocol v2026-03-01</span>
            <span className="font-mono">L{merchant?.policies.autonomyLevel ?? 1}</span>
          </div>
          <Button onClick={logout} variant="ghost" size="sm" className="w-full justify-start text-destructive hover:text-destructive hover:bg-destructive/10">
            <LogOut className="h-4 w-4" />
            <span>Sign Out</span>
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Top Navbar */}
        <header className="flex h-16 items-center justify-between border-b border-border bg-card/20 px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden rounded-md p-2 text-muted-foreground hover:bg-accent"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <h1 className="text-base font-semibold capitalize">
              {currentPath.replace('/', '') || 'Overview'}
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <Badge variant="outline" className="hidden sm:inline-flex text-[10px] text-muted-foreground">
              TEST MODE (RAZORPAY)
            </Badge>
            <Button onClick={() => onNavigate('/onboarding')} variant="outline" size="sm" className="text-xs">
              <Sliders className="h-3.5 w-3.5" />
              Settings
            </Button>
          </div>
        </header>

        {/* Mobile menu overlay */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-b border-border bg-card p-4 space-y-1 animate-in slide-in-from-top-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              const isActive = currentPath === item.path;
              return (
                <button
                  key={item.path}
                  onClick={() => {
                    onNavigate(item.path);
                    setMobileMenuOpen(false);
                  }}
                  className={`flex w-full items-center gap-3 rounded-md px-3 py-2 text-sm font-medium ${
                    isActive ? 'bg-primary text-primary-foreground' : 'text-muted-foreground'
                  }`}
                >
                  <Icon className="h-4 w-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
            <Button onClick={logout} variant="ghost" size="sm" className="w-full justify-start text-destructive mt-2">
              <LogOut className="h-4 w-4" />
              Sign Out
            </Button>
          </div>
        )}

        {/* Viewport Content */}
        <main className="flex-1 overflow-y-auto p-4 sm:p-6 lg:p-8">
          <div className="container mx-auto max-w-7xl">
            {children}
          </div>
        </main>
      </div>

      {/* Session Expired Dialog */}
      <Dialog
        isOpen={sessionExpired}
        onClose={dismissExpiredDialog}
        title="Session Expired"
        description="Your authenticated control plane session has expired. Please sign in again to continue."
      >
        <div className="flex justify-end gap-3 mt-4">
          <Button onClick={() => { dismissExpiredDialog(); onNavigate('/login'); }} variant="primary">
            Sign In Again
          </Button>
        </div>
      </Dialog>
    </div>
  );
};
