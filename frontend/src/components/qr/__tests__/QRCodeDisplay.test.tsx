// frontend/src/components/qr/__tests__/QRCodeDisplay.test.tsx
import { render } from '@testing-library/react';
import { QRCodeDisplay } from '../QRCodeDisplay';

describe('QRCodeDisplay', () => {
  it('renders QR code with value', () => {
    render(<QRCodeDisplay value="https://example.com/sync/ABC123" />);
    const svg = document.querySelector('svg');
    expect(svg).toBeInTheDocument();
  });

  it('applies custom size', () => {
    render(<QRCodeDisplay value="test" size={300} />);
    const svg = document.querySelector('svg');
    expect(svg).toHaveAttribute('width', '300');
  });

  it('applies custom className', () => {
    const { container } = render(
      <QRCodeDisplay value="test" className="custom-class" />
    );
    expect(container.firstChild).toHaveClass('custom-class');
  });
});
