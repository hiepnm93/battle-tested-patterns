# SOP 08: Release Process

## Trigger

When a content milestone is reached and ready for a version tag.

Use [semver](https://semver.org/): bump **minor** for new features/patterns, **patch** for fixes-only batches.

## Pre-Release Checklist

### 1. AI Agent Review (required before every tag)

Run two sub-agents locally via Claude Code:

**Contributor Agent** — simulates a first-time contributor:
```
Prompt: Walk through the contribution process as described in CONTRIBUTING.md
and .sop/01-new-pattern.md. Report friction points, unclear instructions,
and missing steps.
```

**Reviewer Agent** — audits content quality:
```
Prompt: Review all pattern documents for production proof precision,
code quality, exercise format consistency, Chinese translation parity,
and stale references. Rate each dimension 1-10.
```

- [ ] Both agents complete
- [ ] All critical findings (score < 7) addressed
- [ ] Fixes committed before tagging

### 2. Quality Gates

- [ ] `pnpm test` — all TypeScript tests pass
- [ ] `cargo test` — all Rust tests pass (in `exercises/rust/`)
- [ ] `pnpm lint` — no markdown lint errors
- [ ] `pnpm build` — docs site builds
- [ ] `pnpm verify-links` — all production proof links alive
- [ ] CI green on latest commit
- [ ] No `<!-- TODO -->` markers in completed pattern docs

### 3. Content Verification

- [ ] All patterns have complete sections (One Liner through When NOT to Use)
- [ ] All patterns have ≥ 2 production proofs with precise line numbers
- [ ] All patterns have exercises with passing tests
- [ ] All patterns have Chinese translations
- [ ] README pattern table matches actual patterns
- [ ] Homepage pattern table matches actual patterns
- [ ] Sidebar navigation includes all patterns (both locales)

### 4. Tag and Release

```bash
# Generate changelog
pnpm changelog

# Review and commit
git add CHANGELOG.md
git commit -m "chore: prepare release vX.Y.Z"

# Tag
git tag vX.Y.Z
git push && git push --tags
```

`release.yml` will automatically create a GitHub Release with notes.

### 5. Post-Release

- [ ] Verify GitHub Release was created
- [ ] Verify docs site is deployed and accessible
- [ ] Update any external references (if applicable)
