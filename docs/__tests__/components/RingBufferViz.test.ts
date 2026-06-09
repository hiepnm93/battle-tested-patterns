import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import RingBufferViz from '../../.vitepress/theme/components/RingBufferViz.vue';

describe('RingBufferViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders 8 buffer cells as SVG circles', () => {
    const wrapper = mount(RingBufferViz);
    const circles = wrapper.findAll('.ringbuf-svg circle[r="22"]');
    expect(circles).toHaveLength(8);
  });

  it('shows count as 0/8 initially', () => {
    const wrapper = mount(RingBufferViz);
    const svg = wrapper.find('.ringbuf-svg');
    expect(svg.text()).toContain('0');
    expect(svg.text()).toContain('/8');
  });

  it('shows tail pointer label initially', () => {
    const wrapper = mount(RingBufferViz);
    const svg = wrapper.find('.ringbuf-svg');
    expect(svg.text()).toContain('T');
  });

  it('enqueue button exists and is clickable', async () => {
    const wrapper = mount(RingBufferViz);
    const enqueueBtn = wrapper.findAll('.viz-btn').find((b) =>
      b.text().includes('Enqueue') || b.text().includes('入队'),
    );
    expect(enqueueBtn).toBeTruthy();

    await enqueueBtn!.trigger('click');
    vi.advanceTimersByTime(500);
    await flushPromises();

    const svg = wrapper.find('.ringbuf-svg');
    expect(svg.text()).toContain('1');
  });

  it('reset button clears buffer', async () => {
    const wrapper = mount(RingBufferViz);
    const enqueueBtn = wrapper.findAll('.viz-btn').find((b) =>
      b.text().includes('Enqueue') || b.text().includes('入队'),
    );
    const resetBtn = wrapper.find('.viz-btn--danger');

    await enqueueBtn!.trigger('click');
    vi.advanceTimersByTime(500);
    await flushPromises();

    await resetBtn.trigger('click');
    await flushPromises();

    const svg = wrapper.find('.ringbuf-svg');
    expect(svg.text()).toContain('0');
  });
});
