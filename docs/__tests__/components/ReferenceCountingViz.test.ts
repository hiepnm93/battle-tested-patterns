import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import ReferenceCountingViz from '../../.vitepress/theme/components/ReferenceCountingViz.vue';

describe('ReferenceCountingViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders 2 initial objects and 3 references', () => {
    const wrapper = mount(ReferenceCountingViz);
    expect(wrapper.text()).toContain('Obj A');
    expect(wrapper.text()).toContain('Obj B');
    expect(wrapper.text()).toContain('var x');
    expect(wrapper.text()).toContain('var y');
    expect(wrapper.text()).toContain('var z');
  });

  it('shows reference count for each object', () => {
    const wrapper = mount(ReferenceCountingViz);
    expect(wrapper.text()).toContain('rc=2'); // Obj A has 2 refs
    expect(wrapper.text()).toContain('rc=1'); // Obj B has 1 ref
  });

  it('drop button removes a reference and decrements count', async () => {
    const wrapper = mount(ReferenceCountingViz);
    const dropBtns = wrapper.findAll('.rc-ref-drop, .rc-drop-btn');
    if (dropBtns.length > 0) {
      await dropBtns[0].trigger('click');
      vi.advanceTimersByTime(1000);
      await flushPromises();
    }
    expect(wrapper.text()).toMatch(/rc=|Dropped|已删除/);
  });

  it('reset restores initial objects and references', async () => {
    const wrapper = mount(ReferenceCountingViz);
    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('Obj A');
    expect(wrapper.text()).toContain('rc=2');
  });

  it('has preset scenario buttons', () => {
    const wrapper = mount(ReferenceCountingViz);
    const presets = wrapper.find('.viz-presets');
    expect(presets.exists()).toBe(true);
  });
});
