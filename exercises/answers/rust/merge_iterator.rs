use std::collections::BinaryHeap;
use std::cmp::Reverse;

pub fn merge_k_sorted(streams: &[Vec<i32>]) -> Vec<i32> {
    // (value, stream_index, element_index)
    let mut heap: BinaryHeap<Reverse<(i32, usize, usize)>> = BinaryHeap::new();

    for (s, stream) in streams.iter().enumerate() {
        if !stream.is_empty() {
            heap.push(Reverse((stream[0], s, 0)));
        }
    }

    let mut result = Vec::new();
    while let Some(Reverse((val, stream_idx, elem_idx))) = heap.pop() {
        result.push(val);
        let next_idx = elem_idx + 1;
        if next_idx < streams[stream_idx].len() {
            heap.push(Reverse((streams[stream_idx][next_idx], stream_idx, next_idx)));
        }
    }
    result
}
