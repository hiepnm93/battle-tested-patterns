# SOP 11: Pattern Difficulty Classification

## Trigger

When adding a new pattern or reviewing difficulty labels.

## Classification Criteria

### Beginner

- **Single core mechanism** with minimal prerequisites
- Can be understood in one sitting without prior pattern knowledge
- Implementation is typically < 50 lines in any language
- Examples: bitmask (bitwise ops), ring-buffer (modular arithmetic), observer (subscribe/notify), dirty-flag (boolean check)

### Intermediate

- **Combines 2-3 concepts** that must work together
- Requires understanding at least one beginner-level concept first
- Implementation involves non-trivial data structure composition or state management
- Examples: LRU cache (hash map + doubly linked list), circuit-breaker (state machine + failure counting + timeout), bloom-filter (hash functions + bit array + probability)

### Advanced

- **Complex multi-component system** with subtle invariants
- Requires understanding multiple intermediate concepts as prerequisites
- Implementation involves concurrency, disk I/O patterns, or complex tree balancing
- Correctness depends on non-obvious properties (probabilistic guarantees, lock-free invariants, crash recovery semantics)
- Examples: MVCC (versioned snapshots + garbage collection), LSM tree (memtable + SSTable + compaction + bloom filter), work-stealing (lock-free deques + cache-line awareness)

## Where Difficulty Is Stored

- Frontmatter field: `difficulty: "beginner"` / `"intermediate"` / `"advanced"` in `docs/patterns/<name>/index.md`
- Must match in both EN and ZH versions
- Displayed by `<DifficultyBadge />` component (reads frontmatter automatically)

## When to Reclassify

- If feedback shows learners consistently struggle with a "beginner" pattern → promote to intermediate
- If a "intermediate" pattern turns out to have no real prerequisites → demote to beginner
- Reclassification requires updating both EN and ZH frontmatter

## Current Distribution

Target: roughly 1/3 each across all patterns.
