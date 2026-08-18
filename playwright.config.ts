import { defineConfig } from '@playwright/test';

export default defineConfig({
  testDir: './tests/browser',
  fullyParallel: true,
  use: { baseURL: 'http://127.0.0.1:4321', trace: 'retain-on-failure' },
  webServer: [
    {
      command: 'pnpm --filter @edu-hub/web dev --host 127.0.0.1',
      port: 4321,
      reuseExistingServer: true,
    },
    {
      command: 'pnpm --filter @edu-hub/control dev --host 127.0.0.1',
      port: 4322,
      reuseExistingServer: true,
    },
  ],
});
