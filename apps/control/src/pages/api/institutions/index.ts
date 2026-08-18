import { saveInstitutionCommand } from '@edu-hub/database';
import type { APIRoute } from 'astro';
import { getStaffContext } from '../../../lib/auth';
import { institutionCommandFromForm } from '../../../lib/institution-command';

export const prerender = false;
export const POST: APIRoute = async (context) => {
  const staff = await getStaffContext(context);
  if (!staff) return context.redirect('/login?error=session');
  const form = await context.request.formData();
  try {
    const id = await saveInstitutionCommand(staff.client, {
      payload: institutionCommandFromForm(form),
      reason: String(form.get('change_reason') ?? ''),
    });
    return context.redirect(`/institutions/${id}?created=1`);
  } catch (error) {
    console.error('Institution command failed', error);
    return new Response('Unable to create institution transactionally.', {
      status: 400,
    });
  }
};
