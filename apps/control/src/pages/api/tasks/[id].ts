import type { APIRoute } from 'astro';
import { getStaffContext } from '../../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const f = await context.request.formData();
  const { error } = await staff.client.rpc('transition_research_task_command', {
    task_id: context.params.id!,
    status: String(f.get('status')),
    assigned_to: String(f.get('assigned_to') || '') || null,
    outcome: String(f.get('outcome') || '') || null,
  } as never);
  if (error)
    return new Response('Unable to transition task.', {
      status: error.code === '42501' ? 403 : 400,
    });
  return context.redirect('/tasks?updated=1');
};
