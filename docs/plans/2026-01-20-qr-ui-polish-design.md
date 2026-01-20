# Phase 5: QR Sync & UI Polish Design

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Enable kiosk users to share their shopping list via QR code and sync lists on mobile devices, with polished UI states.

**Architecture:** Frontend-only implementation using lightweight QR libraries. Backend share endpoints already exist (`POST /api/lists/{id}/share` returns share_code, `POST /api/lists/sync/{code}` clones list).

**Tech Stack:** react-qr-code (generation), html5-qrcode (scanning), existing React/Tailwind patterns

---

## 1. QR Code Components

### 1.1 QRCodeDisplay Component
Renders a QR code containing the sync URL for a list.

**Props:**
- `value: string` - The URL or data to encode
- `size?: number` - Size in pixels (default: 200)
- `className?: string` - Additional CSS classes

**Implementation:**
- Use `react-qr-code` package (lightweight, SVG-based)
- Encode full sync URL: `${window.location.origin}/sync/{share_code}`
- Include error correction level L (7%)

### 1.2 QRScanner Component
Camera-based QR code scanner using WebRTC.

**Props:**
- `onScan: (data: string) => void` - Callback when QR detected
- `onError?: (error: Error) => void` - Error callback
- `isActive: boolean` - Whether scanner is running

**Implementation:**
- Use `html5-qrcode` package (browser-native, widely compatible)
- Request camera permission on mount
- Parse scanned URL to extract share_code
- Auto-stop after successful scan

### 1.3 ShareListModal Component
Modal displaying QR code with share options.

**Features:**
- Generate share code via API call
- Display QR code (large, scannable on mobile)
- Show share code as text fallback
- Copy sync URL button
- Instructions for mobile users

**Integration:**
- Add "Share List" button to ListPage
- Add to FloatingCart expanded panel

---

## 2. Sync Flow

### 2.1 Sharing (Kiosk)
1. User clicks "Share List" on ListPage
2. Frontend calls `POST /api/lists/{id}/share`
3. Modal shows QR code with sync URL
4. User scans with phone

### 2.2 Receiving (Mobile)
1. User navigates to `/sync` page or scans QR
2. If direct URL: extract share_code from path
3. If scanning: QRScanner extracts code from QR
4. Call `POST /api/lists/sync/{code}`
5. List cloned to user's session
6. Redirect to `/list`

### 2.3 New Route
- `/sync/:code?` - Sync page with optional code parameter
- If code provided: auto-sync on load
- If no code: show QR scanner

---

## 3. UI Polish Components

### 3.1 LoadingSkeleton
Placeholder animations during data loading.

**Variants:**
- `ProductCardSkeleton` - Matches ProductCard dimensions
- `ListItemSkeleton` - Matches ListItemPreview dimensions
- `TextSkeleton` - Single line text placeholder

**Implementation:**
- Tailwind `animate-pulse` with gray backgrounds
- Match exact dimensions of target components

### 3.2 ErrorDisplay
User-friendly error messages.

**Props:**
- `title: string` - Error heading
- `message: string` - Detailed message
- `onRetry?: () => void` - Optional retry button

**Variants:**
- Network error (offline indicator)
- Not found (404)
- Server error (500)

### 3.3 EmptyState
Empty state illustrations with CTAs.

**Variants:**
- Empty search results
- Empty list
- No categories

**Props:**
- `icon: ReactNode` - SVG illustration
- `title: string` - Heading
- `description: string` - Helper text
- `action?: { label: string; onClick: () => void }` - CTA button

### 3.4 Touch-Friendly Enhancements
- Minimum 44x44px touch targets (existing Button already compliant)
- Larger click areas for list items
- Swipe-to-remove on list items (optional)
- Visual feedback on touch (active states)

---

## 4. Error Handling

### 4.1 QR Generation Errors
- API failure: Show error toast, retry button
- No list selected: Disable share button

### 4.2 QR Scanning Errors
- Camera permission denied: Show instructions to enable
- No camera available: Show manual code entry
- Invalid QR: Show "Not a valid share code" message
- Expired/invalid code: Show "List not found" with retry

### 4.3 Network Errors
- Offline: Show offline banner
- Timeout: Show retry button
- Server error: Show generic error with contact info

---

## 5. Testing Strategy

### 5.1 Unit Tests
- QRCodeDisplay renders SVG with correct data
- ShareListModal calls share API
- LoadingSkeleton matches snapshot
- EmptyState renders with all props

### 5.2 Integration Tests
- Full share flow: generate code → display QR
- Scanner detects QR codes (mock camera)
- Sync flow: scan → API call → redirect

### 5.3 E2E Tests (Playwright)
- Share list from ListPage
- Manual code entry sync
- Error state visibility

---

## 6. File Structure

```
frontend/src/
├── components/
│   ├── qr/
│   │   ├── QRCodeDisplay.tsx
│   │   ├── QRScanner.tsx
│   │   ├── ShareListModal.tsx
│   │   └── index.ts
│   ├── ui/
│   │   ├── LoadingSkeleton.tsx
│   │   ├── ErrorDisplay.tsx
│   │   ├── EmptyState.tsx
│   │   └── ... (existing)
│   └── ...
├── pages/
│   ├── SyncPage.tsx  (new)
│   └── ...
└── ...
```

---

## 7. Dependencies

**New packages:**
- `react-qr-code` - QR code generation (SVG-based, ~3KB gzipped)
- `html5-qrcode` - QR code scanning (~45KB gzipped)

Both are well-maintained with TypeScript support.
