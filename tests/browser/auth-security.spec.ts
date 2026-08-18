import { expect, test } from '@playwright/test';

const active = {
  email: process.env.CONTROL_QA_EMAIL,
  password: process.env.CONTROL_QA_PASSWORD,
};
const suspended = {
  email: process.env.SUSPENDED_QA_EMAIL,
  password: process.env.SUSPENDED_QA_PASSWORD,
};

test('active session refreshes after an invalid access token and logout revokes browser access', async ({
  context,
  page,
}) => {
  test.skip(
    !active.email || !active.password,
    'Active QA account is not configured',
  );
  await page.goto('http://127.0.0.1:4322/login');
  await page.getByLabel('Email').fill(active.email!);
  await page.getByLabel('Password').fill(active.password!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(
    page.getByRole('heading', { name: 'Institutions' }),
  ).toBeVisible();

  const cookies = await context.cookies('http://127.0.0.1:4322');
  const access = cookies.find(
    (cookie) => cookie.name === 'edu-hub-access-token',
  );
  const refresh = cookies.find(
    (cookie) => cookie.name === 'edu-hub-refresh-token',
  );
  expect(access).toBeTruthy();
  expect(refresh).toBeTruthy();
  await context.addCookies([
    { ...access!, value: 'expired-or-invalid-access-token' },
  ]);

  await page.goto('http://127.0.0.1:4322/institutions/new');
  await expect(
    page.getByRole('heading', { name: 'Create institution' }),
  ).toBeVisible();
  const refreshedCookies = await context.cookies('http://127.0.0.1:4322');
  expect(
    refreshedCookies.find((cookie) => cookie.name === 'edu-hub-access-token')
      ?.value,
  ).not.toBe('expired-or-invalid-access-token');

  await page.getByRole('button', { name: 'Sign out' }).click();
  await page.goto('http://127.0.0.1:4322/institutions/new');
  await expect(page).toHaveURL(/\/login$/);
});

test('suspended staff and anonymous protected API writes are denied', async ({
  page,
  request,
}) => {
  test.skip(
    !suspended.email || !suspended.password,
    'Suspended QA account is not configured',
  );
  await page.goto('http://127.0.0.1:4322/login');
  await page.getByLabel('Email').fill(suspended.email!);
  await page.getByLabel('Password').fill(suspended.password!);
  await page.getByRole('button', { name: 'Sign in' }).click();
  await expect(page).toHaveURL(/\/login\?error=unauthorized$/);
  await expect(
    page.getByText('This account does not have an active staff role.'),
  ).toBeVisible();

  const response = await request.post('http://127.0.0.1:4322/api/assertions', {
    form: {},
    maxRedirects: 0,
  });
  expect(response.status()).toBe(403);
});
