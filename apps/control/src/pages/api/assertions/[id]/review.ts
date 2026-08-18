import type { APIRoute } from 'astro';
import { getStaffContext } from '../../../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const f = await context.request.formData();
  const id = context.params.id!;
  const { data: a } = await staff.client
    .from('entity_assertions')
    .select('entity_id')
    .eq('id', id)
    .single();
  const { error } = await staff.client.rpc('review_assertion_command', {
    assertion_id: id,
    decision: String(f.get('decision')),
    reason: String(f.get('reason')),
  });
  if (error)
    return new Response('Unable to review assertion.', {
      status: error.code === '42501' ? 403 : 400,
    });
  return context.redirect(`/institutions/${a?.entity_id}/trust?reviewed=1`);
};
