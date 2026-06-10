import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import SkipListViz from '../../.vitepress/theme/components/SkipListViz.vue';

describe('SkipListViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders SVG visualization area', () => {
    const wrapper = mount(SkipListViz);
    expect(wrapper.find('svg').exists()).toBe(true);
  });

  it('starts with empty skip list', () => {
    const wrapper = mount(SkipListViz);
    expect(wrapper.text()).toMatch(/empty|空|Insert|插入/i);
  });

  it('insert button adds a node', async () => {
    const wrapper = mount(SkipListViz);
    const insertBtn = wrapper.find('.viz-btn--primary');
    await insertBtn.trigger('click');
    vi.advanceTimersByTime(2000);
    await flushPromises();

    expect(wrapper.text()).toMatch(/Inserted|已插入|level/i);
  });

  it('reset clears all nodes', async () => {
    const wrapper = mount(SkipListViz);
    const insertBtn = wrapper.find('.viz-btn--primary');
    await insertBtn.trigger('click');
    vi.advanceTimersByTime(1000);
    await flushPromises();

    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toMatch(/empty|空|Insert|插入/i);
  });

  it('has preset scenario buttons', () => {
    const wrapper = mount(SkipListViz);
    const presets = wrapper.find('.viz-presets');
    expect(presets.exists()).toBe(true);
  });
});
