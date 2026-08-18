import { SUPPORTED_LOCALES, type SupportedLocale } from '@edu-hub/config';

export type IndexDirective = 'index,follow' | 'noindex,nofollow';

export function localePath(locale: SupportedLocale): string {
  return `/${locale.toLowerCase()}/`;
}

export function canonicalUrl(origin: string, locale: SupportedLocale): string {
  return new URL(localePath(locale), origin).toString();
}

export function localeAlternates(origin: string) {
  return SUPPORTED_LOCALES.map((locale) => ({
    locale,
    href: canonicalUrl(origin, locale),
  }));
}
