// frontend/src/components/ui/__tests__/EmptyState.test.tsx
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { vi } from 'vitest';
import { EmptyState } from '../EmptyState';

describe('EmptyState', () => {
  it('renders title', () => {
    render(
      <EmptyState title="No items found" description="Your list is empty" />
    );

    expect(screen.getByText('No items found')).toBeInTheDocument();
  });

  it('renders description', () => {
    render(
      <EmptyState title="No items found" description="Your list is empty" />
    );

    expect(screen.getByText('Your list is empty')).toBeInTheDocument();
  });

  it('renders icon when provided', () => {
    const testIcon = <svg data-testid="test-icon" />;

    render(
      <EmptyState
        icon={testIcon}
        title="No items"
        description="Description"
      />
    );

    expect(screen.getByTestId('test-icon')).toBeInTheDocument();
  });

  it('does not render icon container when icon is not provided', () => {
    const { container } = render(
      <EmptyState title="No items" description="Description" />
    );

    // The icon is wrapped in a flex container, but it should not exist
    const iconContainer = container.querySelector('.text-gray-300');
    expect(iconContainer).not.toBeInTheDocument();
  });

  it('shows action button when action is provided', () => {
    render(
      <EmptyState
        title="No items"
        description="Description"
        action={{ label: 'Add Item', onClick: vi.fn() }}
      />
    );

    expect(
      screen.getByRole('button', { name: /add item/i })
    ).toBeInTheDocument();
  });

  it('hides action button when action is not provided', () => {
    render(<EmptyState title="No items" description="Description" />);

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('calls action.onClick when action button is clicked', async () => {
    const user = userEvent.setup();
    const handleClick = vi.fn();

    render(
      <EmptyState
        title="No items"
        description="Description"
        action={{ label: 'Add Item', onClick: handleClick }}
      />
    );

    await user.click(screen.getByRole('button', { name: /add item/i }));

    expect(handleClick).toHaveBeenCalledTimes(1);
  });

  it('renders with centered text alignment', () => {
    const { container } = render(
      <EmptyState title="No items" description="Description" />
    );

    const wrapper = container.firstChild as HTMLElement;
    expect(wrapper).toHaveClass('text-center');
  });

  it('renders title with correct styling', () => {
    render(<EmptyState title="Empty Title" description="Description" />);

    const title = screen.getByText('Empty Title');
    expect(title.tagName).toBe('H2');
    expect(title).toHaveClass('text-xl');
    expect(title).toHaveClass('font-semibold');
    expect(title).toHaveClass('text-gray-900');
  });

  it('renders description with correct styling', () => {
    render(<EmptyState title="Title" description="Empty description" />);

    const description = screen.getByText('Empty description');
    expect(description.tagName).toBe('P');
    expect(description).toHaveClass('text-gray-500');
  });

  it('renders icon with gray text color', () => {
    const testIcon = <svg data-testid="test-icon" />;

    const { container } = render(
      <EmptyState
        icon={testIcon}
        title="Title"
        description="Description"
      />
    );

    const iconContainer = container.querySelector('.text-gray-300');
    expect(iconContainer).toBeInTheDocument();
  });

  it('action button renders with primary variant by default', () => {
    render(
      <EmptyState
        title="Title"
        description="Description"
        action={{ label: 'Click me', onClick: vi.fn() }}
      />
    );

    const button = screen.getByRole('button', { name: /click me/i });
    expect(button).toHaveClass('bg-primary-600');
    expect(button).toHaveClass('text-white');
  });
});
