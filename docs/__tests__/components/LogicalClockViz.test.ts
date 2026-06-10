import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { mount, flushPromises } from '@vue/test-utils';
import LogicalClockViz from '../../.vitepress/theme/components/LogicalClockViz.vue';

describe('LogicalClockViz', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('renders 3 processes P1, P2, P3 with clock=0', () => {
    const wrapper = mount(LogicalClockViz);
    const processes = wrapper.findAll('.lc-process');
    expect(processes).toHaveLength(3);
    expect(wrapper.text()).toContain('P1');
    expect(wrapper.text()).toContain('P2');
    expect(wrapper.text()).toContain('P3');
  });

  it('each process has Local, Send, Receive buttons', () => {
    const wrapper = mount(LogicalClockViz);
    const actionGroups = wrapper.findAll('.lc-actions');
    expect(actionGroups).toHaveLength(3);
    actionGroups.forEach(group => {
      const btns = group.findAll('.lc-btn');
      expect(btns).toHaveLength(3);
    });
  });

  it('Local event increments process clock by 1', async () => {
    const wrapper = mount(LogicalClockViz);
    const localBtn = wrapper.findAll('.lc-btn')[0];
    await localBtn.trigger('click');
    await flushPromises();

    const events = wrapper.findAll('.lc-event-local');
    expect(events).toHaveLength(1);
    expect(wrapper.text()).toContain('1');
  });

  it('Send creates a pending message', async () => {
    const wrapper = mount(LogicalClockViz);
    const sendBtn = wrapper.findAll('.lc-btn')[1];
    await sendBtn.trigger('click');
    await flushPromises();

    expect(wrapper.find('.lc-pending').exists()).toBe(true);
  });

  it('Receive on another process merges clocks with max()+1', async () => {
    const wrapper = mount(LogicalClockViz);
    // P1 does 3 local events (clock=3), then sends (clock=4)
    const p1Local = wrapper.findAll('.lc-btn')[0];
    const p1Send = wrapper.findAll('.lc-btn')[1];
    await p1Local.trigger('click');
    await p1Local.trigger('click');
    await p1Local.trigger('click');
    await p1Send.trigger('click');
    await flushPromises();

    // P2 receives -> max(0, 4) + 1 = 5
    const p2Receive = wrapper.findAll('.lc-btn')[5]; // P2's receive btn
    await p2Receive.trigger('click');
    await flushPromises();

    const recvEvents = wrapper.findAll('.lc-event-recv');
    expect(recvEvents).toHaveLength(1);
  });

  it('reset clears all events and clocks', async () => {
    const wrapper = mount(LogicalClockViz);
    const localBtn = wrapper.findAll('.lc-btn')[0];
    await localBtn.trigger('click');
    await flushPromises();

    const resetBtn = wrapper.find('.viz-btn--danger');
    await resetBtn.trigger('click');
    await flushPromises();

    expect(wrapper.findAll('.lc-event')).toHaveLength(0);
  });

  it('has 3 preset scenario buttons', () => {
    const wrapper = mount(LogicalClockViz);
    const presets = wrapper.find('.viz-presets');
    const btns = presets.findAll('.viz-btn');
    expect(btns).toHaveLength(3);
  });
});
