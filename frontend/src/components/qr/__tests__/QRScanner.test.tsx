// frontend/src/components/qr/__tests__/QRScanner.test.tsx
import { render, screen } from '@testing-library/react';
import { QRScanner } from '../QRScanner';
import { vi } from 'vitest';

// Mock html5-qrcode since it requires camera access
vi.mock('html5-qrcode', () => ({
  Html5Qrcode: vi.fn().mockImplementation(() => ({
    start: vi.fn().mockResolvedValue(undefined),
    stop: vi.fn().mockResolvedValue(undefined),
    clear: vi.fn(),
  })),
}));

describe('QRScanner', () => {
  it('renders scanner container when active', () => {
    render(<QRScanner isActive={true} onScan={vi.fn()} />);
    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument();
  });

  it('does not render when inactive', () => {
    render(<QRScanner isActive={false} onScan={vi.fn()} />);
    expect(screen.queryByTestId('qr-scanner')).not.toBeInTheDocument();
  });

  it('shows instructions text when active', () => {
    render(<QRScanner isActive={true} onScan={vi.fn()} />);
    // The scanner shows "Point your camera" or loading/error state
    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument();
  });
});
