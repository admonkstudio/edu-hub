import { z } from 'zod';

export const COUNTRY_CODE = 'EG' as const;
export const SUPPORTED_LOCALES = ['en-EG', 'ar-EG'] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];
export type Direction = 'ltr' | 'rtl';

export function isSupportedLocale(value: string): value is SupportedLocale {
  return SUPPORTED_LOCALES.includes(value as SupportedLocale);
}

export function localeDirection(locale: SupportedLocale): Direction {
  return locale === 'ar-EG' ? 'rtl' : 'ltr';
}

export const publicEnvironmentSchema = z.object({
  PUBLIC_WEB_ORIGIN: z.url().default('http://localhost:4321'),
  PUBLIC_CONTROL_ORIGIN: z.url().default('http://localhost:4322'),
});

export const databasePublicEnvironmentSchema = publicEnvironmentSchema.extend({
  SUPABASE_URL: z.url(),
  SUPABASE_PUBLISHABLE_KEY: z.string().min(1),
});

export const serverEnvironmentSchema = databasePublicEnvironmentSchema.extend({
  SUPABASE_SECRET_KEY: z.string().min(1),
});

export function parsePublicEnvironment(
  environment: Record<string, string | undefined>,
) {
  return publicEnvironmentSchema.parse(environment);
}

export function parseServerEnvironment(
  environment: Record<string, string | undefined>,
) {
  return serverEnvironmentSchema.parse(environment);
}

export function parseDatabasePublicEnvironment(
  environment: Record<string, string | undefined>,
) {
  return databasePublicEnvironmentSchema.parse(environment);
}
