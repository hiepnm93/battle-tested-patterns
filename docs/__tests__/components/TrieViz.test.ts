import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import TrieViz from '../../.vitepress/theme/components/TrieViz.vue';

describe('TrieViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders SVG with empty-state text when no words inserted', () => {
    const wrapper = mount(TrieViz);
    expect(wrapper.find('svg').exists()).toBe(true);
    expect(wrapper.text()).toMatch(/empty|空/i);
  });

  it('has insert, search, demo, and reset buttons', () => {
    const wrapper = mount(TrieViz);
    const btns = wrapper.findAll('.viz-btn, .viz-btn--primary, .viz-btn--danger');
    const texts = btns.map(b => b.text());
    expect(texts.some(t => t.includes('Insert') || t.includes('插入'))).toBe(true);
    expect(texts.some(t => t.includes('Search') || t.includes('搜索'))).toBe(true);
    expect(texts.some(t => t.includes('Reset') || t.includes('重置'))).toBe(true);
  });

  it('inserting a word adds it to the word list and creates tree nodes', async () => {
    const wrapper = mount(TrieViz);
    const input = wrapper.find('.viz-input');
    await input.setValue('cat');

    const insertBtn = wrapper.find('.viz-btn--primary');
    await insertBtn.trigger('click');
    vi.advanceTimersByTime(1000);
    await flushPromises();

    expect(wrapper.find('.trie-words').exists()).toBe(true);
    expect(wrapper.find('.trie-word-tag').text()).toBe('cat');

    const circles = wrapper.findAll('svg circle');
    expect(circles.length).toBeGreaterThanOrEqual(4);
  });

  it('demo button adds preset words (cat, car, card, care, dog, do)', async () => {
    const wrapper = mount(TrieViz);
    const demoBtn = wrapper.findAll('.viz-btn, .viz-btn--primary').find(
      b => b.text().includes('Demo') || b.text().includes('演示')
    );
    await demoBtn!.trigger('click');
    vi.advanceTimersByTime(2000);
    await flushPromises();

    const tags = wrapper.findAll('.trie-word-tag');
    expect(tags.length).toBe(6);
    expect(tags.map(t => t.text())).toContain('cat');
    expect(tags.map(t => t.text())).toContain('dog');
  });

  it('reset clears all words and tree nodes', async () => {
    const wrapper = mount(TrieViz);
    const input = wrapper.find('.viz-input');
    await input.setValue('hi');
    const insertBtn = wrapper.find('.viz-btn--primary');
    await insertBtn.trigger('click');
    vi.advanceTimersByTime(1000);
    await flushPromises();

    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    expect(wrapper.find('.trie-words').exists()).toBe(false);
    expect(wrapper.text()).toMatch(/empty|空/i);
  });

  it('has 3 preset scenario buttons', () => {
    const wrapper = mount(TrieViz);
    const presets = wrapper.find('.viz-presets');
    expect(presets.exists()).toBe(true);
    const btns = presets.findAll('.viz-btn');
    expect(btns).toHaveLength(3);
  });
});
