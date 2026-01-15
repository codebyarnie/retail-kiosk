#!/usr/bin/env bash

#######################################
# Frontend Installation & Verification Script
#
# This script installs all frontend dependencies and verifies
# that the application is ready for development.
#
# Usage:
#   bash install_and_verify.sh
#
# Requirements:
#   - Node.js 18+ and npm 9+
#######################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  Frontend Installation & Verification${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

# Check Node.js version
echo -e "\n${BLUE}📦 Checking Node.js version...${NC}"
if ! command -v node &> /dev/null; then
    echo -e "${RED}✗ Node.js is not installed${NC}"
    echo -e "${YELLOW}  Please install Node.js 18+ from https://nodejs.org/${NC}"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo -e "${RED}✗ Node.js version $(node -v) is too old${NC}"
    echo -e "${YELLOW}  Please upgrade to Node.js 18+ from https://nodejs.org/${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Node.js $(node -v) is installed${NC}"

# Check npm version
echo -e "\n${BLUE}📦 Checking npm version...${NC}"
if ! command -v npm &> /dev/null; then
    echo -e "${RED}✗ npm is not installed${NC}"
    echo -e "${YELLOW}  npm usually comes with Node.js. Please reinstall Node.js.${NC}"
    exit 1
fi

NPM_VERSION=$(npm -v | cut -d'.' -f1)
if [ "$NPM_VERSION" -lt 9 ]; then
    echo -e "${YELLOW}⚠ npm version $(npm -v) is older than recommended 9+${NC}"
    echo -e "${YELLOW}  Upgrading npm...${NC}"
    npm install -g npm@latest
fi

echo -e "${GREEN}✓ npm $(npm -v) is installed${NC}"

# Navigate to frontend directory
cd "$SCRIPT_DIR"

# Check package.json exists
echo -e "\n${BLUE}📄 Checking package.json...${NC}"
if [ ! -f "package.json" ]; then
    echo -e "${RED}✗ package.json not found in $SCRIPT_DIR${NC}"
    exit 1
fi
echo -e "${GREEN}✓ package.json found${NC}"

# Clean install (remove existing node_modules if present)
if [ -d "node_modules" ]; then
    echo -e "\n${YELLOW}🧹 Cleaning existing node_modules...${NC}"
    rm -rf node_modules package-lock.json
fi

# Install dependencies
echo -e "\n${BLUE}📚 Installing frontend dependencies...${NC}"
echo -e "${YELLOW}  This may take a few minutes...${NC}"

if npm install; then
    echo -e "${GREEN}✓ Dependencies installed successfully${NC}"
else
    echo -e "${RED}✗ Failed to install dependencies${NC}"
    exit 1
fi

# Run type check
echo -e "\n${BLUE}🔍 Running TypeScript type check...${NC}"
if npm run type-check; then
    echo -e "${GREEN}✓ TypeScript type check passed${NC}"
else
    echo -e "${RED}✗ TypeScript type check failed${NC}"
    exit 1
fi

# Run linter
echo -e "\n${BLUE}🔍 Running ESLint check...${NC}"
if npm run lint; then
    echo -e "${GREEN}✓ ESLint check passed${NC}"
else
    echo -e "${YELLOW}⚠ ESLint check found issues (non-blocking)${NC}"
fi

# Run build
echo -e "\n${BLUE}🏗️  Running production build...${NC}"
if npm run build; then
    echo -e "${GREEN}✓ Production build successful${NC}"

    if [ -d "dist" ]; then
        DIST_SIZE=$(du -sh dist | cut -f1)
        echo -e "${GREEN}✓ Build output: dist/ (${DIST_SIZE})${NC}"
    fi
else
    echo -e "${RED}✗ Production build failed${NC}"
    exit 1
fi

# Success summary
echo -e "\n${BLUE}═══════════════════════════════════════════════════${NC}"
echo -e "${GREEN}✓ Frontend installation and verification complete!${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════${NC}"

echo -e "\n${BLUE}Next steps:${NC}"
echo -e "  1. ${YELLOW}Copy .env.example to .env:${NC}"
echo -e "     ${BLUE}cp .env.example .env${NC}"
echo -e ""
echo -e "  2. ${YELLOW}Configure environment variables in .env${NC}"
echo -e ""
echo -e "  3. ${YELLOW}Start development server:${NC}"
echo -e "     ${BLUE}npm run dev${NC}"
echo -e ""
echo -e "  4. ${YELLOW}Visit http://localhost:5173 in your browser${NC}"
echo -e ""
echo -e "${GREEN}Happy coding! 🚀${NC}\n"
