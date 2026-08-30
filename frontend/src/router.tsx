import React, { useEffect, useState } from 'react';
import { useAuth } from '@/lib/auth-store';
import { LandingPage } from '@/pages/landing';
import { LoginPage } from '@/pages/login';
import { SignupPage } from '@/pages/signup';
import { OnboardingPage } from '@/pages/onboarding';
import { DashboardPage } from '@/pages/dashboard';
import { CatalogPage } from '@/pages/catalog';
import { InventoryPage } from '@/pages/inventory';
import { QuotesPage } from '@/pages/quotes';
import { OrdersPage } from '@/pages/orders';
import { PaymentsPage } from '@/pages/payments';
import { NegotiationsPage } from '@/pages/negotiations';
import { ApprovalsPage } from '@/pages/approvals';
import { PoliciesPage } from '@/pages/policies';
import { AuditPage } from '@/pages/audit';
import { SettingsPage } from '@/pages/settings';
import { DemoPage } from '@/pages/demo';
import { UnauthorizedPage } from '@/pages/unauthorized';
import { NotFoundPage } from '@/pages/not-found';
import { Navbar } from '@/components/layout/navbar';
import { AppShell } from '@/components/layout/app-shell';
import { Footer } from '@/components/layout/footer';

export const Router: React.FC = () => {
  const { isAuthenticated, isLoading } = useAuth();
  const [currentPath, setCurrentPath] = useState<string>(() => window.location.pathname || '/');

  useEffect(() => {
    const handlePopState = () => {
      setCurrentPath(window.location.pathname || '/');
    };
    window.addEventListener('popstate', handlePopState);
    return () => window.removeEventListener('popstate', handlePopState);
  }, []);

  const navigate = (path: string) => {
    window.history.pushState({}, '', path);
    setCurrentPath(path);
    if (typeof window !== 'undefined' && window.scrollTo) {
      window.scrollTo(0, 0);
    }
  };

  if (isLoading) {
    return (
      <div className="flex h-screen w-screen items-center justify-center bg-background text-primary">
        <div className="h-8 w-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  // Public Routes (with Navbar/Footer)
  if (currentPath === '/') {
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar onNavigate={navigate} />
        <main className="flex-1">
          <LandingPage onNavigate={navigate} />
        </main>
        <Footer />
      </div>
    );
  }

  if (currentPath === '/login') {
    if (isAuthenticated) {
      navigate('/dashboard');
      return null;
    }
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar onNavigate={navigate} />
        <main className="flex-1">
          <LoginPage onNavigate={navigate} />
        </main>
        <Footer />
      </div>
    );
  }

  if (currentPath === '/signup') {
    if (isAuthenticated) {
      navigate('/dashboard');
      return null;
    }
    return (
      <div className="min-h-screen flex flex-col">
        <Navbar onNavigate={navigate} />
        <main className="flex-1">
          <SignupPage onNavigate={navigate} />
        </main>
        <Footer />
      </div>
    );
  }

  // Protected Routes
  if (!isAuthenticated) {
    navigate('/login');
    return null;
  }

  if (currentPath === '/onboarding') {
    return (
      <AppShell currentPath={currentPath} onNavigate={navigate}>
        <OnboardingPage onNavigate={navigate} />
      </AppShell>
    );
  }

  const renderProtectedView = () => {
    switch (currentPath) {
      case '/dashboard': return <DashboardPage onNavigate={navigate} />;
      case '/catalog': return <CatalogPage />;
      case '/inventory': return <InventoryPage />;
      case '/quotes': return <QuotesPage />;
      case '/orders': return <OrdersPage />;
      case '/payments': return <PaymentsPage />;
      case '/negotiations': return <NegotiationsPage />;
      case '/approvals': return <ApprovalsPage />;
      case '/policies': return <PoliciesPage />;
      case '/audit': return <AuditPage />;
      case '/settings': return <SettingsPage />;
      case '/demo': return <DemoPage />;
      case '/unauthorized': return <UnauthorizedPage onNavigate={navigate} />;
      default: return <NotFoundPage onNavigate={navigate} />;
    }
  };

  return (
    <AppShell currentPath={currentPath} onNavigate={navigate}>
      {renderProtectedView()}
    </AppShell>
  );
};
