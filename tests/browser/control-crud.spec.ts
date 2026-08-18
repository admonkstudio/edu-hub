import { expect, test } from '@playwright/test';

const email = process.env.CONTROL_QA_EMAIL;
const password = process.env.CONTROL_QA_PASSWORD;

test('authorized staff can create and edit a bilingual institution', async ({
  page,
}) => {
  test.skip(
    !email || !password,
    'Local QA staff credentials are not configured',
  );

  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];
  page.on('console', (message) => {
    if (message.type() === 'error') consoleErrors.push(message.text());
  });
  page.on('requestfailed', (request) => failedRequests.push(request.url()));

  await page.goto('http://127.0.0.1:4322/login');
  await page.getByLabel('Email').fill(email!);
  await page.getByLabel('Password').fill(password!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(
    page.getByRole('heading', { name: 'Institutions' }),
  ).toBeVisible();

  await page.getByRole('link', { name: 'Create institution' }).click();
  await page.getByLabel('Official name').fill('Milestone QA Learning Centre');
  await page.getByLabel('Institution type').selectOption({ index: 1 });
  await page
    .getByLabel('Name', { exact: true })
    .first()
    .fill('Milestone QA Learning Centre');
  await page
    .getByLabel('Slug', { exact: true })
    .fill(`milestone-qa-${Date.now()}`);
  await page.getByLabel('الاسم').fill('مركز اختبار المرحلة');
  await page.getByLabel('الرابط المختصر').fill(`اختبار-${Date.now()}`);
  await page.getByLabel('Campus name').fill('Main campus');
  await page.getByLabel('Governorate').selectOption({ index: 1 });
  await page.getByRole('button', { name: 'Create institution' }).click();

  await expect(page).toHaveURL(/\/institutions\/[0-9a-f-]+\?created=1$/);
  await expect(page.getByText('Institution created.')).toBeVisible();
  await page
    .getByLabel('Official name')
    .fill('Milestone QA Learning Centre Updated');
  await page.getByLabel('Change reason').fill('Browser QA update proof');
  await page.getByRole('button', { name: 'Save changes' }).click();
  await expect(page).toHaveURL(/\?saved=1$/);
  await expect(page.getByText('Changes saved.')).toBeVisible();

  expect(consoleErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
});
