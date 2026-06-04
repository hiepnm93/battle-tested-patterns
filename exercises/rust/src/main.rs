mod actor_model;
mod backpressure;
mod batch_processing;
mod bitmask;
mod bloom_filter;
mod circuit_breaker;
mod consistent_hashing;
mod copy_on_write;
mod dependency_graph;
mod dirty_flag;
mod double_buffering;
mod event_loop;
mod flyweight;
mod iterator;
mod logical_clock;
mod lru_cache;
mod merge_iterator;
mod middleware_chain;
mod min_heap;
mod object_pool;
mod observer;
mod rate_limiter;
mod reference_counting;
mod retry_backoff;
mod ring_buffer;
mod semaphore;
mod skip_list;
mod state_machine;
mod trie;
mod write_ahead_log;

fn main() {
    println!("Run `cargo test` to execute exercises.");
}
