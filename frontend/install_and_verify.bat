@echo off
REM ===================================================================
REM Frontend Installation & Verification Script (Windows)
REM
REM This script installs all frontend dependencies and verifies
REM that the application is ready for development.
REM
REM Usage:
REM   install_and_verify.bat
REM
REM Requirements:
REM   - Node.js 18+ and npm 9+
REM ===================================================================

setlocal enabledelayedexpansion

REM Change to script directory
cd /d "%~dp0"

echo ===================================================================
echo   Frontend Installation ^& Verification
echo ===================================================================
echo.

REM Check Node.js installation
echo [*] Checking Node.js version...
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed
    echo [INFO] Please install Node.js 18+ from https://nodejs.org/
    exit /b 1
)

REM Get Node.js version
for /f "tokens=1 delims=." %%a in ('node -v') do (
    set NODE_VERSION=%%a
)
set NODE_VERSION=%NODE_VERSION:~1%

if %NODE_VERSION% LSS 18 (
    echo [ERROR] Node.js version is too old ^(requires 18+^)
    for /f "delims=" %%v in ('node -v') do set CURRENT_VERSION=%%v
    echo [INFO] Current version: !CURRENT_VERSION!
    echo [INFO] Please upgrade to Node.js 18+ from https://nodejs.org/
    exit /b 1
)

for /f "delims=" %%v in ('node -v') do (
    echo [OK] Node.js %%v is installed
)

REM Check npm installation
echo.
echo [*] Checking npm version...
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] npm is not installed
    echo [INFO] npm usually comes with Node.js. Please reinstall Node.js.
    exit /b 1
)

for /f "tokens=1 delims=." %%a in ('npm -v') do (
    set NPM_VERSION=%%a
)

if %NPM_VERSION% LSS 9 (
    echo [WARNING] npm version is older than recommended 9+
    for /f "delims=" %%v in ('npm -v') do (
        echo [INFO] Current version: %%v
    )
    echo [INFO] Upgrading npm...
    call npm install -g npm@latest
)

for /f "delims=" %%v in ('npm -v') do (
    echo [OK] npm %%v is installed
)

REM Check package.json
echo.
echo [*] Checking package.json...
if not exist "package.json" (
    echo [ERROR] package.json not found in %CD%
    exit /b 1
)
echo [OK] package.json found

REM Clean install if node_modules exists
if exist "node_modules" (
    echo.
    echo [*] Cleaning existing node_modules...
    rmdir /s /q node_modules 2>nul
    del /f /q package-lock.json 2>nul
)

REM Install dependencies
echo.
echo [*] Installing frontend dependencies...
echo [INFO] This may take a few minutes...
echo.

call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install dependencies
    exit /b 1
)

echo [OK] Dependencies installed successfully

REM Run type check
echo.
echo [*] Running TypeScript type check...
call npm run type-check
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] TypeScript type check failed
    exit /b 1
)
echo [OK] TypeScript type check passed

REM Run linter
echo.
echo [*] Running ESLint check...
call npm run lint
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] ESLint check found issues ^(non-blocking^)
) else (
    echo [OK] ESLint check passed
)

REM Run build
echo.
echo [*] Running production build...
call npm run build
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Production build failed
    exit /b 1
)
echo [OK] Production build successful

if exist "dist" (
    echo [OK] Build output created: dist\
)

REM Success summary
echo.
echo ===================================================================
echo [OK] Frontend installation and verification complete!
echo ===================================================================
echo.
echo Next steps:
echo   1. Copy .env.example to .env:
echo      copy .env.example .env
echo.
echo   2. Configure environment variables in .env
echo.
echo   3. Start development server:
echo      npm run dev
echo.
echo   4. Visit http://localhost:5173 in your browser
echo.
echo Happy coding! 🚀
echo.

endlocal
exit /b 0
