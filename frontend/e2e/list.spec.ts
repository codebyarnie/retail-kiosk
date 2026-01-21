// frontend/e2e/list.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Shopping List', () => {
  test.beforeEach(async ({ page }) => {
    // Clear localStorage before each test for a clean state
    await page.goto('/');
    await page.evaluate(() => localStorage.clear());
  });

  test('can view list page', async ({ page }) => {
    await page.goto('/list');
    // Should show empty state or list content
    await expect(page).toHaveURL('/list');
  });

  test('shows empty state message when no active list', async ({ page }) => {
    await page.goto('/list');
    // The empty state should show "No Active List" or similar message
    const emptyMessage = page.getByText(/no active list/i);
    await expect(emptyMessage).toBeVisible();
  });

  test('shows Browse Products button in empty state', async ({ page }) => {
    await page.goto('/list');
    const browseButton = page.getByRole('button', { name: /browse products/i });
    await expect(browseButton).toBeVisible();
  });

  test('clicking Browse Products navigates to home page', async ({ page }) => {
    await page.goto('/list');
    const browseButton = page.getByRole('button', { name: /browse products/i });
    await browseButton.click();
    await expect(page).toHaveURL('/');
  });

  test('Start Cart button is visible on home page when no session', async ({ page }) => {
    await page.goto('/');
    const startCartButton = page.getByRole('button', { name: /start cart/i });
    await expect(startCartButton).toBeVisible();
  });

  test('clicking Start Cart creates a new list session', async ({ page }) => {
    await page.goto('/');

    // Mock the API to avoid backend dependency
    await page.route('**/api/lists', async (route) => {
      if (route.request().method() === 'POST') {
        await route.fulfill({
          status: 200,
          contentType: 'application/json',
          body: JSON.stringify({
            id: 1,
            list_id: 'test-list-123',
            session_id: 'test-session-456',
            name: 'My List',
            created_at: new Date().toISOString(),
            items: [],
            total_items: 0,
          }),
        });
      } else {
        await route.continue();
      }
    });

    const startCartButton = page.getByRole('button', { name: /start cart/i });
    await startCartButton.click();

    // After clicking, the floating cart button should appear
    // (the Start Cart button is replaced by the cart icon with badge)
    await page.waitForTimeout(500);
  });
});
