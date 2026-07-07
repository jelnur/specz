# ADR-0002: Requirement ID Grammar

- Status: Accepted
- Date: 2026-07-07 (amended same day: lowercase, mnemonic segment, segment registry)

## Context

Requirement IDs get embedded in code comments across the entire repo, making
them the hardest artifact to migrate — they must be immutable from day one.
The original draft used typed prefixes (`FR-`/`NFR-`) with a `[A-Z][A-Z]`
suffix and the FR/NFR boundary is blurry enough that requirements get re-classified — which would force rewriting every referencing comment or letting the prefix lie.

A first cut of this ADR chose bare `SPZ-[A-Z0-9]{2}`, but two-char random
suffixes carry zero meaning for humans reading code comments. A mnemonic
domain segment fixes that — provided it does not re-import the mutability
problem that killed typed prefixes.

## Decision

**Lowercase, generic prefix, frozen mnemonic segment, alphanumeric suffix:**

```
spz-<segment>-<suffix>
segment: [a-z0-9]{2,5}   — from the project's segment registry
suffix:  [a-z0-9]{2}     — random, non-sequential
```

Example: `spz-auth-bz`, `spz-perf-c1`.

- **The ID is pure identity and immutable.** Requirement type (`functional`,
  `non-functional`, …) lives in the spec file's frontmatter.
- **The segment is a frozen mnemonic hint**, chosen at creation and never
  renamed. It is *not* validated against the spec's folder path — specs move
  freely without ID changes. It asserts a topic, not a checkable
  classification, so it cannot "lie" the way a frozen `FR-` prefix could.
- **Segments come from a controlled vocabulary** in `specz/config.yaml`
  (`segments:` list, each with a one-line description). `/specz:init` seeds a
  starter set (`auth`, `sec`, `perf`, `api`, `ui`, `data`, `infra`, `test`,
  `docs`, `core`); adding a segment is an explicit registry edit. The checker
  rejects IDs whose segment is unregistered — this prevents synonym sprawl
  (`auth` / `authn` / `login`) that would break category grep.
- **Uniqueness is carried by the whole ID**: `spz-auth-bz` and `spz-api-bz`
  may coexist. IDs are never reused, including those of archived specs.

Rejected:

- **Typed prefixes (`FR-`/`NFR-`)**: freezes classification into the
  immutable key; re-classification rewrites every referencing comment.
  `FR-` also grep-collides with Jira-style keys in many repos.
- **Typed-but-frozen prefixes**: prefix and frontmatter become two sources
  of type that are allowed to disagree about a formal property.
- **Folder-synced segment**: moving a spec or renaming a folder would force
  ID renames across every referencing comment — the typed-prefix mistake
  with a different coat of paint.
- **Bare `spz-xx` (no segment)**: shortest, but meaningless to humans and
  no category grep.

## Consequences

- `# SPECZ: spz-auth-bz, spz-perf-c1` is readable at a glance; `rg
  "spz-auth"` finds all auth-mapped code with no tooling.
- Re-classifying or moving a requirement touches zero code comments.
- If a requirement genuinely migrates domains (auth → billing), the hint
  goes stale; accepted as rare, and the registry description plus spec
  frontmatter remain the truth.
- The checker needs the segment registry to validate IDs; an unregistered
  segment is a structural error.
- Suffix space is 1,296 per segment; the suffix may extend to
  `[a-z0-9]{3}` if a segment exhausts it.
