import type { APIRoute } from 'astro';
import { getStaffContext } from '../../../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const f = await context.request.formData();
  const conflictId = context.params.id!;
  const { data: c } = await staff.client
    .from('assertion_conflicts')
    .select('entity_id')
    .eq('id', conflictId)
    .single();
  const { error } = await staff.client.rpc(
    'resolve_assertion_conflict_command',
    {
      conflict_id: conflictId,
      accepted_assertion_id: String(f.get('accepted_assertion_id')),
      reason: String(f.get('reason')),
    },
  );
  if (error)
    return new Response('Unable to resolve conflict.', {
      status: error.code === '42501' ? 403 : 400,
    });
  return context.redirect(`/institutions/${c?.entity_id}/trust?resolved=1`);
};
