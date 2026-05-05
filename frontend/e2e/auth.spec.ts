// File: frontend/e2e/auth.spec.ts
// Purpose: E2E tests for authentication flows

import { test, expect } from "@playwright/test";

test.describe("Authentication", () => {
  test("login page loads", async ({ page }) => {
    await page.goto("/login");
    await expect(page.locator("h2")).toContainText("Login");
  });

  test("register page loads", async ({ page }) => {
    await page.goto("/register");
    await expect(page.locator("h2")).toContainText("Register");
  });

  test("navigates to dashboard after login", async ({ page }) => {
    await page.goto("/login");
    await page.fill('input[type="email"]', "test@example.com");
    await page.fill('input[type="password"]', "password123");
    await page.click('button[type="submit"]');
    await expect(page).toHaveURL(/.*dashboard/);
  });
});
