"""
Backend installation verification script.

This script verifies that all backend dependencies are installed correctly
and that the main application can be imported without errors.

Usage:
    cd backend
    pip install -r requirements.txt
    python verify_installation.py
"""

import sys
from pathlib import Path


def verify_dependencies():
    """Verify all required dependencies can be imported."""
    print("Checking backend dependencies...")

    required_packages = [
        ("fastapi", "FastAPI framework"),
        ("uvicorn", "ASGI server"),
        ("pydantic", "Data validation"),
        ("pydantic_settings", "Settings management"),
        ("sqlalchemy", "Database ORM"),
        ("alembic", "Database migrations"),
        ("psycopg2", "PostgreSQL driver (sync)"),
        ("asyncpg", "PostgreSQL driver (async)"),
        ("redis", "Redis client"),
        ("qdrant_client", "Qdrant vector database client"),
        ("celery", "Distributed task queue"),
        ("httpx", "HTTP client"),
        ("jose", "JWT tokens"),
        ("passlib", "Password hashing"),
        ("loguru", "Logging"),
        ("pytest", "Testing framework"),
        ("ruff", "Linter"),
        ("black", "Code formatter"),
        ("mypy", "Type checker"),
    ]

    failed = []
    for package, description in required_packages:
        try:
            __import__(package)
            print(f"  ✓ {package:20s} - {description}")
        except ImportError as e:
            print(f"  ✗ {package:20s} - {description} (FAILED: {e})")
            failed.append(package)

    if failed:
        print(f"\n❌ Failed to import {len(failed)} package(s): {', '.join(failed)}")
        return False

    print(f"\n✓ All {len(required_packages)} required packages imported successfully!")
    return True


def verify_app_import():
    """Verify the FastAPI application can be imported."""
    print("\nChecking FastAPI application import...")

    try:
        # Add backend directory to Python path if not already there
        backend_dir = Path(__file__).parent
        if str(backend_dir) not in sys.path:
            sys.path.insert(0, str(backend_dir))

        from app.main import app

        print("  ✓ Successfully imported FastAPI app from app.main")
        print(f"  ✓ App title: {app.title}")
        print(f"  ✓ App version: {app.version}")
        print(f"  ✓ Docs URL: {app.docs_url}")

        return True
    except Exception as e:
        print(f"  ✗ Failed to import app.main: {e}")
        return False


def verify_config():
    """Verify the configuration module can be imported."""
    print("\nChecking configuration module...")

    try:
        from app.config import get_settings

        settings = get_settings()
        print("  ✓ Successfully imported and initialized settings")
        print(f"  ✓ App name: {settings.app_name}")
        print(f"  ✓ Environment: {settings.environment}")
        print(f"  ✓ Debug mode: {settings.debug}")

        return True
    except Exception as e:
        print(f"  ✗ Failed to import config: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("Backend Installation Verification")
    print("=" * 70)
    print()

    checks = [
        ("Dependencies", verify_dependencies),
        ("FastAPI Application", verify_app_import),
        ("Configuration", verify_config),
    ]

    results = []
    for name, check_func in checks:
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print(f"\n❌ Unexpected error in {name}: {e}")
            results.append((name, False))
        print()

    # Summary
    print("=" * 70)
    print("Verification Summary")
    print("=" * 70)

    all_passed = True
    for name, passed in results:
        status = "✓ PASSED" if passed else "✗ FAILED"
        print(f"  {status:10s} - {name}")
        if not passed:
            all_passed = False

    print()
    if all_passed:
        print("✅ Backend installation verification PASSED!")
        print("Backend imports OK")
        return 0
    else:
        print("❌ Backend installation verification FAILED!")
        print("\nPlease ensure all dependencies are installed:")
        print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
