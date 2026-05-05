import { test as setup, expect } from '@playwright/test';
import path from 'path';

const authFile = path.join(__dirname, '../playwright/.auth/user.json');

setup('authenticate', async ({ page }) => {
  await page.goto('http://localhost:5173/login');
  await page.fill('[data-testid="email-input"]', 'test@taka.os');
  await page.fill('[data-testid="password-input"]', 'TestPass123!');
  await page.click('[data-testid="login-button"]');
  await page.waitForURL('http://localhost:5173/dashboard', { timeout: 10000 });
  await expect(page.locator('[data-testid="dashboard-welcome"]')).toBeVisible();
  await page.context().storageState({ path: authFile });
});
