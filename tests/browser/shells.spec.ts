import { expect, test } from '@playwright/test';

test('renders English and Arabic public shells with correct direction', async ({
  page,
}) => {
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('requestfailed', (request) => failedRequests.push(request.url()));

  await page.goto('/en-eg/');
  await expect(page.locator('html')).toHaveAttribute('dir', 'ltr');
  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'trustworthy',
  );
  await page.goto('/ar-eg/');
  await expect(page.locator('html')).toHaveAttribute('lang', 'ar-EG');
  await expect(page.locator('html')).toHaveAttribute('dir', 'rtl');
  await expect(page.getByRole('heading', { level: 1 })).toContainText(
    'مرجع تعليمي',
  );
  expect(consoleErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
});

test('renders the protected control sign-in shell', async ({ page }) => {
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('requestfailed', (request) => failedRequests.push(request.url()));
  await page.goto('http://127.0.0.1:4322/');
  await expect(page).toHaveURL('http://127.0.0.1:4322/login');
  await expect(
    page.getByRole('heading', { name: 'Staff sign in' }),
  ).toBeVisible();
  await expect(page.locator('meta[name="robots"]')).toHaveAttribute(
    'content',
    'noindex,nofollow',
  );
  expect(consoleErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
});

test('shells remain overflow-free at representative widths', async ({
  page,
}) => {
  for (const viewport of [
    { width: 1440, height: 900 },
    { width: 1024, height: 768 },
    { width: 768, height: 1024 },
    { width: 390, height: 844 },
  ]) {
    await page.setViewportSize(viewport);
    for (const url of [
      'http://127.0.0.1:4321/en-eg/',
      'http://127.0.0.1:4321/ar-eg/',
      'http://127.0.0.1:4322/',
    ]) {
      await page.goto(url);
      const hasOverflow = await page.evaluate(
        () =>
          document.documentElement.scrollWidth >
          document.documentElement.clientWidth,
      );
      expect(hasOverflow, `${url} at ${viewport.width}px`).toBe(false);
    }
  }
});
