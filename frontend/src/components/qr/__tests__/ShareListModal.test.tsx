// frontend/src/components/qr/__tests__/ShareListModal.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ShareListModal } from '../ShareListModal';
import api from '@/services/api';
import { vi } from 'vitest';

vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn().mockResolvedValue({
      data: {
        list_id: 'list-123',
        share_code: 'ABC123',
        sync_url: '/api/lists/sync/ABC123',
      },
    }),
  },
}));

describe('ShareListModal', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('renders modal when open', () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    expect(screen.getByText(/share your list/i)).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    render(
      <ShareListModal isOpen={false} onClose={vi.fn()} listId="list-123" />
    );
    expect(screen.queryByText(/share your list/i)).not.toBeInTheDocument();
  });

  it('displays QR code after loading', async () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(document.querySelector('svg')).toBeInTheDocument();
    });
  });

  it('shows share code text', async () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(screen.getByText('ABC123')).toBeInTheDocument();
    });
  });

  it('calls API to generate share code on open', async () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(api.post).toHaveBeenCalledWith('/lists/list-123/share');
    });
  });

  it('shows loading state initially', () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    // Loading spinner should be present initially
    expect(document.querySelector('.animate-spin')).toBeInTheDocument();
  });

  it('shows error state when API fails', async () => {
    vi.mocked(api.post).mockRejectedValueOnce(new Error('API Error'));
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(screen.getByText(/failed to generate share code/i)).toBeInTheDocument();
    });
  });

  it('shows Try Again button on error', async () => {
    vi.mocked(api.post).mockRejectedValueOnce(new Error('API Error'));
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });
  });

  it('retries API call when Try Again is clicked', async () => {
    const user = userEvent.setup();
    vi.mocked(api.post)
      .mockRejectedValueOnce(new Error('API Error'))
      .mockResolvedValueOnce({
        data: {
          list_id: 'list-123',
          share_code: 'ABC123',
          sync_url: '/api/lists/sync/ABC123',
        },
      });

    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /try again/i })).toBeInTheDocument();
    });

    await user.click(screen.getByRole('button', { name: /try again/i }));

    await waitFor(() => {
      expect(api.post).toHaveBeenCalledTimes(2);
    });
  });

  it('shows Copy Link button after loading', async () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(screen.getByRole('button', { name: /copy link/i })).toBeInTheDocument();
    });
  });

  it('shows expiration notice', async () => {
    render(
      <ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />
    );
    await waitFor(() => {
      expect(screen.getByText(/expires in 24 hours/i)).toBeInTheDocument();
    });
  });
});
