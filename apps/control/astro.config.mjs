import vercel from '@astrojs/vercel';
import { defineConfig, envField } from 'astro/config';
export default defineConfig({
  adapter: vercel(),
  env: {
    schema: {
      SUPABASE_URL: envField.string({ context: 'server', access: 'secret' }),
      SUPABASE_PUBLISHABLE_KEY: envField.string({
        context: 'server',
        access: 'secret',
      }),
    },
  },
  site: process.env.PUBLIC_CONTROL_ORIGIN ?? 'http://localhost:4322',
  vite: {
    // Bundle the workspace repository and Supabase client into the server
    // function. This also keeps Vercel output portable across pnpm hosts.
    ssr: { noExternal: ['@edu-hub/database', '@supabase/supabase-js'] },
  },
});
