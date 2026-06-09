import { describe, it, expect, vi, beforeEach } from 'vitest';
import { ref } from 'vue';

const mockLang = ref('en-US');
vi.mock('vitepress', () => ({
  useData: () => ({ lang: mockLang }),
}));

import { useI18n } from '../../.vitepress/theme/composables/useI18n';

describe('useI18n', () => {
  beforeEach(() => {
    mockLang.value = 'en-US';
  });

  it('returns English text when lang is en-US', () => {
    const { t } = useI18n();
    expect(t('Hello', '你好')).toBe('Hello');
  });

  it('returns Chinese text when lang is zh-CN', () => {
    mockLang.value = 'zh-CN';
    const { t } = useI18n();
    expect(t('Hello', '你好')).toBe('你好');
  });

  it('isZh computed reflects language', () => {
    const { isZh } = useI18n();
    expect(isZh.value).toBe(false);

    mockLang.value = 'zh-CN';
    expect(isZh.value).toBe(true);
  });
});
