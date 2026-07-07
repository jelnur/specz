# ADR-0003: Spec-to-Spec Relationships

- Status: Accepted
- Date: 2026-07-07

## Context

Specs need to reference each other (a login spec depends on a password-policy
spec). The question was whether specz needs an explicit parent-child
hierarchy, typed relations, or plain cross-references. Candidates:

1. Free references in body text; folders provide topical grouping
2. Parent-child tree via a frontmatter `parent:` field, plus free references
3. Typed frontmatter references (`refines:`, `depends-on:`, `relates-to:`)

## Decision

Option 1: **free references + folders.**

- Specs reference each other inline in body text with `[[<id>]]` (e.g.
  `[[spz-auth-bz]]`), anywhere prose needs them.
- Folders under `specz/` provide human/agent-facing topical grouping and
  carry no semantic meaning; moving a spec between folders changes nothing.
- No relationship fields in frontmatter.

Rejected:

- **Parent-child tree**: creates a second hierarchy that drifts from (or
  must rigidly mirror) the folder layout; re-parenting rewrites frontmatter
  across files; cross-cutting requirements (e.g. rate limiting under both
  security and performance) break the single-parent assumption.
- **Typed references**: expressive but heavier — agents mislabel relation
  types, the checker needs cycle/orphan rules per type, and most projects
  use one relation type ~95% of the time. YAGNI for v1.

## Consequences

- Context extraction is a deterministic graph walk: load a spec plus its
  1-hop reference neighborhood (transitively if asked).
- The checker has one rule: every `[[id]]` must resolve to an existing,
  non-archived spec.
- No status roll-up ("epic DONE when children DONE"); the outline file and
  folders serve as the progress-aggregation proxy.
- Upgrade path stays open: `[[id]]` syntax can later gain optional type
  qualifiers (Option 3) without breaking any existing reference. A tree
  could not be retrofitted or removed cleanly.
