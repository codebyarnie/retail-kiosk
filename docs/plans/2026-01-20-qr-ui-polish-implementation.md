# Phase 5: QR Sync & UI Polish Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable QR-based list sharing and add UI polish (loading states, error handling, empty states).

**Architecture:** Frontend-only implementation using react-qr-code and html5-qrcode libraries, with existing backend endpoints.

**Tech Stack:** React 18, TypeScript, Tailwind CSS, react-qr-code, html5-qrcode

---

## Task 1: Install QR Dependencies

**Files:**
- Modify: `frontend/package.json`

**Step 1: Install QR packages**

Run:
```bash
cd frontend && npm install react-qr-code html5-qrcode
```

**Step 2: Verify installation**

Run:
```bash
cd frontend && npm list react-qr-code html5-qrcode
```
Expected: Both packages listed with versions

**Step 3: Commit**

```bash
git add frontend/package.json frontend/package-lock.json
git commit -m "feat(frontend): add QR code dependencies"
```

---

## Task 2: Create QRCodeDisplay Component

**Files:**
- Create: `frontend/src/components/qr/QRCodeDisplay.tsx`
- Create: `frontend/src/components/qr/index.ts`
- Test: `frontend/src/components/qr/__tests__/QRCodeDisplay.test.tsx`

**Step 1: Write the failing test**

```tsx
// frontend/src/components/qr/__tests__/QRCodeDisplay.test.tsx
import { render, screen } from '@testing-library/react';
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
```

**Step 2: Run test to verify it fails**

Run: `cd frontend && npm test -- --run src/components/qr/__tests__/QRCodeDisplay.test.tsx`
Expected: FAIL - module not found

**Step 3: Implement QRCodeDisplay**

```tsx
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
    <div className={classNames('inline-block p-4 bg-white rounded-lg', className)}>
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
```

**Step 4: Create barrel export**

```tsx
// frontend/src/components/qr/index.ts
export { QRCodeDisplay } from './QRCodeDisplay';
```

**Step 5: Run tests**

Run: `cd frontend && npm test -- --run src/components/qr/__tests__/QRCodeDisplay.test.tsx`
Expected: PASS

**Step 6: Commit**

```bash
git add frontend/src/components/qr/
git commit -m "feat(frontend): add QRCodeDisplay component"
```

---

## Task 3: Create ShareListModal Component

**Files:**
- Create: `frontend/src/components/qr/ShareListModal.tsx`
- Modify: `frontend/src/components/qr/index.ts`
- Modify: `frontend/src/services/api.ts` (add shareList function)
- Test: `frontend/src/components/qr/__tests__/ShareListModal.test.tsx`

**Step 1: Write the failing test**

```tsx
// frontend/src/components/qr/__tests__/ShareListModal.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { ShareListModal } from '../ShareListModal';

// Mock api
vi.mock('@/services/api', () => ({
  default: {
    post: vi.fn().mockResolvedValue({
      data: { list_id: 'list-123', share_code: 'ABC123', sync_url: '/api/lists/sync/ABC123' }
    })
  }
}));

describe('ShareListModal', () => {
  it('renders modal when open', () => {
    render(<ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />);
    expect(screen.getByText(/share your list/i)).toBeInTheDocument();
  });

  it('displays QR code after loading', async () => {
    render(<ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />);
    await waitFor(() => {
      expect(document.querySelector('svg')).toBeInTheDocument();
    });
  });

  it('shows share code text', async () => {
    render(<ShareListModal isOpen={true} onClose={vi.fn()} listId="list-123" />);
    await waitFor(() => {
      expect(screen.getByText('ABC123')).toBeInTheDocument();
    });
  });

  it('calls onClose when close button clicked', async () => {
    const onClose = vi.fn();
    render(<ShareListModal isOpen={true} onClose={onClose} listId="list-123" />);
    const closeButton = screen.getByRole('button', { name: /close/i });
    await userEvent.click(closeButton);
    expect(onClose).toHaveBeenCalled();
  });
});
```

**Step 2: Add shareList API function**

```tsx
// Add to frontend/src/services/api.ts (or create lists.ts)
import api from './api';
import type { ListSyncResponse } from '@/types';

export async function shareList(listId: string): Promise<ListSyncResponse> {
  const response = await api.post<ListSyncResponse>(`/lists/${listId}/share`);
  return response.data;
}

export async function syncListFromCode(shareCode: string): Promise<void> {
  await api.post(`/lists/sync/${shareCode}`);
}
```

**Step 3: Implement ShareListModal**

```tsx
// frontend/src/components/qr/ShareListModal.tsx
import { useEffect, useState } from 'react';
import { Modal, Button } from '@/components/ui';
import { QRCodeDisplay } from './QRCodeDisplay';
import api from '@/services/api';
import type { ListSyncResponse } from '@/types';

interface ShareListModalProps {
  isOpen: boolean;
  onClose: () => void;
  listId: string;
}

export function ShareListModal({ isOpen, onClose, listId }: ShareListModalProps) {
  const [shareData, setShareData] = useState<ListSyncResponse | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    if (isOpen && !shareData) {
      generateShareCode();
    }
  }, [isOpen]);

  const generateShareCode = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const response = await api.post<ListSyncResponse>(`/lists/${listId}/share`);
      setShareData(response.data);
    } catch (err) {
      setError('Failed to generate share code');
    } finally {
      setIsLoading(false);
    }
  };

  const getSyncUrl = () => {
    if (!shareData) return '';
    return `${window.location.origin}/sync/${shareData.share_code}`;
  };

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(getSyncUrl());
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch {
      // Fallback for older browsers
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Share Your List" size="md">
      <div className="text-center py-4">
        {isLoading && (
          <div className="flex items-center justify-center h-48">
            <div className="w-8 h-8 border-4 border-primary-600 border-t-transparent rounded-full animate-spin" />
          </div>
        )}

        {error && (
          <div className="text-red-600 py-8">
            <p>{error}</p>
            <Button variant="outline" onClick={generateShareCode} className="mt-4">
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
```

**Step 4: Update barrel export**

```tsx
// frontend/src/components/qr/index.ts
export { QRCodeDisplay } from './QRCodeDisplay';
export { ShareListModal } from './ShareListModal';
```

**Step 5: Run tests**

Run: `cd frontend && npm test -- --run src/components/qr/`
Expected: PASS

**Step 6: Commit**

```bash
git add frontend/src/components/qr/ frontend/src/services/
git commit -m "feat(frontend): add ShareListModal component"
```

---

## Task 4: Integrate Share Button into ListPage

**Files:**
- Modify: `frontend/src/pages/ListPage.tsx`

**Step 1: Add share button and modal**

Update ListPage.tsx to include:

```tsx
import { useState } from 'react';
import { ShareListModal } from '@/components/qr';

// Inside component, add state:
const [showShareModal, setShowShareModal] = useState(false);

// Add button next to Clear List:
<Button variant="secondary" onClick={() => setShowShareModal(true)}>
  <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
  </svg>
  Share List
</Button>

// Add modal at bottom:
{currentList && (
  <ShareListModal
    isOpen={showShareModal}
    onClose={() => setShowShareModal(false)}
    listId={currentList.list_id}
  />
)}
```

**Step 2: Test manually**

Run: `cd frontend && npm run dev`
Navigate to /list, click Share List, verify QR code displays

**Step 3: Commit**

```bash
git add frontend/src/pages/ListPage.tsx
git commit -m "feat(frontend): add share button to ListPage"
```

---

## Task 5: Create QRScanner Component

**Files:**
- Create: `frontend/src/components/qr/QRScanner.tsx`
- Modify: `frontend/src/components/qr/index.ts`
- Test: `frontend/src/components/qr/__tests__/QRScanner.test.tsx`

**Step 1: Write the failing test**

```tsx
// frontend/src/components/qr/__tests__/QRScanner.test.tsx
import { render, screen } from '@testing-library/react';
import { QRScanner } from '../QRScanner';

describe('QRScanner', () => {
  it('renders scanner container when active', () => {
    render(<QRScanner isActive={true} onScan={vi.fn()} />);
    expect(screen.getByTestId('qr-scanner')).toBeInTheDocument();
  });

  it('does not render when inactive', () => {
    render(<QRScanner isActive={false} onScan={vi.fn()} />);
    expect(screen.queryByTestId('qr-scanner')).not.toBeInTheDocument();
  });

  it('shows camera instructions', () => {
    render(<QRScanner isActive={true} onScan={vi.fn()} />);
    expect(screen.getByText(/point your camera/i)).toBeInTheDocument();
  });
});
```

**Step 2: Implement QRScanner**

```tsx
// frontend/src/components/qr/QRScanner.tsx
import { useEffect, useRef, useState } from 'react';
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

  useEffect(() => {
    if (!isActive) {
      stopScanner();
      return;
    }

    startScanner();

    return () => {
      stopScanner();
    };
  }, [isActive]);

  const startScanner = async () => {
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
      const message = err instanceof Error ? err.message : 'Camera access denied';
      setError(message);
      onError?.(err instanceof Error ? err : new Error(message));
    }
  };

  const stopScanner = async () => {
    if (scannerRef.current) {
      try {
        await scannerRef.current.stop();
        scannerRef.current.clear();
      } catch {
        // Ignore stop errors
      }
      scannerRef.current = null;
    }
  };

  if (!isActive) return null;

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
          <svg className="w-12 h-12 text-red-500 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
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
```

**Step 3: Update barrel export**

```tsx
// frontend/src/components/qr/index.ts
export { QRCodeDisplay } from './QRCodeDisplay';
export { ShareListModal } from './ShareListModal';
export { QRScanner } from './QRScanner';
```

**Step 4: Run tests**

Run: `cd frontend && npm test -- --run src/components/qr/__tests__/QRScanner.test.tsx`
Expected: PASS

**Step 5: Commit**

```bash
git add frontend/src/components/qr/
git commit -m "feat(frontend): add QRScanner component"
```

---

## Task 6: Create SyncPage

**Files:**
- Create: `frontend/src/pages/SyncPage.tsx`
- Modify: `frontend/src/App.tsx` (add route)

**Step 1: Implement SyncPage**

```tsx
// frontend/src/pages/SyncPage.tsx
import { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { QRScanner } from '@/components/qr';
import { Button } from '@/components/ui';
import api from '@/services/api';
import { useListStore } from '@/store';

export function SyncPage() {
  const { code } = useParams<{ code?: string }>();
  const navigate = useNavigate();
  const { fetchCurrentList } = useListStore();

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
      await api.post(`/lists/sync/${shareCode}`);
      await fetchCurrentList();
      navigate('/list');
    } catch (err) {
      setError('Could not find a list with that code. Please try again.');
      setIsLoading(false);
    }
  };

  const handleScan = (data: string) => {
    // Extract code from URL if full URL scanned
    const match = data.match(/\/sync\/([A-Z0-9]+)/i);
    const shareCode = match ? match[1] : data;
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
              <label htmlFor="code" className="block text-sm font-medium text-gray-700 mb-1">
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
            <Button type="submit" className="w-full" disabled={!manualCode.trim()}>
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
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v1m6 11h2m-6 0h-2v4m0-11v3m0 0h.01M12 12h4.01M16 20h4M4 12h4m12 0h.01M5 8h2a1 1 0 001-1V5a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1zm12 0h2a1 1 0 001-1V5a1 1 0 00-1-1h-2a1 1 0 00-1 1v2a1 1 0 001 1zM5 20h2a1 1 0 001-1v-2a1 1 0 00-1-1H5a1 1 0 00-1 1v2a1 1 0 001 1z" />
            </svg>
            Scan QR Code
          </Button>
        </div>
      )}
    </div>
  );
}
```

**Step 2: Add route to App.tsx**

```tsx
// Add import
import { SyncPage } from './pages/SyncPage';

// Add route inside Routes
<Route path="/sync/:code?" element={<SyncPage />} />
```

**Step 3: Test manually**

Run: `cd frontend && npm run dev`
Navigate to /sync, verify scanner loads or manual entry works

**Step 4: Commit**

```bash
git add frontend/src/pages/SyncPage.tsx frontend/src/App.tsx
git commit -m "feat(frontend): add SyncPage for QR code sync"
```

---

## Task 7: Create UI Polish Components

**Files:**
- Create: `frontend/src/components/ui/LoadingSkeleton.tsx`
- Create: `frontend/src/components/ui/ErrorDisplay.tsx`
- Create: `frontend/src/components/ui/EmptyState.tsx`
- Modify: `frontend/src/components/ui/index.ts`

**Step 1: Create LoadingSkeleton**

```tsx
// frontend/src/components/ui/LoadingSkeleton.tsx
import classNames from 'classnames';

interface SkeletonProps {
  className?: string;
}

export function Skeleton({ className }: SkeletonProps) {
  return (
    <div
      className={classNames(
        'animate-pulse bg-gray-200 rounded',
        className
      )}
    />
  );
}

export function ProductCardSkeleton() {
  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4">
      <Skeleton className="w-full h-40 mb-4" />
      <Skeleton className="h-4 w-3/4 mb-2" />
      <Skeleton className="h-3 w-1/2 mb-4" />
      <Skeleton className="h-8 w-20" />
    </div>
  );
}

export function ListItemSkeleton() {
  return (
    <div className="flex items-center gap-4 py-4">
      <Skeleton className="w-16 h-16 rounded-lg" />
      <div className="flex-1">
        <Skeleton className="h-4 w-3/4 mb-2" />
        <Skeleton className="h-3 w-1/4" />
      </div>
      <Skeleton className="h-8 w-16" />
    </div>
  );
}

export function TextSkeleton({ className }: SkeletonProps) {
  return <Skeleton className={classNames('h-4', className)} />;
}
```

**Step 2: Create ErrorDisplay**

```tsx
// frontend/src/components/ui/ErrorDisplay.tsx
import { Button } from './Button';

interface ErrorDisplayProps {
  title?: string;
  message: string;
  onRetry?: () => void;
}

export function ErrorDisplay({
  title = 'Something went wrong',
  message,
  onRetry,
}: ErrorDisplayProps) {
  return (
    <div className="text-center py-12 px-4">
      <svg
        className="w-16 h-16 text-red-500 mx-auto mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={1.5}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
      <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">{message}</p>
      {onRetry && (
        <Button variant="outline" onClick={onRetry}>
          Try Again
        </Button>
      )}
    </div>
  );
}
```

**Step 3: Create EmptyState**

```tsx
// frontend/src/components/ui/EmptyState.tsx
import { ReactNode } from 'react';
import { Button } from './Button';

interface EmptyStateProps {
  icon?: ReactNode;
  title: string;
  description: string;
  action?: {
    label: string;
    onClick: () => void;
  };
}

export function EmptyState({ icon, title, description, action }: EmptyStateProps) {
  return (
    <div className="text-center py-12 px-4">
      {icon && (
        <div className="flex justify-center mb-4 text-gray-300">
          {icon}
        </div>
      )}
      <h2 className="text-xl font-semibold text-gray-900 mb-2">{title}</h2>
      <p className="text-gray-500 mb-6 max-w-md mx-auto">{description}</p>
      {action && (
        <Button onClick={action.onClick}>{action.label}</Button>
      )}
    </div>
  );
}
```

**Step 4: Update barrel export**

```tsx
// frontend/src/components/ui/index.ts
export { Button } from './Button';
export { Modal } from './Modal';
export { Skeleton, ProductCardSkeleton, ListItemSkeleton, TextSkeleton } from './LoadingSkeleton';
export { ErrorDisplay } from './ErrorDisplay';
export { EmptyState } from './EmptyState';
```

**Step 5: Run linting**

Run: `cd frontend && npm run lint`
Expected: No errors

**Step 6: Commit**

```bash
git add frontend/src/components/ui/
git commit -m "feat(frontend): add UI polish components (skeleton, error, empty)"
```

---

## Task 8: Apply Loading States to Pages

**Files:**
- Modify: `frontend/src/pages/SearchResultsPage.tsx`
- Modify: `frontend/src/pages/CategoryPage.tsx`

**Step 1: Add loading skeletons to SearchResultsPage**

Update SearchResultsPage to show ProductCardSkeleton while loading:

```tsx
import { ProductCardSkeleton } from '@/components/ui';

// In the loading state section:
{isLoading && (
  <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-4">
    {Array.from({ length: 8 }).map((_, i) => (
      <ProductCardSkeleton key={i} />
    ))}
  </div>
)}
```

**Step 2: Add loading skeletons to CategoryPage**

Similar update for CategoryPage.

**Step 3: Test manually**

Run: `cd frontend && npm run dev`
Search for products, verify skeletons show during loading

**Step 4: Commit**

```bash
git add frontend/src/pages/
git commit -m "feat(frontend): add loading skeletons to pages"
```

---

## Task 9: Apply Error and Empty States

**Files:**
- Modify: `frontend/src/pages/SearchResultsPage.tsx`
- Modify: `frontend/src/pages/ListPage.tsx`

**Step 1: Add error handling to SearchResultsPage**

```tsx
import { ErrorDisplay, EmptyState } from '@/components/ui';

// Error state
{error && (
  <ErrorDisplay
    message="Failed to load search results"
    onRetry={refetch}
  />
)}

// Empty state
{!isLoading && results.length === 0 && (
  <EmptyState
    icon={<svg className="w-24 h-24" ...>...</svg>}
    title="No results found"
    description={`We couldn't find any products matching "${query}"`}
    action={{ label: 'Clear Search', onClick: () => navigate('/') }}
  />
)}
```

**Step 2: Update ListPage empty state**

Replace inline empty state with EmptyState component.

**Step 3: Test manually**

Verify error and empty states display correctly

**Step 4: Commit**

```bash
git add frontend/src/pages/
git commit -m "feat(frontend): add error and empty states to pages"
```

---

## Task 10: Run Full Test Suite

**Step 1: Run all frontend tests**

Run: `cd frontend && npm test -- --run`
Expected: All tests pass

**Step 2: Run lint**

Run: `cd frontend && npm run lint`
Expected: No errors

**Step 3: Run type check**

Run: `cd frontend && npm run type-check`
Expected: No errors

**Step 4: Build for production**

Run: `cd frontend && npm run build`
Expected: Build succeeds

**Step 5: Final commit**

```bash
git add .
git commit -m "feat(frontend): complete Phase 5 QR sync and UI polish"
```

---

## Task 11: Update TODO.md

**Step 1: Mark Phase 5 complete**

Update TODO.md to mark all Phase 5 items as done.

**Step 2: Commit**

```bash
git add TODO.md
git commit -m "docs: mark Phase 5 complete"
```
