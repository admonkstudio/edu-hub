import type { APIRoute } from 'astro';
import { getStaffContext } from '../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const form = await context.request.formData();
  const { error } = await staff.client.from('sources').insert({
    source_type: String(form.get('source_type')),
    authority_level: Number(form.get('authority_level')),
    publisher: String(form.get('publisher')).trim(),
    title: String(form.get('title')).trim(),
    url: String(form.get('url')).trim(),
    language: String(form.get('language')),
    notes: String(form.get('notes') ?? '').trim() || null,
    created_by: staff.user.id,
  });
  if (error) return new Response('Unable to add source.', { status: 400 });
  return context.redirect('/sources?created=1');
};
