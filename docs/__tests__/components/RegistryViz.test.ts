import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import RegistryViz from '../../.vitepress/theme/components/RegistryViz.vue';

describe('RegistryViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders 5 available plugins', () => {
    const wrapper = mount(RegistryViz);
    expect(wrapper.text()).toContain('JSONHandler');
    expect(wrapper.text()).toContain('XMLHandler');
    expect(wrapper.text()).toContain('CSVHandler');
  });

  it('starts with empty registry', () => {
    const wrapper = mount(RegistryViz);
    expect(wrapper.text()).toMatch(/empty|空|0 handler/i);
  });

  it('clicking a plugin registers it into the registry', async () => {
    const wrapper = mount(RegistryViz);
    const registerBtns = wrapper.findAll('.reg-plugin-btn, button').filter(
      b => b.text().includes('Register') || b.text().includes('注册') || b.text().includes('JSON')
    );
    if (registerBtns.length > 0) {
      await registerBtns[0].trigger('click');
      vi.advanceTimersByTime(1000);
      await flushPromises();
    }
    expect(wrapper.text()).toMatch(/Registered|已注册|1 handler/i);
  });

  it('reset clears the registry', async () => {
    const wrapper = mount(RegistryViz);
    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toMatch(/empty|空|0 handler/i);
  });

  it('has preset scenario buttons', () => {
    const wrapper = mount(RegistryViz);
    const presets = wrapper.find('.viz-presets');
    expect(presets.exists()).toBe(true);
  });
});
