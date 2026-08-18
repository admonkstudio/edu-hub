import { describe, expect, it } from 'vitest';
import {
  COUNTRY_CODE,
  isSupportedLocale,
  localeDirection,
  parsePublicEnvironment,
} from './index.js';

describe('foundation configuration', () => {
  it('defines Egypt and both launch locales', () => {
    expect(COUNTRY_CODE).toBe('EG');
    expect(isSupportedLocale('en-EG')).toBe(true);
    expect(isSupportedLocale('ar-EG')).toBe(true);
    expect(isSupportedLocale('en-US')).toBe(false);
  });

  it('maps locale direction', () => {
    expect(localeDirection('en-EG')).toBe('ltr');
    expect(localeDirection('ar-EG')).toBe('rtl');
  });

  it('validates and defaults public environment values', () => {
    expect(parsePublicEnvironment({}).PUBLIC_WEB_ORIGIN).toBe(
      'http://localhost:4321',
    );
    expect(() =>
      parsePublicEnvironment({ PUBLIC_WEB_ORIGIN: 'not-a-url' }),
    ).toThrow();
  });
});
