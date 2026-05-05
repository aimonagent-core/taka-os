// File: frontend/e2e/documents.spec.ts
// Purpose: E2E tests for document upload and parsing

import { test, expect } from "@playwright/test";

test.describe("Documents", () => {
  test("documents page loads", async ({ page }) => {
    await page.goto("/documents");
    await expect(page.locator("h2")).toContainText("Documents");
    await expect(page.locator("h3")).toContainText("Upload Document");
  });

  test("upload button is disabled without file", async ({ page }) => {
    await page.goto("/documents");
    const btn = page.locator('button[type="submit"]');
    await expect(btn).toBeDisabled();
  });
});
