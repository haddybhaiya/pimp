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
  Layers,
  ShoppingCart,
  CreditCard,
  Sliders,
  FileText,
  Sparkles,
  LogOut,
  Menu,
  X,
  Database,
} from 'lucide-react';

export interface AppShellProps {
  currentPath: string;
  onNavigate: (path: string) => void;
  children: React.ReactNode;
}

export const AppShell: React.FC<AppShellProps> = ({ currentPath, onNavigate, children }) => {
  const { merchant, logout, sessionExpired, dismissExpiredDialog } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const navGroups = [
    {
      title: 'OPERATE',
      items: [
        { label: 'Overview', path: '/dashboard', icon: LayoutDashboard },
        { label: 'Approval Queue', path: '/approvals', icon: Clock },
        { label: 'Orders Ledger', path: '/orders', icon: ShoppingCart },
        { label: 'Payments', path: '/payments', icon: CreditCard },
      ],
    },
    {
      title: 'MANAGE',
      items: [
        { label: 'Products & Catalog', path: '/catalog', icon: Package },
        { label: 'Inventory Stock', path: '/inventory', icon: Layers },
        { label: 'Policy Governance', path: '/policies', icon: Sliders },
      ],
    },
    {
      title: 'INSPECT',
      items: [
        { label: 'Audit Trail (SHA-256)', path: '/audit', icon: FileText },
        { label: 'Simulation Sandbox', path: '/demo', icon: Sparkles, badge: 'Interactive' },
      ],
    },
  ];

  return (
    <div className="flex min-h-screen bg-[#070B14] text-[#F4F7FF]">
      {/* Desktop Sidebar */}
      <aside className="hidden lg:flex w-64 flex-col border-r border-[#24314A]/70 bg-[#0D1424]">
        {/* Brand header */}
        <div
          className="flex h-16 items-center gap-3 border-b border-[#24314A]/60 px-5 cursor-pointer hover:opacity-90 transition"
          onClick={() => onNavigate('/')}
        >
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-brand to-brand-deep text-white shadow-glow-sm">
            <ShieldCheck className="h-5 w-5" />
          </div>
          <div>
            <span className="font-bold text-sm tracking-tight text-text-primary block">
              Agent-Ready Merchant
            </span>
            <span className="text-[10px] text-text-muted font-mono tracking-wide">
              CONTROL PLANE
            </span>
          </div>
        </div>

        {/* Merchant Context Card */}
        <div className="p-3 border-b border-[#24314A]/40">
          <div className="bg-[#141D31]/80 rounded-lg p-3 border border-[#24314A]/60">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[10px] uppercase font-mono tracking-wider text-brand-bright">
                Store Profile
              </span>
              <span className="inline-flex items-center gap-1 text-[10px] text-emerald-400 font-medium">
                <span className="h-1.5 w-1.5 rounded-full bg-emerald-400 animate-pulse"></span>
                ACTIVE
              </span>
            </div>
            <p className="font-semibold text-xs text-text-primary truncate">
              {merchant?.name || 'Store Operator'}
            </p>
            <p className="text-[11px] text-text-muted font-mono truncate">
              slug: {merchant?.slug || 'default'}
            </p>
          </div>
        </div>

        {/* Grouped Navigation */}
        <nav className="flex-1 space-y-4 p-3 overflow-y-auto">
          {navGroups.map((group) => (
            <div key={group.title} className="space-y-1">
              <h3 className="px-3 text-[10px] font-mono font-semibold tracking-wider text-text-muted uppercase">
                {group.title}
              </h3>
              <div className="space-y-0.5">
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentPath === item.path;
                  return (
                    <button
                      key={item.path}
                      onClick={() => onNavigate(item.path)}
                      className={`flex w-full items-center justify-between rounded-lg px-3 py-2 text-xs font-medium transition-all ${
                        isActive
                          ? 'bg-brand/15 text-brand-bright border-l-2 border-brand font-semibold shadow-sm'
                          : 'text-text-secondary hover:bg-[#141D31] hover:text-text-primary'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className={`h-4 w-4 ${isActive ? 'text-brand-bright' : 'text-text-muted'}`} />
                        <span>{item.label}</span>
                      </div>
                      {item.badge && (
                        <span className="px-1.5 py-0.5 rounded text-[9px] font-mono bg-brand/20 text-brand-bright border border-brand/30">
                          {item.badge}
                        </span>
                      )}
                    </button>
                  );
                })}
              </div>
            </div>
          ))}
        </nav>

        {/* Footer info & Logout */}
        <div className="border-t border-[#24314A]/60 p-3 space-y-2 bg-[#070B14]/40">
          <div className="flex items-center justify-between text-[10px] text-text-muted px-2 font-mono">
            <span>Autonomy Level</span>
            <span className="text-text-primary font-bold">L{merchant?.policies.autonomyLevel ?? 1}</span>
          </div>
          <Button
            onClick={logout}
            variant="ghost"
            size="sm"
            className="w-full justify-start text-xs text-rose-400 hover:text-rose-300 hover:bg-rose-500/10"
          >
            <LogOut className="h-3.5 w-3.5" />
            <span>Sign Out</span>
          </Button>
        </div>
      </aside>

      {/* Main Content Area */}
      <div className="flex flex-1 flex-col overflow-hidden">
        {/* Command Center Topbar */}
        <header className="flex h-16 items-center justify-between border-b border-[#24314A]/70 bg-[#0D1424]/80 backdrop-blur-md px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="lg:hidden rounded-lg p-2 text-text-muted hover:bg-[#141D31] hover:text-text-primary"
            >
              {mobileMenuOpen ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
            </button>
            <div>
              <h1 className="text-sm font-bold capitalize text-text-primary flex items-center gap-2">
                {currentPath.replace('/', '').replace('-', ' ') || 'Overview Command'}
              </h1>
              <p className="text-[10px] text-text-muted font-mono hidden sm:block">
                SERVER-AUTHORITATIVE COMMERCE PIPELINE
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            {/* System Engine indicator */}
            <div className="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-[#141D31] border border-[#24314A] text-[11px] text-text-secondary">
              <Database className="h-3 w-3 text-emerald-400" />
              <span>InsForge PostgreSQL</span>
            </div>

            <Badge variant="outline" className="text-[10px] text-brand-bright border-brand/30 bg-brand/5">
              TEST MODE
            </Badge>

            <Button
              onClick={() => onNavigate('/demo')}
              variant="outline"
              size="sm"
              className="text-xs bg-brand/10 border-brand/40 text-brand-bright hover:bg-brand/20 hidden sm:inline-flex"
            >
              <Sparkles className="h-3 w-3 text-brand-bright" />
              Sandbox
            </Button>
          </div>
        </header>

        {/* Mobile menu overlay */}
        {mobileMenuOpen && (
          <div className="lg:hidden border-b border-[#24314A] bg-[#0D1424] p-4 space-y-4 animate-in slide-in-from-top-2">
            {navGroups.map((group) => (
              <div key={group.title} className="space-y-1">
                <h4 className="text-[10px] font-mono text-text-muted uppercase px-2">{group.title}</h4>
                {group.items.map((item) => {
                  const Icon = item.icon;
                  const isActive = currentPath === item.path;
                  return (
                    <button
                      key={item.path}
                      onClick={() => {
                        onNavigate(item.path);
                        setMobileMenuOpen(false);
                      }}
                      className={`flex w-full items-center gap-3 rounded-lg px-3 py-2 text-xs font-medium ${
                        isActive ? 'bg-brand text-white font-semibold' : 'text-text-secondary hover:bg-[#141D31]'
                      }`}
                    >
                      <Icon className="h-4 w-4" />
                      <span>{item.label}</span>
                    </button>
                  );
                })}
              </div>
            ))}
            <Button
              onClick={logout}
              variant="ghost"
              size="sm"
              className="w-full justify-start text-rose-400 hover:bg-rose-500/10 text-xs"
            >
              <LogOut className="h-3.5 w-3.5" />
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

      {/* Session Expired Re-auth Dialog */}
      {sessionExpired && (
        <Dialog
          isOpen={sessionExpired}
          onClose={dismissExpiredDialog}
          title="Session Expired"
          description="Your merchant admin credentials have expired. Please sign in again to continue managing your autonomous store."
        >
          <div className="py-4 text-xs text-text-secondary">
            For security, administrator tokens are bounded to 24 hours. No unauthorized financial operations can proceed without re-authentication.
          </div>
          <div className="flex justify-end gap-3">
            <Button
              onClick={() => {
                dismissExpiredDialog();
                onNavigate('/login');
              }}
              className="w-full"
            >
              Sign In Again
            </Button>
          </div>
        </Dialog>
      )}
    </div>
  );
};
