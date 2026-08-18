import type { InstitutionCommandPayload } from '@edu-hub/database';

const nullable = (form: FormData, key: string) =>
  String(form.get(key) ?? '').trim() || null;

export function institutionCommandFromForm(
  form: FormData,
): InstitutionCommandPayload {
  return {
    core: {
      official_name: String(form.get('official_name') ?? '').trim(),
      institution_type_id: String(form.get('institution_type_id') ?? ''),
      provider_id: nullable(form, 'provider_id'),
      ownership_type_id: nullable(form, 'ownership_type_id'),
      education_model_id: nullable(form, 'education_model_id'),
      official_website_url: nullable(form, 'official_website_url'),
      founded_year: nullable(form, 'founded_year')
        ? Number(form.get('founded_year'))
        : null,
      publication_status: String(form.get('publication_status') ?? 'draft'),
      data_status: String(form.get('data_status') ?? 'candidate'),
    },
    localizations: [
      {
        locale: 'en-EG',
        name: String(form.get('name_en') ?? '').trim(),
        slug: String(form.get('slug_en') ?? '').trim(),
        summary: nullable(form, 'summary_en'),
      },
      {
        locale: 'ar-EG',
        name: String(form.get('name_ar') ?? '').trim(),
        slug: String(form.get('slug_ar') ?? '').trim(),
        summary: nullable(form, 'summary_ar'),
      },
    ],
    campus: {
      id: nullable(form, 'campus_id'),
      name: String(form.get('campus_name') ?? '').trim(),
      location_id: String(form.get('location_id') ?? ''),
      is_main: true,
      address_en: nullable(form, 'address_en'),
      address_ar: nullable(form, 'address_ar'),
    },
    relationships: {
      education_levels: form.getAll('education_level_ids').map(String),
      curricula: form.getAll('curriculum_ids').map(String),
      languages: form.getAll('language_ids').map(String),
      certificates: form.getAll('certificate_ids').map(String),
    },
    source_id: nullable(form, 'source_id'),
  };
}
