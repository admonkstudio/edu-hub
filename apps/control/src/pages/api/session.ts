import type { APIRoute } from 'astro';
import {
  clearSessionCookies,
  establishSession,
  getStaffContext,
} from '../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  clearSessionCookies(context);
  const form = await context.request.formData();
  const result = await establishSession(
    context,
    String(form.get('email') ?? ''),
    String(form.get('password') ?? ''),
  );
  if (result.error || !result.data.session)
    return context.redirect('/login?error=credentials');
  if (!(await getStaffContext(context)))
    return context.redirect('/login?error=unauthorized');
  return context.redirect('/');
};
