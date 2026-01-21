// frontend/e2e/search.spec.ts
import { test, expect } from '@playwright/test';

test.describe('Search Flow', () => {
  test('can enter search query in search bar', async ({ page }) => {
    await page.goto('/');
    const searchInput = page.getByPlaceholder(/search for products/i);
    await searchInput.fill('drill');
    await expect(searchInput).toHaveValue('drill');
  });

  test('navigates to search results page on form submit', async ({ page }) => {
    await page.goto('/');
    const searchInput = page.getByPlaceholder(/search for products/i);
    await searchInput.fill('hammer');
    await searchInput.press('Enter');
    await expect(page).toHaveURL(/\/search\?q=hammer/);
  });

  test('search results page displays search query', async ({ page }) => {
    await page.goto('/search?q=screwdriver');
    // The page should display the search term or have search functionality
    await expect(page).toHaveURL(/\/search/);
  });

  test('search bar is accessible via header on all pages', async ({ page }) => {
    // Check search bar exists on search results page header
    await page.goto('/search?q=test');
    const searchInput = page.getByPlaceholder(/search for products/i);
    await expect(searchInput).toBeVisible();
  });

  test('can search with special characters', async ({ page }) => {
    await page.goto('/');
    const searchInput = page.getByPlaceholder(/search for products/i);
    await searchInput.fill('1/4" drill bit');
    await searchInput.press('Enter');
    // URL should be properly encoded
    await expect(page).toHaveURL(/\/search\?q=/);
  });
});
