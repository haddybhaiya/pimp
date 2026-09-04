import React, { useState } from 'react';
import { useAuth } from '@/lib/auth-store';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import {
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
  Bot,
  FlaskConical,
  Globe,
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
        { label: 'Merchant Agent', path: '/agent', icon: Bot, badge: 'AI' },
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
        { label: 'Discoverability', path: '/discoverability', icon: Globe },
      ],
    },
    {
      title: 'INSPECT',
      items: [
        { label: 'Experiments', path: '/experiments', icon: FlaskConical },
        { label: 'Audit Trail (SHA-256)', path: '/audit', icon: FileText },
        { label: 'Simulation Sandbox', path: '/demo', icon: Sparkles, badge: 'Interactive' },
      ],
    },
  ];

  return (
    <div className="portal-font flex h-screen overflow-hidden bg-[#101113] text-[#f3f4f6]">
      {/* Desktop Sidebar */}
      <aside className="hidden w-64 flex-col border-r border-white/10 bg-[#1b1c1e] lg:flex shrink-0 h-full">
        {/* Brand header */}
        <div
          className="flex h-16 cursor-pointer items-center gap-3 border-b border-white/10 px-5 transition hover:opacity-90"
          onClick={() => onNavigate('/')}
        >
          <div>
            <span className="block text-xl font-semibold tracking-[-0.08em] text-slate-50">
              pimp
            </span>
            <span className="text-[10px] text-text-muted font-mono tracking-wide">
              CONTROL PLANE
            </span>
          </div>
        </div>

        {/* Merchant Context Card */}
        <div className="border-b border-white/[0.07] p-3 shrink-0">
          <div className="rounded-md border border-white/10 bg-white/[0.035] p-3">
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
                          ? 'bg-white/[0.10] text-white font-semibold'
                          : 'text-slate-400 hover:bg-white/[0.06] hover:text-slate-100'
                      }`}
                    >
                      <div className="flex items-center gap-2.5">
                        <Icon className={`h-4 w-4 ${isActive ? 'text-emerald-300' : 'text-slate-500'}`} />
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
        <div className="space-y-2 border-t border-white/10 bg-black/10 p-3 shrink-0">
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
        <header className="flex h-16 items-center justify-between border-b border-white/10 bg-[#17181a] px-4 sm:px-6">
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
              className="rounded-lg p-2 text-text-muted hover:bg-white/10 hover:text-text-primary lg:hidden"
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
            <div className="hidden items-center gap-1.5 rounded-md border border-white/10 bg-white/[0.035] px-2.5 py-1 text-[11px] text-slate-400 md:flex">
              <Database className="h-3 w-3 text-emerald-400" />
              <span>InsForge PostgreSQL</span>
            </div>

            <Badge variant="outline" className="border-emerald-300/25 bg-emerald-300/[0.06] text-[10px] text-emerald-200">
              TEST MODE
            </Badge>

            <Button
              onClick={() => onNavigate('/demo')}
              variant="outline"
              size="sm"
              className="hidden border-white/15 bg-white/[0.06] text-xs text-slate-200 hover:bg-white/[0.1] sm:inline-flex"
            >
              <Sparkles className="h-3 w-3 text-brand-bright" />
              Sandbox
            </Button>

            <Button
              onClick={logout}
              variant="ghost"
              size="sm"
              aria-label="Sign out"
              title="Sign out"
              className="px-2 text-rose-400 hover:bg-rose-500/10 hover:text-rose-300 lg:hidden"
            >
              <LogOut className="h-4 w-4" />
            </Button>
          </div>
        </header>

        {/* Mobile menu overlay */}
        {mobileMenuOpen && (
          <div className="animate-in slide-in-from-top-2 space-y-4 border-b border-white/10 bg-[#1b1c1e] p-4 lg:hidden">
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
                        isActive ? 'bg-emerald-300 text-slate-950 font-semibold' : 'text-text-secondary hover:bg-white/[0.07]'
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
