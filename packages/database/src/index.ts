import {
  parseDatabasePublicEnvironment,
  parseServerEnvironment,
} from '@edu-hub/config';
import { createClient } from '@supabase/supabase-js';
import type { Database } from './database.types.js';

export type DatabaseClient = ReturnType<typeof createServerDatabaseClient>;

export function createServerDatabaseClient(
  environment: Record<string, string | undefined>,
) {
  const config = parseServerEnvironment(environment);
  return createClient<Database>(
    config.SUPABASE_URL,
    config.SUPABASE_SECRET_KEY,
    {
      auth: { autoRefreshToken: false, persistSession: false },
    },
  );
}

export function createAuthenticatedDatabaseClient(
  environment: Record<string, string | undefined>,
  accessToken: string,
) {
  const config = parseDatabasePublicEnvironment(environment);
  return createClient<Database>(
    config.SUPABASE_URL,
    config.SUPABASE_PUBLISHABLE_KEY,
    {
      global: { headers: { Authorization: `Bearer ${accessToken}` } },
      auth: { autoRefreshToken: false, persistSession: false },
    },
  );
}

export type { Database } from './database.types.js';
export * from './institutions.js';
