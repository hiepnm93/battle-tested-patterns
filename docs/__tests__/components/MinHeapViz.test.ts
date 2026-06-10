import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import MinHeapViz from '../../.vitepress/theme/components/MinHeapViz.vue';

describe('MinHeapViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders SVG tree area and controls', () => {
    const wrapper = mount(MinHeapViz);
    expect(wrapper.find('svg').exists()).toBe(true);
    expect(wrapper.find('.viz-controls').exists()).toBe(true);
  });

  it('starts with empty heap', () => {
    const wrapper = mount(MinHeapViz);
    const rects = wrapper.findAll('svg rect');
    expect(rects).toHaveLength(0);
  });

  it('insert button adds a node to the heap', async () => {
    const wrapper = mount(MinHeapViz);
    const insertBtn = wrapper.find('.viz-btn--primary');
    await insertBtn.trigger('click');
    vi.advanceTimersByTime(2000);
    await flushPromises();

    const rects = wrapper.findAll('svg rect');
    expect(rects.length).toBeGreaterThanOrEqual(1);
  });

  it('reset clears the heap', async () => {
    const wrapper = mount(MinHeapViz);
    const insertBtn = wrapper.find('.viz-btn--primary');
    await insertBtn.trigger('click');
    vi.advanceTimersByTime(2000);
    await flushPromises();

    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    const rects = wrapper.findAll('svg rect');
    expect(rects).toHaveLength(0);
  });

  it('has preset scenario buttons', () => {
    const wrapper = mount(MinHeapViz);
    const presets = wrapper.find('.viz-presets');
    expect(presets.exists()).toBe(true);
  });
});
