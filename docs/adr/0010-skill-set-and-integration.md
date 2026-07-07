# ADR-0010: Skill Set, Workflow, and Framework Integration

- Status: Accepted
- Date: 2026-07-08

## Context

specz is a traceability layer, not a development framework: brainstorming,
planning, and implementation belong to whichever framework the project uses
(superpowers, gstack, plain agent chat). specz skills must (a) capture the
specs those frameworks produce into specz format — or better, get them
generated in specz format directly, (b) keep implementation artifacts mapped
automatically during development, and (c) stay invocable manually on demand.
The open questions were the skill inventory and how specz gets invoked from
inside foreign workflows without forking them.

## Decision

### Workflow stages

| Stage | What happens | Skill | Invocation |
|---|---|---|---|
| 0 Adoption | bootstrap `specz/`; brownfield reverse-engineering (review gate; generated specs start `draft`) | `init` | manual, once |
| 1 Capture | design/plan artifact → spec files (mint IDs, ACs, index) | `capture` | auto after design/plan; manual |
| 2 Context | load precise slice for an ID: spec + `[[refs]]` 1-hop + mapped code | `context` | auto at task start; manual |
| 3 Mapping | maintain `SPECZ:` lines and `.specz` sidecars as code is written | `map` | auto during implementation; manual |
| 4 Reconcile | verify ACs, flip `todo → done`, write `synced` hash; repair drift | `reconcile` | auto at task end; manual |
| 5 Verify | structural checks (deterministic) / semantic review (LLM) | `check` / `audit` | CI + hook + manual / manual, scheduled |

### Skill inventory (7)

- **`/specz:init`** — create `specz/` (config.yaml with segment registry,
  `SPECS.md`); on brownfield, traverse code, draft specs, annotate, and
  gate on human review.
- **`/specz:capture`** — convert a design/plan artifact or prose ask into
  spec files: mint IDs (ADR-0002), write Description + Acceptance Criteria
  (ADR-0007), set `todo`, regenerate the index (ADR-0006). The narrative
  doc remains prose; specz files are the requirements of record.
- **`/specz:context`** — for a given ID: load the spec, its 1-hop `[[id]]`
  neighborhood (ADR-0003), and `rg "SPECZ:.*<id>"` mapped code paths.
- **`/specz:map`** — annotate code with `SPECZ:` lines (ADR-0009), create
  or update `.specz` sidecars (ADR-0008).
- **`/specz:reconcile`** — per-AC verification, status flip, `synced` hash
  update (ADR-0004); the repair tool for every detected inconsistency.
- **`/specz:check`** — deterministic, grep-fast, no LLM: dangling IDs,
  unregistered segments, orphan sidecars, stale index, hash mismatches,
  references to archived specs. CI-gateable.
- **`/specz:audit`** — semantic, LLM-driven: does mapped code satisfy the
  ACs; unmapped-code sweep (new-code vs dead-code triage). Deliberate runs.

The seven inconsistency states map onto: structural detection in `check`,
semantic detection in `audit`, repair in `reconcile`; "spec exists, no code
yet" is simply a `todo` spec — the dev framework's queue, assisted by
`context` + `map`.

### Integration mechanism

**Convention layer plus one deterministic hook:**

- `/specz:init` writes a short rules block into the project's agent
  instructions (e.g. `CLAUDE.md`): after producing a design/plan artifact,
  invoke `/specz:capture` — or generate acceptance criteria in specz format
  directly; while writing code, maintain mappings per `/specz:map`; at task
  completion, run `/specz:reconcile`.
- `init` also installs a PostToolUse hook running `check` (structural only,
  no LLM, fast) on edited files, so forgotten mappings surface at edit time
  instead of CI.

Rejected:

- **Wrapper skills** (`/specz:brainstorm` wrapping a framework's skill):
  deterministic seam, but couples specz to N frameworks × M skills and
  their release cadence, and forces users to abandon existing commands.
- **Hooks-only integration**: cannot detect intent ("a design doc was just
  written"), is Claude-Code-specific (kills other-agent portability), and
  LLM work on every file write is slow and expensive.

## Consequences

- specz works beside any framework that reads the rules file; portability
  to other agents reduces to porting one rules block plus text skills.
- The convention layer is probabilistic — an agent can forget; the check
  hook and CI `check` are the deterministic safety net that catches misses.
- The rules block adds a small standing token cost to every session.
- Skill names, the rules-block wording, and the hook definition are
  implementation surface for the upcoming skill-authoring phase.
