import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-border bg-card/20 py-8 text-xs text-muted-foreground">
      <div className="container mx-auto flex flex-col sm:flex-row max-w-7xl items-center justify-between gap-4 px-4 sm:px-6">
        <span className="font-display text-base font-semibold tracking-[-0.07em] text-slate-100">pimp</span>
        <div className="flex items-center gap-6">
          <a href="/docs" className="hover:text-foreground transition-colors">API Docs</a>
          <a href="https://razorpay.com" target="_blank" rel="noreferrer" className="hover:text-foreground transition-colors">Razorpay Powered</a>
          <span className="font-mono">Protocol: 2026-03-01</span>
        </div>
      </div>
    </footer>
  );
};
