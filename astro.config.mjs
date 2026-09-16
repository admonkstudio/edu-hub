import vercel from '@astrojs/vercel';
import { defineConfig } from 'astro/config';

export default defineConfig({
  adapter: vercel(),
  site: process.env.PUBLIC_WEB_ORIGIN ?? 'http://localhost:4321',
});
