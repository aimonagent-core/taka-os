// File: frontend/e2e/hil.spec.ts
// Purpose: E2E tests for HIL dashboard

import { test, expect } from "@playwright/test";

test.describe("HIL", () => {
  test("hil page loads", async ({ page }) => {
    await page.goto("/hil");
    await expect(page.locator("h2")).toContainText("Human-in-the-Loop");
    await expect(page.locator("h3")).toContainText("HIL Pending Requests");
  });

  test("refresh button is present", async ({ page }) => {
    await page.goto("/hil");
    await expect(page.locator("button", { hasText: "Refresh" })).toBeVisible();
  });
});
