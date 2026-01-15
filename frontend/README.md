# Retail Kiosk - Frontend Service

Modern, responsive frontend application for the Retail Kiosk point-of-sale system, built with React, TypeScript, and Vite.

## 🚀 Quick Start

### Installation

#### Option 1: Automated Install (Recommended)

**Linux/macOS:**
```bash
bash install_and_verify.sh
```

**Windows:**
```cmd
install_and_verify.bat
```

#### Option 2: Manual Install

```bash
# Check Node.js version (18+ required)
node -v

# Install dependencies
npm install

# Verify installation
node verify_installation.js

# Run type check
npm run type-check

# Build for production
npm run build
```

### Configuration

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Configure environment variables in `.env`:
   ```env
   VITE_API_BASE_URL=http://localhost:8000
   VITE_APP_TITLE=Retail Kiosk
   VITE_APP_VERSION=0.1.0
   ```

### Development Server

Start the Vite development server:

```bash
npm run dev
```

The application will be available at: **http://localhost:5173**

Features:
- ⚡ Hot Module Replacement (HMR)
- 🔄 Fast refresh for React components
- 🔍 TypeScript type checking in IDE
- 🎨 Automatic CSS updates

## 📁 Project Structure

```
frontend/
├── src/
│   ├── main.tsx              # Application entry point
│   ├── App.tsx               # Root component
│   ├── App.css               # Root component styles
│   ├── index.css             # Global styles
│   ├── components/           # Reusable UI components
│   ├── pages/                # Page components
│   ├── hooks/                # Custom React hooks
│   ├── services/             # API service layer
│   ├── store/                # State management (Zustand)
│   ├── types/                # TypeScript type definitions
│   ├── utils/                # Utility functions
│   └── assets/               # Static assets (images, fonts)
├── public/                   # Public static files
├── index.html                # HTML entry point
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
├── .eslintrc.json            # ESLint configuration
├── .prettierrc               # Prettier configuration
└── package.json              # Dependencies and scripts
```

## 🛠️ Development

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server (port 5173) |
| `npm run build` | Build for production |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint |
| `npm run lint:fix` | Fix ESLint issues automatically |
| `npm run format` | Format code with Prettier |
| `npm run format:check` | Check code formatting |
| `npm run type-check` | Run TypeScript type checking |
| `npm test` | Run tests with Vitest |
| `npm run test:ui` | Run tests with UI |
| `npm run test:coverage` | Generate test coverage report |

### Code Quality Tools

#### ESLint
Lint JavaScript/TypeScript code:
```bash
# Check for issues
npm run lint

# Auto-fix issues
npm run lint:fix
```

Configuration: `.eslintrc.json`
- TypeScript support with `@typescript-eslint`
- React hooks rules
- React Refresh for HMR
- Prettier integration

#### Prettier
Format code consistently:
```bash
# Check formatting
npm run format:check

# Auto-format
npm run format
```

Configuration: `.prettierrc`
- 80 character line width
- 2-space indentation
- Single quotes
- Semicolons enabled

#### TypeScript
Type checking:
```bash
npm run type-check
```

Configuration: `tsconfig.json`
- Strict mode enabled
- ES2020 target
- Modern module resolution
- Path aliases: `@/*` → `src/*`

### Testing

Run tests with Vitest:

```bash
# Run all tests
npm test

# Run with UI
npm run test:ui

# Generate coverage report
npm run test:coverage
```

Configuration in `vite.config.ts`:
- `jsdom` environment for DOM testing
- Coverage reporting with v8
- Global test utilities

### State Management

Using **Zustand** for state management:

```typescript
// Example store
import { create } from 'zustand';

interface CartStore {
  items: CartItem[];
  addItem: (item: CartItem) => void;
  removeItem: (id: string) => void;
}

const useCartStore = create<CartStore>((set) => ({
  items: [],
  addItem: (item) => set((state) => ({
    items: [...state.items, item]
  })),
  removeItem: (id) => set((state) => ({
    items: state.items.filter(item => item.id !== id)
  })),
}));
```

### API Integration

Using **axios** for HTTP requests:

```typescript
// Example API service
import axios from 'axios';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 10000,
});

export const getProducts = async () => {
  const response = await api.get('/api/products');
  return response.data;
};
```

Using **React Query** for data fetching:

```typescript
import { useQuery } from 'react-query';

function ProductList() {
  const { data, isLoading, error } = useQuery(
    'products',
    getProducts
  );

  if (isLoading) return <div>Loading...</div>;
  if (error) return <div>Error loading products</div>;

  return <div>{/* Render products */}</div>;
}
```

## 📦 Dependencies

### Core Dependencies

| Package | Version | Description |
|---------|---------|-------------|
| `react` | ^18.2.0 | UI library |
| `react-dom` | ^18.2.0 | React DOM rendering |
| `react-router-dom` | ^6.21.1 | Client-side routing |
| `axios` | ^1.6.5 | HTTP client |
| `zustand` | ^4.4.7 | State management |
| `react-query` | ^3.39.3 | Data fetching and caching |
| `classnames` | ^2.5.1 | Conditional CSS classes |

### Development Dependencies

| Package | Version | Description |
|---------|---------|-------------|
| `typescript` | ^5.3.3 | TypeScript compiler |
| `vite` | ^5.0.11 | Build tool and dev server |
| `@vitejs/plugin-react` | ^4.2.1 | Vite React plugin |
| `vitest` | ^1.2.0 | Testing framework |
| `@vitest/ui` | ^1.2.0 | Vitest UI |
| `jsdom` | ^23.2.0 | DOM implementation for tests |
| `eslint` | ^8.56.0 | Linter |
| `prettier` | ^3.2.4 | Code formatter |
| `tailwindcss` | ^3.4.1 | Utility-first CSS framework |
| `autoprefixer` | ^10.4.16 | PostCSS plugin for vendor prefixes |
| `postcss` | ^8.4.33 | CSS transformer |

## 🐳 Docker

### Build Docker Image

```bash
# Build image
docker build -t retail-kiosk-frontend:latest .

# Run container
docker run -p 8080:80 retail-kiosk-frontend:latest
```

The production Docker image:
- Uses multi-stage build for minimal size
- Runs nginx:1.25-alpine for serving
- Includes custom nginx configuration
- Supports SPA routing (all routes → index.html)
- Adds security headers
- Enables gzip compression
- Configures static asset caching
- Health check endpoint: `/health`

### Using Docker Compose

From the project root:

```bash
# Start all services (including frontend)
make up

# Or manually
docker-compose up -d

# View logs
docker-compose logs -f frontend

# Stop services
docker-compose down
```

## 🌐 Environment Variables

All frontend environment variables must be prefixed with `VITE_` to be available in the browser.

### Application Settings

```env
# API Configuration
VITE_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=10000

# Application Info
VITE_APP_TITLE=Retail Kiosk
VITE_APP_VERSION=0.1.0
VITE_APP_ENVIRONMENT=development

# Feature Flags
VITE_FEATURE_BARCODE_SCANNER=true
VITE_FEATURE_CASH_DRAWER=true
VITE_FEATURE_RECEIPT_PRINTER=true
VITE_FEATURE_CUSTOMER_DISPLAY=false

# UI Configuration
VITE_UI_THEME=light
VITE_UI_LANGUAGE=en
VITE_UI_CURRENCY=USD

# Performance
VITE_ENABLE_DEVTOOLS=true
VITE_ENABLE_PROFILER=false
VITE_ENABLE_STRICT_MODE=true
```

See `.env.example` for the complete list of available environment variables.

## 🔧 Troubleshooting

### Common Issues

#### Port 5173 already in use

```bash
# Kill process using port 5173
# Linux/macOS
lsof -ti:5173 | xargs kill -9

# Windows (Command Prompt)
netstat -ano | findstr :5173
taskkill /PID <PID> /F
```

Or use a different port:
```bash
npm run dev -- --port 3000
```

#### Dependencies not installing

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and lockfile
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

#### Type checking errors

```bash
# Restart TypeScript server in VS Code
# Ctrl+Shift+P → "TypeScript: Restart TS Server"

# Or rebuild type definitions
npm run type-check
```

#### Build errors

```bash
# Clean build artifacts
rm -rf dist

# Rebuild
npm run build
```

### Getting Help

- Check [Vite documentation](https://vitejs.dev/)
- Review [React documentation](https://react.dev/)
- See project README in root directory
- Check GitHub issues

## 📚 Additional Resources

- [React Best Practices](https://react.dev/learn)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Vite Guide](https://vitejs.dev/guide/)
- [Vitest Documentation](https://vitest.dev/)
- [React Query Guide](https://tanstack.com/query/latest)
- [Zustand Documentation](https://docs.pmnd.rs/zustand/getting-started/introduction)

## 📄 License

UNLICENSED - Private project for Retail Kiosk application.
