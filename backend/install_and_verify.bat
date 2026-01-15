@echo off
REM Backend installation and verification script for Windows
REM
REM This script installs all backend dependencies and verifies the installation.
REM
REM Usage:
REM   cd backend
REM   install_and_verify.bat

setlocal enabledelayedexpansion

echo =====================================================================
echo Backend Installation and Verification
echo =====================================================================
echo.

REM Check if we're in the backend directory
if not exist "requirements.txt" (
    echo Error: requirements.txt not found.
    echo Please run this script from the backend\ directory.
    exit /b 1
)

REM Check if Python is available
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    where py >nul 2>&1
    if !ERRORLEVEL! NEQ 0 (
        echo Error: Python not found in PATH.
        echo Please install Python 3.11 or higher.
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% --version
echo.

REM Check Python version (should be 3.11+)
echo Checking Python version...
%PYTHON_CMD% -c "import sys; assert sys.version_info >= (3, 11), 'Python 3.11+ required'; print('✓ Python version OK')"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Python 3.11 or higher is required.
    exit /b 1
)
echo.

REM Install dependencies
echo Installing backend dependencies...
echo This may take a few minutes...
echo.

%PYTHON_CMD% -m pip install --upgrade pip setuptools wheel
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to upgrade pip.
    exit /b 1
)

%PYTHON_CMD% -m pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error: Failed to install dependencies.
    exit /b 1
)

echo.
echo ✓ Dependencies installed successfully!
echo.

REM Run verification script
echo Running verification checks...
echo.

%PYTHON_CMD% verify_installation.py

REM Check exit code
if %ERRORLEVEL% EQU 0 (
    echo.
    echo =====================================================================
    echo ✅ Backend installation and verification COMPLETED!
    echo =====================================================================
    echo.
    echo Next steps:
    echo   1. Copy .env.example to .env and configure environment variables
    echo   2. Start the development server: uvicorn app.main:app --reload
    echo   3. Visit http://localhost:8000/api/docs for API documentation
    echo.
    exit /b 0
) else (
    echo.
    echo =====================================================================
    echo ❌ Backend verification FAILED!
    echo =====================================================================
    echo.
    echo Please review the errors above and fix any issues.
    echo.
    exit /b 1
)

endlocal
