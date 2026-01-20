// frontend/src/components/qr/ShareListModal.tsx
import { useCallback, useEffect, useState } from 'react';
import { Modal } from '@/components/ui/Modal';
import { Button } from '@/components/ui/Button';
import { QRCodeDisplay } from './QRCodeDisplay';
import api from '@/services/api';
import type { ListSyncResponse } from '@/types';

interface ShareListModalProps {
  isOpen: boolean;
  onClose: () => void;
  listId: string;
}

export function ShareListModal({
  isOpen,
  onClose,
  listId,
}: ShareListModalProps) {
  const [shareData, setShareData] = useState<ListSyncResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  const generateShareCode = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.post<ListSyncResponse>(
        `/lists/${listId}/share`
      );
      setShareData(response.data);
    } catch {
      setError('Failed to generate share code');
    } finally {
      setIsLoading(false);
    }
  }, [listId]);

  useEffect(() => {
    if (isOpen && !shareData) {
      generateShareCode();
    }
  }, [isOpen, shareData, generateShareCode]);

  const getSyncUrl = () => {
    if (!shareData) {
      return '';
    }
    return `${window.location.origin}/sync/${shareData.share_code}`;
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(getSyncUrl());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers - silently fail
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Share Your List" size="md">
      <div className="text-center py-4">
        {isLoading && (
          <div className="flex items-center justify-center h-48">
            <div
              className={
                'w-8 h-8 border-4 border-primary-600 border-t-transparent ' +
                'rounded-full animate-spin'
              }
            />
          </div>
        )}

        {error && (
          <div className="text-red-600 py-8">
            <p>{error}</p>
            <Button
              variant="outline"
              onClick={generateShareCode}
              className="mt-4"
            >
              Try Again
            </Button>
          </div>
        )}

        {shareData && !isLoading && (
          <>
            <p className="text-gray-600 mb-6">
              Scan this QR code with your phone to save your list
            </p>

            <div className="flex justify-center mb-6">
              <QRCodeDisplay value={getSyncUrl()} size={200} />
            </div>

            <div className="bg-gray-100 rounded-lg p-4 mb-4">
              <p className="text-sm text-gray-500 mb-1">Share Code</p>
              <p className="text-2xl font-mono font-bold tracking-wider">
                {shareData.share_code}
              </p>
            </div>

            <Button variant="outline" onClick={handleCopy} className="w-full">
              {copied ? 'Copied!' : 'Copy Link'}
            </Button>

            <p className="text-xs text-gray-400 mt-4">
              Share code expires in 24 hours
            </p>
          </>
        )}
      </div>
    </Modal>
  );
}
