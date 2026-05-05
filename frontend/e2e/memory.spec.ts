// File: frontend/e2e/memory.spec.ts
// Purpose: E2E tests for memory search

import { test, expect } from "@playwright/test";

test.describe("Memory", () => {
  test("memory page loads", async ({ page }) => {
    await page.goto("/memory");
    await expect(page.locator("h2")).toContainText("Memory");
    await expect(page.locator("h3")).toContainText("Memory Search");
  });

  test("search input is present", async ({ page }) => {
    await page.goto("/memory");
    await expect(page.locator('input[placeholder="Search memory..."]')).toBeVisible();
  });
});
