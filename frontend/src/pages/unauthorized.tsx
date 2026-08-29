import React from 'react';
import { Button } from '@/components/ui/button';
import { ShieldAlert } from 'lucide-react';

export interface UnauthorizedPageProps {
  onNavigate: (path: string) => void;
}

export const UnauthorizedPage: React.FC<UnauthorizedPageProps> = ({ onNavigate }) => {
  return (
    <div className="flex min-h-[calc(100vh-12rem)] flex-col items-center justify-center text-center px-4">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-destructive/15 text-destructive mb-4">
        <ShieldAlert className="h-8 w-8" />
      </div>
      <h2 className="text-2xl font-bold">Access Denied</h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        You do not have the required merchant authorization or capability to access this view.
      </p>
      <div className="mt-6 flex gap-3">
        <Button onClick={() => onNavigate('/login')} variant="primary" size="sm">
          Sign In as Admin
        </Button>
        <Button onClick={() => onNavigate('/')} variant="outline" size="sm">
          Back to Home
        </Button>
      </div>
    </div>
  );
};
