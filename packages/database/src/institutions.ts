import type { SupabaseClient } from '@supabase/supabase-js';
import type { Database, TablesInsert, TablesUpdate } from './database.types.js';

type Client = SupabaseClient<Database>;
type LocalizationInput = Omit<
  TablesInsert<'institution_localizations'>,
  'institution_id'
>;
type CampusInput = Omit<TablesInsert<'campuses'>, 'institution_id' | 'id'>;

export type InstitutionCommandPayload = {
  core: TablesInsert<'institutions'>;
  localizations: Array<LocalizationInput>;
  campus: CampusInput & { id?: string | null };
  relationships: {
    education_levels: string[];
    curricula: string[];
    languages: string[];
    certificates: string[];
  };
  source_id?: string | null;
};

export async function saveInstitutionCommand(
  client: Client,
  input: { id?: string; payload: InstitutionCommandPayload; reason: string },
) {
  const command = input.id
    ? client.rpc('update_institution_command', {
        institution_id: input.id,
        payload: input.payload as never,
        reason: input.reason,
      })
    : client.rpc('create_institution_command', {
        payload: input.payload as never,
        reason: input.reason,
      });
  const { data, error } = await command;
  if (error) throw error;
  return data;
}

export async function listInstitutions(client: Client) {
  const { data, error } = await client
    .from('institutions')
    .select(
      'id,official_name,publication_status,data_status,institution_types(code,label_en),institution_localizations(locale,name),campuses(name,is_main,locations(name_en,name_ar))',
    )
    .order('official_name');
  if (error) throw error;
  return data;
}

export async function getInstitution(client: Client, id: string) {
  const { data, error } = await client
    .from('institutions')
    .select(
      '*,institution_localizations(*),campuses(*),institution_education_levels(education_level_id),institution_curricula(curriculum_id),institution_languages(language_id),institution_certificates(certificate_id)',
    )
    .eq('id', id)
    .single();
  if (error) throw error;
  return data;
}

export async function createInstitution(
  client: Client,
  input: TablesInsert<'institutions'>,
) {
  const { data, error } = await client
    .from('institutions')
    .insert(input)
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function updateInstitution(
  client: Client,
  id: string,
  input: TablesUpdate<'institutions'>,
) {
  const { data, error } = await client
    .from('institutions')
    .update(input)
    .eq('id', id)
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function upsertInstitutionLocalization(
  client: Client,
  institutionId: string,
  input: LocalizationInput,
) {
  const { data, error } = await client
    .from('institution_localizations')
    .upsert(
      { ...input, institution_id: institutionId },
      { onConflict: 'institution_id,locale' },
    )
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function createCampus(
  client: Client,
  institutionId: string,
  input: CampusInput,
) {
  const { data, error } = await client
    .from('campuses')
    .insert({ ...input, institution_id: institutionId })
    .select()
    .single();
  if (error) throw error;
  return data;
}

export async function updateCampus(
  client: Client,
  campusId: string,
  input: Partial<CampusInput>,
) {
  const { data, error } = await client
    .from('campuses')
    .update(input)
    .eq('id', campusId)
    .select()
    .single();
  if (error) throw error;
  return data;
}

const relationshipTables = {
  educationLevels: ['institution_education_levels', 'education_level_id'],
  curricula: ['institution_curricula', 'curriculum_id'],
  languages: ['institution_languages', 'language_id'],
  certificates: ['institution_certificates', 'certificate_id'],
} as const;

export async function replaceInstitutionRelationships(
  client: Client,
  institutionId: string,
  kind: keyof typeof relationshipTables,
  relatedIds: string[],
) {
  const [table, column] = relationshipTables[kind];
  const { error: deleteError } = await client
    .from(table)
    .delete()
    .eq('institution_id', institutionId);
  if (deleteError) throw deleteError;
  if (relatedIds.length === 0) return;
  const rows = relatedIds.map((id) => ({
    institution_id: institutionId,
    [column]: id,
  }));
  const { error: insertError } = await client.from(table).insert(rows as never);
  if (insertError) throw insertError;
}
