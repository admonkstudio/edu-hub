import type { InstitutionCommandPayload } from '@edu-hub/database';

const nullable = (form: FormData, key: string) =>
  String(form.get(key) ?? '').trim() || null;

export function institutionCommandFromForm(
  form: FormData,
): InstitutionCommandPayload {
  const publicationStatus = String(form.get('publication_status') ?? 'draft');
  const localizations = [
    localizationFromForm(form, 'en-EG', 'en'),
    localizationFromForm(form, 'ar-EG', 'ar'),
  ].filter((localization) => localization !== null);

  if (localizations.length === 0) {
    throw new Error('At least one complete localization is required.');
  }
  if (
    ['public_noindex', 'index_ready', 'published'].includes(
      publicationStatus,
    ) &&
    !['en-EG', 'ar-EG'].every((locale) =>
      localizations.some((localization) => localization.locale === locale),
    )
  ) {
    throw new Error('Both launch localizations are required for publication.');
  }

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
      publication_status: publicationStatus,
      data_status: String(form.get('data_status') ?? 'candidate'),
    },
    localizations,
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

function localizationFromForm(
  form: FormData,
  locale: 'en-EG' | 'ar-EG',
  suffix: 'en' | 'ar',
) {
  const name = String(form.get(`name_${suffix}`) ?? '').trim();
  const slug = String(form.get(`slug_${suffix}`) ?? '').trim();
  const summary = nullable(form, `summary_${suffix}`);
  const hasAnyValue = Boolean(name || slug || summary);

  if (!hasAnyValue) return null;
  if (!name || !slug) {
    throw new Error(`${locale} requires both a name and slug.`);
  }

  return { locale, name, slug, summary };
}
