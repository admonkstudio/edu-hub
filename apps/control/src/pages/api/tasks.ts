import type { APIRoute } from 'astro';
import { getStaffContext } from '../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const form = await context.request.formData();
  const { error } = await staff.client.from('research_tasks').insert({
    task_type: String(form.get('task_type')),
    entity_type: 'institution',
    entity_id: String(form.get('entity_id')),
    priority: String(form.get('priority')),
    notes: String(form.get('notes') ?? '').trim() || null,
    created_by: staff.user.id,
  });
  if (error) return new Response('Unable to create task.', { status: 400 });
  return context.redirect('/tasks?created=1');
};
