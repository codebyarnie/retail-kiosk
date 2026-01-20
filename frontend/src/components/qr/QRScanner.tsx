// frontend/src/components/qr/QRScanner.tsx
import { useCallback, useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from 'html5-qrcode';

interface QRScannerProps {
  isActive: boolean;
  onScan: (data: string) => void;
  onError?: (error: Error) => void;
}

export function QRScanner({ isActive, onScan, onError }: QRScannerProps) {
  const scannerRef = useRef<Html5Qrcode | null>(null);
  const [hasPermission, setHasPermission] = useState<boolean | null>(null);
  const [error, setError] = useState<string | null>(null);

  const stopScanner = useCallback(async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop();
        scannerRef.current.clear();
      } catch {
        // Ignore stop errors
      }
      scannerRef.current = null;
    }
  }, []);

  const startScanner = useCallback(async () => {
    try {
      const scanner = new Html5Qrcode('qr-reader');
      scannerRef.current = scanner;

      await scanner.start(
        { facingMode: 'environment' },
        {
          fps: 10,
          qrbox: { width: 250, height: 250 },
        },
        (decodedText) => {
          onScan(decodedText);
          stopScanner();
        },
        () => {
          // Ignore scan failures (no QR in view)
        }
      );
      setHasPermission(true);
      setError(null);
    } catch (err) {
      setHasPermission(false);
      const message =
        err instanceof Error ? err.message : 'Camera access denied';
      setError(message);
      onError?.(err instanceof Error ? err : new Error(message));
    }
  }, [onScan, onError, stopScanner]);

  useEffect(() => {
    if (!isActive) {
      stopScanner();
      return;
    }

    startScanner();

    return () => {
      stopScanner();
    };
  }, [isActive, startScanner, stopScanner]);

  if (!isActive) {
    return null;
  }

  return (
    <div data-testid="qr-scanner" className="relative">
      <div id="qr-reader" className="w-full max-w-sm mx-auto" />

      {hasPermission === null && (
        <div className="text-center py-8">
          <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Requesting camera access...</p>
        </div>
      )}

      {hasPermission === true && (
        <p className="text-center text-sm text-gray-500 mt-4">
          Point your camera at a QR code
        </p>
      )}

      {error && (
        <div className="text-center py-8">
          <svg
            className="w-12 h-12 text-red-500 mx-auto mb-4"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
            />
          </svg>
          <p className="text-red-600 mb-2">{error}</p>
          <p className="text-sm text-gray-500">
            Please enable camera access in your browser settings
          </p>
        </div>
      )}
    </div>
  );
}
