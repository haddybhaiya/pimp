import React from 'react';
import { Button } from '@/components/ui/button';
import { FileQuestion } from 'lucide-react';

export interface NotFoundPageProps {
  onNavigate: (path: string) => void;
}

export const NotFoundPage: React.FC<NotFoundPageProps> = ({ onNavigate }) => {
  return (
    <div className="flex min-h-[calc(100vh-12rem)] flex-col items-center justify-center text-center px-4">
      <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-muted text-muted-foreground mb-4">
        <FileQuestion className="h-8 w-8" />
      </div>
      <h2 className="text-2xl font-bold">404 - View Not Found</h2>
      <p className="mt-2 max-w-sm text-sm text-muted-foreground">
        The requested control plane route does not exist.
      </p>
      <Button onClick={() => onNavigate('/')} className="mt-6" size="sm">
        Return Home
      </Button>
    </div>
  );
};
