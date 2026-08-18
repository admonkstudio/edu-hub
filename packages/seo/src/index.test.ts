import { describe, expect, it } from 'vitest';
import { canonicalUrl, localeAlternates, localePath } from './index.js';

describe('SEO foundation', () => {
  it('builds stable lower-case locale paths and canonical URLs', () => {
    expect(localePath('en-EG')).toBe('/en-eg/');
    expect(canonicalUrl('https://example.com', 'ar-EG')).toBe(
      'https://example.com/ar-eg/',
    );
  });

  it('returns both locale alternates', () => {
    expect(localeAlternates('https://example.com')).toHaveLength(2);
  });
});
