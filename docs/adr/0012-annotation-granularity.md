# ADR-0012: Annotation Granularity — File Default + Overrides

- Status: Accepted
- Date: 2026-07-08

## Context

The original draft annotated every function and class. That yields a
uniform rule but forces vague mappings onto glue code, spams cross-cutting
NFRs across every unit, and adds diff churn and token cost — the pollution
specz exists to fight. The opposite extreme (file-level only) destroys
function-level precision, the core of the context-extraction pitch.

## Decision

**Every source file carries a file-level mapping; inner units are annotated
only when their spec set differs from the file default.**

- **File default:** a `SPECZ:` line at the top of the file (native comment
  syntax, ADR-0009), or the file's `.specz` sidecar for uncommentable
  files (ADR-0008). Every source file in scope must have one — this keeps
  coverage a deterministic, grep-cheap check.
- **Inner override:** a function/class/snippet gets its own `SPECZ:` line
  only when its spec set is *narrower, extra, or different* relative to
  the file default. An override states the unit's **complete** spec set
  (replaces, not extends, the default — no set arithmetic needed to read
  it).
- **Inheritance:** un-annotated units inherit the file default. A bare
  helper means "serves the same specs as the file."
- **Cross-cutting NFRs** map once at file level (or via a folder's files
  during `init`), never repeated per function.
- Files out of scope (vendored code, generated artifacts, lockfiles) are
  excluded via `specz/config.yaml` ignore patterns; `check` skips them.

Rejected:

- **Every function/class**: zero-judgment but maximal noise — forced
  mappings on glue code say nothing, NFRs metastasize, every diff churns.
- **File-level only**: minimal churn but context extraction degrades to
  whole-file loads; a 500-line file serving six specs has no addressable
  precision.

## Consequences

- `check` gains a structural rule: every in-scope file has a file-level
  mapping (inline or sidecar); a bare file is a finding — "unmapped code"
  detection survives at file granularity.
- A `SPECZ:` line on an inner unit carries real signal: this unit differs
  from its file.
- Override correctness (is the differing set still right?) is semantic —
  `audit`'s job, not `check`'s.
- Context extraction for an ID: files whose default lists it, plus inner
  units that override with it — both are single `rg` passes.
- Agents need the two-level rule in the conventions block; `map` skill
  encodes the "differs → own line" test.
