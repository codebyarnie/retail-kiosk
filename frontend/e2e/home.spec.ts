// frontend/e2e/home.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Home Page', () => {
  test('loads successfully with correct title', async ({ page }) => {
    await page.goto('/');
    await expect(page).toHaveTitle(/Retail Kiosk/i);
  });

  test('displays search bar with placeholder', async ({ page }) => {
    await page.goto('/');
    const searchInput = page.getByPlaceholder(/search for products/i);
    await expect(searchInput).toBeVisible();
  });

  test('displays hero section with heading', async ({ page }) => {
    await page.goto('/');
    const heading = page.getByRole('heading', { name: /find what you need/i });
    await expect(heading).toBeVisible();
  });

  test('displays Browse Categories section', async ({ page }) => {
    await page.goto('/');
    const categoriesHeading = page.getByRole('heading', { name: /browse categories/i });
    await expect(categoriesHeading).toBeVisible();
  });

  test('displays Start Cart button when no session exists', async ({ page }) => {
    // Clear storage to ensure no session
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
    await page.reload();

    const startCartButton = page.getByRole('button', { name: /start cart/i });
    await expect(startCartButton).toBeVisible();
  });
});
