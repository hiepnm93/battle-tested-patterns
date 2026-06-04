# Pattern: Merge Iterator
# Difficulty: Basic -> Intermediate

import heapq


def merge_k_sorted(streams: list[list[int]]) -> list[int]:  # TODO: implement
    heap: list[tuple[int, int, int]] = []  # (value, stream_idx, element_idx)

    for s, stream in enumerate(streams):
        if stream:
            heapq.heappush(heap, (stream[0], s, 0))

    result: list[int] = []
    while heap:
        val, stream_idx, elem_idx = heapq.heappop(heap)
        result.append(val)
        next_idx = elem_idx + 1
        if next_idx < len(streams[stream_idx]):
            heapq.heappush(heap, (streams[stream_idx][next_idx], stream_idx, next_idx))

    return result


# ─── Tests (do not modify below this line) ───

def test_merge_three_sorted():
    lists = [[1, 4, 7], [2, 5, 8], [3, 6, 9]]
    result = merge_k_sorted(lists)
    assert result == [1, 2, 3, 4, 5, 6, 7, 8, 9]

def test_merge_unequal_lengths():
    lists = [[1, 10], [2, 3, 4, 5], [6]]
    result = merge_k_sorted(lists)
    for i in range(1, len(result)):
        assert result[i] >= result[i - 1], f"not sorted at index {i}: {result}"

def test_merge_empty_lists():
    result = merge_k_sorted([[], [], []])
    assert result == []

def test_merge_single_list():
    result = merge_k_sorted([[5, 10, 15]])
    assert result == [5, 10, 15]
