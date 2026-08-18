import type { APIRoute } from 'astro';
import { getStaffContext } from '../../lib/auth';
export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const f = await context.request.formData();
  let value;
  try {
    value = JSON.parse(String(f.get('value_jsonb')));
  } catch {
    return new Response('Assertion value must be valid JSON.', { status: 400 });
  }
  const entityId = String(f.get('entity_id'));
  const { error } = await staff.client.from('entity_assertions').insert({
    entity_type: 'institution',
    entity_id: entityId,
    field_key: String(f.get('field_key')),
    locale: String(f.get('locale') || '') || null,
    value_jsonb: value,
    source_id: String(f.get('source_id')),
    confidence: Number(f.get('confidence') || 50),
    observed_at: new Date(String(f.get('observed_at'))).toISOString(),
    created_by: staff.user.id,
  });
  if (error) return new Response('Unable to add assertion.', { status: 400 });
  return context.redirect(`/institutions/${entityId}/trust?assertion=created`);
};
