import { expect, test } from '@playwright/test';

const researcher = {
  email: process.env.RESEARCHER_QA_EMAIL,
  password: process.env.RESEARCHER_QA_PASSWORD,
};
const reviewer = {
  email: process.env.REVIEWER_QA_EMAIL,
  password: process.env.REVIEWER_QA_PASSWORD,
};

test('researcher evidence, conflict, reviewer resolution, task and logout workflow', async ({
  page,
}) => {
  test.skip(
    !researcher.email ||
      !researcher.password ||
      !reviewer.email ||
      !reviewer.password,
    'Trust workflow QA accounts are not configured',
  );
  const consoleErrors: string[] = [];
  const failedRequests: string[] = [];
  page.on('console', (m) => {
    if (m.type() === 'error') consoleErrors.push(m.text());
  });
  page.on('requestfailed', (r) => failedRequests.push(r.url()));
  const login = async (email: string, password: string) => {
    await page.goto('http://127.0.0.1:4322/login');
    await page.getByLabel('Email').fill(email);
    await page.getByLabel('Password').fill(password);
    await page.getByRole('button', { name: 'Sign in' }).click();
    await expect(
      page.getByRole('heading', { name: 'Institutions' }),
    ).toBeVisible();
  };
  await login(researcher.email!, researcher.password!);
  await page.getByRole('link', { name: 'Create institution' }).click();
  const suffix = Date.now();
  await page.getByLabel('Official name').fill(`Trust QA ${suffix}`);
  await page.getByLabel('Institution type').selectOption({ index: 1 });
  await page
    .getByLabel('Name', { exact: true })
    .first()
    .fill(`Trust QA ${suffix}`);
  await page.getByLabel('Slug', { exact: true }).fill(`trust-qa-${suffix}`);
  await page.getByLabel('الاسم').fill(`اختبار الثقة ${suffix}`);
  await page.getByLabel('الرابط المختصر').fill(`اختبار-الثقة-${suffix}`);
  await page.getByLabel('Campus name').fill('Main campus');
  await page.getByLabel('Governorate').selectOption({ index: 1 });
  await page.getByRole('button', { name: 'Create institution' }).click();
  const institutionUrl = page.url().replace(/\?.*$/, '');
  await page.getByRole('link', { name: 'Sources' }).click();
  for (const [title, url, level] of [
    ['Official website', `https://official-${suffix}.example.test`, '2'],
    ['Official social post', `https://social-${suffix}.example.test`, '4'],
  ] as const) {
    await page.getByLabel('Publisher').fill('Trust QA Institution');
    await page.getByLabel('Title').fill(title);
    await page.getByLabel('URL').fill(url);
    await page.getByLabel('Authority level').fill(level);
    await page.getByRole('button', { name: 'Add source' }).click();
  }
  await page.goto(`${institutionUrl}/trust`);
  for (const [index, value] of [
    '"https://first.example.test"',
    '"https://second.example.test"',
  ].entries()) {
    await page.getByLabel('Source').selectOption({ index });
    await page.getByLabel('Observed value (JSON)').fill(value);
    await page.getByLabel('Observed at').fill('2026-08-18T12:00');
    await page
      .getByRole('button', { name: 'Add unreviewed assertion' })
      .click();
  }
  await expect(
    page.getByRole('heading', { name: 'Open conflicts' }),
  ).toBeVisible();
  await expect(
    page
      .getByRole('cell', { name: '"https://first.example.test"' })
      .getByRole('code'),
  ).toBeVisible();
  await page.getByRole('button', { name: 'Sign out' }).click();
  await expect(page).toHaveURL(/\/login\?signed_out=1/);
  await page.goto(institutionUrl);
  await expect(page).toHaveURL(/\/login$/);
  await login(reviewer.email!, reviewer.password!);
  await page.goto(`${institutionUrl}/trust`);
  await page
    .getByPlaceholder('Resolution rationale')
    .first()
    .fill('Official website is the preferred current source.');
  await page
    .getByRole('button', { name: 'Accept this assertion' })
    .first()
    .click();
  await expect(page.getByText('No open conflicts.')).toBeVisible();
  await expect(page.getByText('fresh', { exact: true })).toBeVisible();
  await page.getByRole('link', { name: 'Research tasks' }).click();
  await page
    .getByLabel('Institution')
    .selectOption({ label: `Trust QA ${suffix}` });
  await page.getByRole('button', { name: 'Create task' }).click();
  const taskRow = page
    .locator('tbody tr')
    .filter({ hasText: `Trust QA ${suffix}` })
    .first();
  await taskRow.getByLabel('Status').selectOption('completed');
  await taskRow
    .getByLabel('Outcome')
    .fill('Conflict reviewed and official value accepted.');
  await taskRow.getByRole('button', { name: 'Update' }).click();
  await expect(taskRow.getByText('completed', { exact: true })).toBeVisible();
  expect(consoleErrors).toEqual([]);
  expect(failedRequests).toEqual([]);
});
