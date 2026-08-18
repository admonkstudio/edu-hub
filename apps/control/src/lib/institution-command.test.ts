import { describe, expect, it } from 'vitest';
import { institutionCommandFromForm } from './institution-command';

const baseForm = () => {
  const form = new FormData();
  form.set('official_name', 'Localized institution');
  form.set('institution_type_id', '10000000-0000-4000-8000-000000000001');
  form.set('publication_status', 'draft');
  form.set('data_status', 'candidate');
  return form;
};

describe('institutionCommandFromForm localizations', () => {
  it('allows a draft candidate with English only', () => {
    const form = baseForm();
    form.set('name_en', 'Small Talk Nursery');
    form.set('slug_en', 'small-talk-nursery');

    expect(institutionCommandFromForm(form).localizations).toEqual([
      {
        locale: 'en-EG',
        name: 'Small Talk Nursery',
        slug: 'small-talk-nursery',
        summary: null,
      },
    ]);
  });

  it('allows a legitimately sourced Arabic-only draft candidate', () => {
    const form = baseForm();
    form.set('name_ar', 'مؤسسة عربية');
    form.set('slug_ar', 'مؤسسة-عربية');

    const localizations = institutionCommandFromForm(form).localizations;
    expect(localizations).toHaveLength(1);
    expect(localizations[0]?.locale).toBe('ar-EG');
  });

  it('rejects zero localizations', () => {
    expect(() => institutionCommandFromForm(baseForm())).toThrow(
      'At least one complete localization is required.',
    );
  });

  it('rejects a partial localization instead of generating a placeholder', () => {
    const form = baseForm();
    form.set('name_en', 'Missing slug');
    expect(() => institutionCommandFromForm(form)).toThrow(
      'en-EG requires both a name and slug.',
    );
  });

  it('requires both launch localizations for a public status', () => {
    const form = baseForm();
    form.set('publication_status', 'public_noindex');
    form.set('name_en', 'English only');
    form.set('slug_en', 'english-only');
    expect(() => institutionCommandFromForm(form)).toThrow(
      'Both launch localizations are required for publication.',
    );
  });

  it('keeps existing bilingual draft payloads unchanged', () => {
    const form = baseForm();
    form.set('name_en', 'Bilingual Institution');
    form.set('slug_en', 'bilingual-institution');
    form.set('name_ar', 'مؤسسة ثنائية اللغة');
    form.set('slug_ar', 'مؤسسة-ثنائية-اللغة');

    expect(
      institutionCommandFromForm(form).localizations.map(
        ({ locale }) => locale,
      ),
    ).toEqual(['en-EG', 'ar-EG']);
  });
});
