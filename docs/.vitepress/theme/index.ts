import DefaultTheme from 'vitepress/theme';
import type { Theme } from 'vitepress';
import RingBufferViz from './components/RingBufferViz.vue';
import LRUCacheViz from './components/LRUCacheViz.vue';
import BloomFilterViz from './components/BloomFilterViz.vue';
import CircuitBreakerViz from './components/CircuitBreakerViz.vue';
import ConsistentHashViz from './components/ConsistentHashViz.vue';
import MinHeapViz from './components/MinHeapViz.vue';
import SkipListViz from './components/SkipListViz.vue';
import TrieViz from './components/TrieViz.vue';
import StateMachineViz from './components/StateMachineViz.vue';
import EventLoopViz from './components/EventLoopViz.vue';
import RateLimiterViz from './components/RateLimiterViz.vue';
import MerkleTreeViz from './components/MerkleTreeViz.vue';
import BPlusTreeViz from './components/BPlusTreeViz.vue';
import DependencyGraphViz from './components/DependencyGraphViz.vue';
import ObserverViz from './components/ObserverViz.vue';
import BackpressureViz from './components/BackpressureViz.vue';
import CopyOnWriteViz from './components/CopyOnWriteViz.vue';
import './custom.css';

export default {
  extends: DefaultTheme,
  enhanceApp({ app }) {
    app.component('RingBufferViz', RingBufferViz);
    app.component('LRUCacheViz', LRUCacheViz);
    app.component('BloomFilterViz', BloomFilterViz);
    app.component('CircuitBreakerViz', CircuitBreakerViz);
    app.component('ConsistentHashViz', ConsistentHashViz);
    app.component('MinHeapViz', MinHeapViz);
    app.component('SkipListViz', SkipListViz);
    app.component('TrieViz', TrieViz);
    app.component('StateMachineViz', StateMachineViz);
    app.component('EventLoopViz', EventLoopViz);
    app.component('RateLimiterViz', RateLimiterViz);
    app.component('MerkleTreeViz', MerkleTreeViz);
    app.component('BPlusTreeViz', BPlusTreeViz);
    app.component('DependencyGraphViz', DependencyGraphViz);
    app.component('ObserverViz', ObserverViz);
    app.component('BackpressureViz', BackpressureViz);
    app.component('CopyOnWriteViz', CopyOnWriteViz);
  },
} satisfies Theme;
