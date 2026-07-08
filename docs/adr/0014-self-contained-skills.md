# ADR-0014: Tailored Self-Contained Skill Content

- Status: Accepted
- Date: 2026-07-08

## Context

Several skills need the same format rules (ID grammar ADR-0002, comment
grammar ADR-0009, spec template ADR-0007, body hash ADR-0004). Candidates:
each skill inlines exactly the rules it uses; a shared conventions file
every skill reads first; or full duplication of the complete rule set in
all seven skills.

## Decision

**Tailored self-contained**: each SKILL.md inlines exactly the rules it
uses, stated once with canonical examples and ADR citations. No shared
conventions file.

- One read gives an agent its full instructions; there is no "read X
  first" indirection an agent can skip — the dominant failure mode of
  prompt-only tooling, and format precision is exactly where improvisation
  hurts most.
- Portability stays "copy the file".
- Definitions that appear in more than one skill (hash pipeline, grammar
  regexes, index regeneration rule) are copied verbatim; the ADRs remain
  the single source of truth a fix propagates from.

Rejected:

- **Shared conventions reference**: single edit point, but adds a skippable
  read on every invocation and `${CLAUDE_PLUGIN_ROOT}` coupling.
- **Full duplication**: any one file teaches everything, but 7× drift
  surface and every invocation pays for rules it never uses.

## Consequences

- A format-rule change touches 2–3 skill files; acceptable because rules
  are frozen by ADRs and change rarely.
- Verification must include a consistency check that duplicated
  definitions are byte-identical across skills.
