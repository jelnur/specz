# ADR-0004: Status Model — Stored Workflow State, Computed Sync State

- Status: Accepted
- Date: 2026-07-07

## Context

The original draft used one enum: `DRAFT, TODO, DONE, ARCHIVED, CHANGED`.
`CHANGED` is a different kind of fact from the others: workflow position is
a decision, while "spec edited since code was last reconciled" is a
derivable property of the repo. Storing it manually means a human editing a
spec through the GitHub UI, or a non-specz-aware agent, silently skips the
DONE→CHANGED flip — the exact silent-drift failure specz exists to prevent.
It also erases the prior state (was it `done` or `todo` before the edit?).

## Decision

**Split the two concerns: workflow status is stored; sync state is computed.**

Frontmatter:

```yaml
status: draft | todo | done | archived   # stored, set by humans/agents
synced: a3f9c1e2                         # body hash at last reconciliation
```

- `status` is a single clean workflow axis:
  `draft` (being written) → `todo` (approved, awaiting implementation) →
  `done` (implemented & reconciled) → `archived` (retired; mapped code is
  dead by definition).
- `synced` is written **only by the reconcile skill**, never by hand: the
  first 8 hex chars of SHA-256 over the normalized spec body (content after
  the frontmatter block, leading/trailing blank lines stripped). It is
  present only on `done` specs.
- **There is no stored CHANGED state.** The checker recomputes the body
  hash; `hash(body) != synced` on a `done` spec ⇒ reported as *changed*
  (spec edited, code possibly stale). Any edit by anyone through any tool
  triggers this — no discipline required.

Rejected:

- **Single enum incl. CHANGED**: relies on editors remembering the flip
  (silent rot); erases prior state; conflates decision with derivable fact.
- **Stored CHANGED auto-flipped by the checker**: stale between runs, two
  sources for one fact, and the checker mutating spec files breaks
  read-only CI gates and dirties working trees — it still needs the hash
  anchor anyway, so it is Option B plus failure modes.

## Consequences

- Drift detection is deterministic, grep-cheap, and CI-gateable.
- `synced` doubles as an audit record: which version of the spec the code
  was last verified against.
- Sync state is not visible by reading the file alone — running the checker
  is the way to ask; accepted, since the checker is specz's core component.
- Reconciliation = update code/mappings, then rewrite `synced` — updating
  the anchor *is* the act of declaring reconciliation complete.
- Hash normalization must stay stable across specz versions; a change to
  the normalization rule is a breaking change requiring a migration.
