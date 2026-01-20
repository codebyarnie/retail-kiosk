// frontend/src/components/ui/__tests__/ErrorDisplay.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { ErrorDisplay } from '../ErrorDisplay';

describe('ErrorDisplay', () => {
  it('renders default title when not provided', () => {
    render(<ErrorDisplay message="An error occurred" />);

    expect(screen.getByText('Something went wrong')).toBeInTheDocument();
  });

  it('renders custom title when provided', () => {
    render(<ErrorDisplay title="Custom Error" message="An error occurred" />);

    expect(screen.getByText('Custom Error')).toBeInTheDocument();
    expect(
      screen.queryByText('Something went wrong')
    ).not.toBeInTheDocument();
  });

  it('renders message', () => {
    render(<ErrorDisplay message="This is the error message" />);

    expect(screen.getByText('This is the error message')).toBeInTheDocument();
  });

  it('renders error icon', () => {
    const { container } = render(<ErrorDisplay message="Error" />);

    const svg = container.querySelector('svg');
    expect(svg).toBeInTheDocument();
    expect(svg).toHaveClass('text-red-500');
  });

  it('shows retry button when onRetry is provided', () => {
    render(<ErrorDisplay message="Error" onRetry={vi.fn()} />);

    expect(
      screen.getByRole('button', { name: /try again/i })
    ).toBeInTheDocument();
  });

  it('hides retry button when onRetry is not provided', () => {
    render(<ErrorDisplay message="Error" />);

    expect(
      screen.queryByRole('button', { name: /try again/i })
    ).not.toBeInTheDocument();
  });

  it('calls onRetry when retry button is clicked', async () => {
    const user = userEvent.setup();
    const handleRetry = vi.fn();

    render(<ErrorDisplay message="Error" onRetry={handleRetry} />);

    await user.click(screen.getByRole('button', { name: /try again/i }));

    expect(handleRetry).toHaveBeenCalledTimes(1);
  });

  it('retry button has outline variant', () => {
    render(<ErrorDisplay message="Error" onRetry={vi.fn()} />);

    const button = screen.getByRole('button', { name: /try again/i });
    expect(button).toHaveClass('border-2');
    expect(button).toHaveClass('border-primary-600');
  });

  it('renders with centered text alignment', () => {
    const { container } = render(<ErrorDisplay message="Error" />);

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('text-center');
  });

  it('renders title with correct styling', () => {
    render(<ErrorDisplay title="Error Title" message="Error message" />);

    const title = screen.getByText('Error Title');
    expect(title.tagName).toBe('H2');
    expect(title).toHaveClass('text-xl');
    expect(title).toHaveClass('font-semibold');
    expect(title).toHaveClass('text-gray-900');
  });

  it('renders message with correct styling', () => {
    render(<ErrorDisplay message="Error description" />);

    const message = screen.getByText('Error description');
    expect(message.tagName).toBe('P');
    expect(message).toHaveClass('text-gray-500');
  });
});
