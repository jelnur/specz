# ADR-0006: Outline File (SPECS.md) Structure

- Status: Accepted
- Date: 2026-07-07

## Context

`SPECS.md` is the entry point an agent loads first to orient itself before
extracting a precise context slice. It must answer both "what is this
product?" (narrative) and "what specs exist, in what status?" (inventory)
without forcing a scan of every spec file's frontmatter. Candidates:

1. Hand-curated overview only (no spec listing)
2. Generated index only (no narrative)
3. Hybrid: curated narrative + a marked generated-index block

## Decision

Option 3: **hybrid — human-owned narrative above, skill-owned index below.**

```markdown
# <Project> Specs
<one-paragraph product vision>

## Domains
- auth: login, sessions, MFA
- perf: latency budgets

## Conventions
<project-specific notes>

<!-- specz:index:begin -->
| id | title | status | path |
|----|-------|--------|------|
| spz-auth-bz | Login | done | auth/spz-auth-bz.md |
<!-- specz:index:end -->
```

- The narrative half is hand-written and only changes when the product
  story changes.
- The fenced `specz:index` block is rewritten **only by specz skills**
  whenever specs are added/removed or frontmatter changes.
- The checker verifies index freshness against the tree: a stale block is
  a structural error and is mechanically auto-fixable. Derived facts get
  verified, never trusted (same philosophy as ADR-0004).
- Per-segment progress roll-up (count of `done`) is derivable from the
  index — this is the aggregation proxy ADR-0003 pointed to.

Rejected:

- **Overview only**: inventory would require reading every frontmatter in
  `specz/` — the exact token cost specz exists to eliminate; no roll-up.
- **Index only**: committed derived data with no narrative — cold-start
  agents learn what exists but not what the product is; drifts silently
  without the narrative benefits.

## Consequences

- One file read gives an agent both orientation and full inventory.
- Duplicate truth (frontmatter + index) is tolerated because the checker
  guards it and regeneration is mechanical.
- The index block is a merge-conflict magnet on busy repos; regenerating
  after merge is a single skill invocation and resolves any conflict.
- Humans must not hand-edit inside the fence; the checker flags it if they
  do.
