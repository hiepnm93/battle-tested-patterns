# SOP 12: Related Patterns Bidirectionality Audit

## Trigger

- After adding or modifying Related Patterns tables in any pattern document
- After adding a new pattern (which creates new connections)
- Periodically as a quality check before release

## Rule

If pattern A's Related Patterns table lists pattern B, then pattern B's Related Patterns table **must** list pattern A back. This rule applies to both EN and ZH versions.

One-way links are a content defect: they suggest to the reader that only one pattern relates to the other, hiding a useful connection from the reverse direction.

## Audit Steps

### 1. Extract All Edges

For every `docs/patterns/*/index.md`, parse the `## Related Patterns` table and extract `(source, target)` pairs from the link URLs.

### 2. Check Bidirectionality

For each edge `(A, B)`, verify that `(B, A)` also exists. Any missing reverse edges are defects.

### 3. Add Missing Back-Links

For each missing `(B, A)`:

- [ ] Open `docs/patterns/B/index.md`
- [ ] Add a row to its `## Related Patterns` table linking to A
- [ ] Write a meaningful relationship description (not generic "related to")
- [ ] Do the same in `docs/zh/patterns/B/index.md` using the Chinese header `## 相关模式`
- [ ] Use Chinese relationship description in ZH version

### 4. Verify Consistency

After fixing, re-run the audit to confirm 100% bidirectionality.

## Relationship Description Guidelines

When adding a back-link, the description should explain the relationship **from the target pattern's perspective**:

```
Pattern A → B: "B provides the underlying data structure for A"
Pattern B → A: "A uses B as its underlying storage layer"
```

Both descriptions should be specific and complementary, not just "related to each other."

## Common Pitfalls

- ZH files use `## 相关模式` not `## Related Patterns`
- Grep for the pattern slug in the Related Patterns section may match code variable names — use the markdown link format `](/patterns/slug/)` for precise matching
- When a pattern has many Related Patterns entries, check for deduplication before adding

## Automation

A quick audit script (save to `$TMPDIR` and run):

```python
import os, re, glob

patterns_dir = "docs/patterns"
edges = set()
for path in glob.glob(f"{patterns_dir}/*/index.md"):
    slug = os.path.basename(os.path.dirname(path))
    with open(path) as f:
        content = f.read()
    # Find Related Patterns section
    m = re.search(r"## Related Patterns.*?\n\|.*?\n\|[-|]+\n(.*?)(?=\n##|\Z)", content, re.DOTALL)
    if not m:
        continue
    for link in re.findall(r"\(/patterns/([^/]+)/\)", m.group(1)):
        edges.add((slug, link))

missing = [(a, b) for (a, b) in edges if (b, a) not in edges]
if missing:
    print(f"Found {len(missing)} one-way links:")
    for a, b in sorted(missing):
        print(f"  {a} → {b} (but {b} does NOT link back to {a})")
else:
    print("All Related Patterns links are bidirectional.")
```
