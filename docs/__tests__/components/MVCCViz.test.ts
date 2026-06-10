import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import MVCCViz from '../../.vitepress/theme/components/MVCCViz.vue';

describe('MVCCViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders initial store with user and balance keys', () => {
    const wrapper = mount(MVCCViz);
    expect(wrapper.text()).toContain('user');
    expect(wrapper.text()).toContain('balance');
  });

  it('Begin Transaction creates a new active transaction', async () => {
    const wrapper = mount(MVCCViz);
    const beginBtn = wrapper.findAll('button').find(b => b.text().includes('Begin') || b.text().includes('开始'));
    await beginBtn!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toMatch(/T1/);
  });

  it('shows transaction snapshot version', async () => {
    const wrapper = mount(MVCCViz);
    const beginBtn = wrapper.findAll('button').find(b => b.text().includes('Begin') || b.text().includes('开始'));
    await beginBtn!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toMatch(/snapshot|快照|v1/i);
  });

  it('reset clears all transactions', async () => {
    const wrapper = mount(MVCCViz);
    const beginBtn = wrapper.findAll('button').find(b => b.text().includes('Begin') || b.text().includes('开始'));
    await beginBtn!.trigger('click');
    await flushPromises();

    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    expect(wrapper.text()).not.toContain('T1');
  });

  it('has preset scenario buttons', () => {
    const wrapper = mount(MVCCViz);
    const presets = wrapper.find('.viz-presets');
    expect(presets.exists()).toBe(true);
  });
});
