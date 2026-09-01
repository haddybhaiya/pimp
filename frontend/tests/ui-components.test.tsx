import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { Dialog } from '@/components/ui/dialog';
import { StepIndicator } from '@/components/ui/step-indicator';

describe('UI Component Foundation Tests', () => {
  it('renders button with primary variant and handles click', () => {
    const onClick = vi.fn();
    render(<Button onClick={onClick}>Click Me</Button>);
    const btn = screen.getByRole('button', { name: /click me/i });
    fireEvent.click(btn);
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('disables button when isLoading is true', () => {
    render(<Button isLoading>Saving</Button>);
    const btn = screen.getByRole('button');
    expect(btn).toBeDisabled();
  });

  it('renders input with label and error message', () => {
    render(<Input label="Store Name" error="Name is required" />);
    expect(screen.getByLabelText(/store name/i)).toBeInTheDocument();
    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
  });

  it('renders badge with correct status variant', () => {
    render(<Badge variant="success">ACTIVE</Badge>);
    expect(screen.getByText('ACTIVE')).toBeInTheDocument();
  });

  it('renders dialog modal and closes on Escape key', () => {
    const onClose = vi.fn();
    render(
      <Dialog isOpen={true} onClose={onClose} title="Test Modal">
        <p>Modal content</p>
      </Dialog>
    );
    expect(screen.getByText('Test Modal')).toBeInTheDocument();
    fireEvent.keyDown(document, { key: 'Escape' });
    expect(onClose).toHaveBeenCalled();
  });

  it('renders step indicator correctly highlighting current step', () => {
    const steps = [
      { id: 1, title: 'Step 1' },
      { id: 2, title: 'Step 2' },
      { id: 3, title: 'Step 3' },
    ];
    render(<StepIndicator steps={steps} currentStep={2} />);
    expect(screen.getByText('Step 1')).toBeInTheDocument();
    expect(screen.getByText('Step 2')).toBeInTheDocument();
  });
});
