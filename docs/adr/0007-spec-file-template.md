# ADR-0007: Spec File Template

- Status: Accepted
- Date: 2026-07-07

## Context

Frontmatter is pinned by ADR-0002 (`id`, `type`) and ADR-0004 (`status`,
`synced`). The open question was how prescriptive the body should be:
free-form prose, required sections, or a formal requirement grammar
(EARS / Gherkin).

## Decision

**Required sections: `## Description` and `## Acceptance Criteria`;
everything else optional.**

```markdown
---
id: spz-auth-bz
type: functional
status: done
synced: a3f9c1e2
---
# Login with email+password

## Description
Users authenticate with email and password. Lockout after 5 consecutive
failures (see [[spz-sec-k9]]).

## Acceptance Criteria
- [ ] valid credentials → session cookie issued
- [ ] 5 consecutive failures → account locked 15 minutes
```

- The H1 is the spec's title (extracted into the SPECS.md index; no
  `title:` frontmatter duplication).
- `## Description` holds intent and context, with `[[id]]` references
  (ADR-0003) woven into prose.
- `## Acceptance Criteria` is a markdown checklist of individually
  verifiable statements. These are the firm basis for the reconcile
  skill's code-vs-spec check and the input TDD skills turn into tests.
- The checker enforces section presence structurally (grep-cheap). AC
  *quality* remains a review concern, not a checker concern.
- EARS-style phrasing may be used voluntarily inside criteria; it is not
  enforced.

Rejected:

- **Free-form body**: zero friction but no guaranteed acceptance criteria —
  "does code match spec?" degrades into judgment over vibes, and TDD has
  no mechanical hook.
- **Formal grammar (EARS/Gherkin) enforced**: maximum precision, but high
  authoring friction and poor fit for many requirement types; historically
  the death of RE tools. YAGNI — option B can adopt it voluntarily.

## Consequences

- Semantic verification and test generation have an enumerated, per-item
  target instead of prose.
- Pure constraints (e.g. "p95 < 200 ms") carry a slightly forced
  Description/AC split; accepted.
- Boilerplate ACs are possible; the review skill should flag
  non-verifiable criteria.
