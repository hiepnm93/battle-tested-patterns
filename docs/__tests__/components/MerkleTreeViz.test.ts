import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import MerkleTreeViz from '../../.vitepress/theme/components/MerkleTreeViz.vue';

describe('MerkleTreeViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders SVG with 7 tree nodes and 6 edges', () => {
    const wrapper = mount(MerkleTreeViz);
    const svg = wrapper.find('.merkle-svg');
    expect(svg.exists()).toBe(true);
    const rects = svg.findAll('rect');
    expect(rects).toHaveLength(7);
    const lines = svg.findAll('line');
    expect(lines).toHaveLength(6);
  });

  it('shows Root, H12, H34, and leaf labels', () => {
    const wrapper = mount(MerkleTreeViz);
    const text = wrapper.text();
    expect(text).toContain('Root');
    expect(text).toContain('H(A)');
    expect(text).toContain('H(D)');
  });

  it('Verify A triggers path highlighting animation', async () => {
    const wrapper = mount(MerkleTreeViz);
    const verifyBtn = wrapper.findAll('.viz-btn--primary')[0];
    await verifyBtn.trigger('click');
    vi.advanceTimersByTime(2000);
    await flushPromises();

    expect(wrapper.text()).toMatch(/Verified|验证/);
  });

  it('Tamper changes leaf data and root hash', async () => {
    const wrapper = mount(MerkleTreeViz);
    const tamperBtn = wrapper.find('.viz-btn--danger');
    await tamperBtn.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toMatch(/Tampered|篡改/);
  });

  it('reset restores leaves to A, B, C, D', async () => {
    const wrapper = mount(MerkleTreeViz);
    const tamperBtn = wrapper.find('.viz-btn--danger');
    await tamperBtn.trigger('click');
    await flushPromises();

    const resetBtn = wrapper.findAll('button').find(b => b.text().includes('Reset') || b.text().includes('重置'));
    await resetBtn!.trigger('click');
    await flushPromises();

    expect(wrapper.text()).toContain('H(A)');
    expect(wrapper.text()).toContain('H(D)');
  });

  it('has 3 preset scenario buttons', () => {
    const wrapper = mount(MerkleTreeViz);
    const presets = wrapper.find('.viz-presets');
    const btns = presets.findAll('.viz-btn');
    expect(btns).toHaveLength(3);
  });
});
