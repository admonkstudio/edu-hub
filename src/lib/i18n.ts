export const SUPPORTED_LOCALES = ['en-EG', 'ar-EG'] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export const localePath = (locale: SupportedLocale) =>
  `/${locale.toLowerCase()}/`;

export const localeDirection = (locale: SupportedLocale) =>
  locale === 'ar-EG' ? 'rtl' : 'ltr';

export const isSupportedLocale = (value: string): value is Lowercase<SupportedLocale> =>
  value === 'en-eg' || value === 'ar-eg';

export const toSupportedLocale = (value: string): SupportedLocale =>
  value.toLowerCase() === 'ar-eg' ? 'ar-EG' : 'en-EG';
