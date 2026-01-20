// frontend/src/components/qr/QRCodeDisplay.tsx
import QRCode from 'react-qr-code';
import classNames from 'classnames';

interface QRCodeDisplayProps {
  value: string;
  size?: number;
  className?: string;
}

export function QRCodeDisplay({
  value,
  size = 200,
  className,
}: QRCodeDisplayProps) {
  return (
    <div
      className={classNames(
        'inline-block p-4 bg-white rounded-lg',
        className
      )}
    >
      <QRCode
        value={value}
        size={size}
        level="L"
        bgColor="#FFFFFF"
        fgColor="#000000"
      />
    </div>
  );
}
