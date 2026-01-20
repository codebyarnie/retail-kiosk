// frontend/src/pages/SyncPage.tsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QRScanner } from '@/components/qr';
import { Button } from '@/components/ui';
import { listService } from '@/services';
import { useListStore, useSessionStore } from '@/store';

export function SyncPage() {
  const { code } = useParams<{ code?: string }>();
  const navigate = useNavigate();
  const { setList } = useListStore();
  const { setSession, sessionId } = useSessionStore();

  const [isScanning, setIsScanning] = useState(!code);
  const [isLoading, setIsLoading] = useState(!!code);
  const [error, setError] = useState<string | null>(null);
  const [manualCode, setManualCode] = useState('');

  useEffect(() => {
    if (code) {
      syncList(code);
    }
  }, [code]);

  const syncList = async (shareCode: string) => {
    setIsLoading(true);
    setError(null);
    try {
      const syncedList = await listService.syncFromCode(shareCode);
      setList(syncedList);
      // Update session with the synced list
      if (sessionId) {
        setSession(sessionId, syncedList.id);
      }
      navigate('/list');
    } catch (err) {
      setError('Could not find a list with that code. Please try again.');
      setIsLoading(false);
    }
  };

  const handleScan = (data: string) => {
    // Extract code from URL if full URL scanned
    const match = data.match(/\/sync\/([A-Z0-9]+)/i);
    const shareCode = match?.[1] ?? data;
    syncList(shareCode);
  };

  const handleManualSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (manualCode.trim()) {
      syncList(manualCode.trim().toUpperCase());
    }
  };

  if (isLoading) {
    return (
      <div className="max-w-md mx-auto px-4 py-12 text-center">
        <div className="w-12 h-12 border-4 border-primary-600 border-t-transparent rounded-full animate-spin mx-auto mb-4" />
        <p className="text-gray-600">Syncing your list...</p>
      </div>
    );
  }

  return (
    <div className="max-w-md mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold text-gray-900 text-center mb-2">
        Sync Your List
      </h1>
      <p className="text-gray-500 text-center mb-8">
        Scan a QR code or enter a share code to sync a list
      </p>

      {error && (
        <div className="bg-red-50 text-red-700 p-4 rounded-lg mb-6 text-center">
          {error}
        </div>
      )}

      {isScanning ? (
        <div className="mb-8">
          <QRScanner
            isActive={isScanning}
            onScan={handleScan}
            onError={() => setIsScanning(false)}
          />
          <Button
            variant="ghost"
            onClick={() => setIsScanning(false)}
            className="w-full mt-4"
          >
            Enter code manually
          </Button>
        </div>
      ) : (
        <div className="mb-8">
          <form onSubmit={handleManualSubmit} className="space-y-4">
            <div>
              <label
                htmlFor="code"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Share Code
              </label>
              <input
                id="code"
                type="text"
                value={manualCode}
                onChange={(e) => setManualCode(e.target.value.toUpperCase())}
                placeholder="ABC123"
                className="w-full px-4 py-3 border border-gray-300 rounded-lg text-center text-xl font-mono tracking-wider focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                maxLength={10}
              />
            </div>
            <Button
              type="submit"
              className="w-full"
              disabled={!manualCode.trim()}
            >
              Sync List
            </Button>
          </form>

          <div className="relative my-6">
            <div className="absolute inset-0 flex items-center">
              <div className="w-full border-t border-gray-200" />
            </div>
            <div className="relative flex justify-center text-sm">
              <span className="px-2 bg-white text-gray-500">or</span>
            </div>
          </div>

          <Button
            variant="outline"
            onClick={() => setIsScanning(true)}
            className="w-full"
          >
            <svg
              className="w-5 h-5 mr-2"
              fill="none"
              stroke="currentColor"
              viewBox="0 0 24 24"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z"
              />
            </svg>
            Scan QR Code
          </Button>
        </div>
      )}
    </div>
  );
}
