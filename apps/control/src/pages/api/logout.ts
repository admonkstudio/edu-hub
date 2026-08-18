import type { APIRoute } from 'astro';
import { signOut } from '../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  await signOut(context);
  return context.redirect('/login?signed_out=1');
};
