# specz v1 Skills — Design

- Date: 2026-07-08
- Status: Approved (brainstorming session)
- Governing ADRs: 0001–0012 (this design adds 0013, 0014)

## Goal

Author the seven pure-markdown skills decided in ADR-0010, packaged per
ADR-0011, and verify them against a fixture project before calling v1 done.
specz remains a traceability layer: the skills capture, map, and reconcile
specs — they never brainstorm, plan, or implement.

## Decisions made in this session

1. **Packaging: Claude Code plugin.** `.claude-plugin/plugin.json` (name
   `specz`) plus `.claude-plugin/marketplace.json` (single entry) so
   `/plugin marketplace add` works directly from this repo and skills invoke
   as `/specz:<name>` — matching ADR-0010's naming. Still pure markdown: no
   scripts, no hooks (ADR-0011 holds). → ADR-0013.
2. **Skill content: tailored self-contained.** Each SKILL.md inlines exactly
   the format rules it uses, stated once with canonical examples and ADR
   citations. No shared conventions file an agent could skip; portability
   stays "copy the file". Cost: a format change touches 2–3 skills; the ADRs
   remain the source of truth. → ADR-0014.
3. **Verification: fixture-project testing.** Each skill flow is exercised by
   a subagent against a committed fixture app before v1 is done (see
   Testing).

## Repository layout

```
specz/
  .claude-plugin/
    plugin.json          # { "name": "specz", ... }
    marketplace.json     # single-entry marketplace
  skills/
    init/SKILL.md
    capture/SKILL.md
    context/SKILL.md
    map/SKILL.md
    reconcile/SKILL.md
    check/SKILL.md
    audit/SKILL.md
  docs/adr/              # 0001–0012 + new 0013, 0014
  tests/fixture/webapp/  # committed fake app for verification
```

## Skill anatomy (all seven)

Every SKILL.md contains:

- Frontmatter: `name`, `description`. The description doubles as the
  auto-trigger condition ("Use when …") for the convention layer.
- "When to use / when not to use."
- A workflow section — a numbered checklist for multi-step skills
  (`init`, `capture`, `reconcile`, `audit`).
- Inlined format rules with canonical examples, each citing its ADR.
- Failure behavior. Uniform rules:
  - No `specz/` directory → stop; tell the user to run `/specz:init`.
  - Unresolvable ID → report it; never guess or invent.
  - Unregistered segment → propose an explicit `config.yaml` registry edit;
    never silently add one.
  - `context`, `check`, `audit` are strictly read-only.
  - `capture` never overwrites an existing spec file.
  - Destructive ambiguity (archiving, re-anchoring a changed spec) → ask.

## The seven skills

### `/specz:init` — adoption (stage 0)

Two modes, detected by presence of source files.

**Greenfield:**
1. Create `specz/config.yaml`: starter segment registry (`auth`, `sec`,
   `perf`, `api`, `ui`, `data`, `infra`, `test`, `docs`, `core`, each with a
   one-line description) and `ignore:` glob patterns (vendored code,
   generated artifacts, lockfiles) per ADR-0012.
2. Create `specz/SPECS.md`: hand-narrative skeleton (vision, Domains,
   Conventions) + empty `<!-- specz:index:begin/end -->` fence (ADR-0006).
3. Create one folder per registered segment (ADR-0005 convention).
4. Append the rules block (below) to the project's agent-instructions file:
   `CLAUDE.md` by default, `AGENTS.md` if that is what the project uses,
   between `<!-- specz:rules:begin/end -->` markers.

**Brownfield (additionally):**
5. Traverse in-scope code; propose extra registry segments.
6. Draft specs (`status: draft`) for observed behavior; annotate files per
   the granularity rule; regenerate the index.
7. **Stop at the human review gate**: generated specs stay `draft` until a
   human promotes them to `todo`/`done`.

Idempotent: existing `specz/` → offer to update the rules block or config;
never clobber existing specs.

### `/specz:capture` — design/plan → specs (stage 1)

Input: a design/plan document path, or a prose ask.

1. Extract discrete requirements from the artifact.
2. Per requirement: choose a segment from the registry (propose a registry
   addition if none fits); mint an ID — `spz-<segment>-<suffix>`, suffix two
   random `[a-z0-9]` chars, uniqueness verified by `rg` across `specz/`
   (including archived specs; IDs are never reused) (ADR-0002).
3. Write the spec file per the ADR-0007 template: frontmatter `id`, `type`,
   `status: todo`, no `synced`; H1 title; `## Description` with `[[id]]`
   references woven in (ADR-0003); `## Acceptance Criteria` as a checklist of
   individually verifiable statements.
4. Place the file in the segment-matching folder (ADR-0005 convention).
5. Regenerate the SPECS.md index block (ADR-0006).

The narrative source document remains prose and is not modified; specz files
become the requirements of record.

### `/specz:context` — precise slice for an ID (stage 2)

Input: one or more spec IDs. Read-only.

1. Resolve ID → file by search (`rg --files -g "<id>.md"`), never by path
   construction (ADR-0005).
2. Load the spec plus its 1-hop `[[id]]` neighborhood (ADR-0003);
   transitively only if asked.
3. Find mapped code: `rg "SPECZ:.*<id>"` (inline) and `rg -l "<id>" -g
   "*.specz"` (sidecars). `SPECZ:` marker = mapping declaration; a bare ID in
   prose = mention, not mapping (ADR-0009).
4. Output a compact slice: spec body, neighbor titles + statuses, mapped
   files with any overriding inner units.

### `/specz:map` — maintain mappings (stage 3)

Encodes ADR-0012's two-level rule as a decision test:

- **File default:** every in-scope source file carries a `SPECZ:` line at the
  top (native comment leader), or a `<filename>.specz` sidecar if the format
  cannot carry comments (ADR-0008). Sidecar format: one spec ID per line,
  nothing else, same directory as the target.
- **Inner override:** a function/class/snippet gets its own `SPECZ:` line
  only when its spec set is narrower, extra, or different from the file
  default — and the override states the unit's **complete** set (replaces,
  never extends).
- Canonical written form (ADR-0009): `<leader> SPECZ: <id>[, <id>]*` — e.g.
  `# SPECZ: spz-auth-bz, spz-perf-c1`. Skills always write canonical form.
- Cross-cutting NFRs map once at file level, never per function.
- Files matching `config.yaml` `ignore:` patterns are out of scope.

### `/specz:reconcile` — verify, flip, anchor (stage 4)

The only writer of `synced`, and the repair tool for detected drift.
Input: spec ID(s), or "the task just finished" (infer touched specs from the
diff).

1. Per spec, verify each acceptance criterion against the mapped code; tick
   `- [x]` only as evidence is confirmed.
2. All ACs verified → flip `status: todo → done`; compute the body hash;
   write `synced` (ADR-0004).
3. Changed specs (`done` with hash mismatch): re-verify ACs against current
   code; update code/mappings as needed; re-anchor the hash. Re-anchoring
   without re-verification is forbidden.
4. Regenerate the index if any frontmatter changed.
5. Finish by running the `check` pipeline and reporting its result.

### `/specz:check` — structural verification (stage 5, deterministic)

Grep-only; no LLM judgment; prescribes an exact, numbered, reproducible
command pipeline (`rg`, glob, `shasum`) that can be pasted into CI
(ADR-0011). Checks:

| # | Finding | Severity |
|---|---------|----------|
| 1 | Dangling ID (in `SPECZ:` line, `[[ref]]`, or sidecar) | error |
| 2 | Unregistered segment in any ID | error |
| 3 | Orphan sidecar (target file missing) | error |
| 4 | Stale or hand-edited SPECS.md index block | error |
| 5 | Spec missing `## Description` / `## Acceptance Criteria` | error |
| 6 | `done` spec, recomputed hash ≠ `synced` → **changed** | error |
| 7 | Reference to an archived spec | error |
| 8 | In-scope file with no file-level mapping | error |
| 9 | Spec outside its segment-matching folder | warning |

Output: findings table + pass/fail summary. Read-only — repair is
`reconcile`'s job.

### `/specz:audit` — semantic verification (stage 5, deliberate)

LLM-driven; scope chosen at invocation (segment, folder, or all `done`
specs). Read-only; findings route to `reconcile`/`capture`.

- Per spec: read ACs + mapped code; judge whether the code satisfies each
  criterion.
- Flag non-verifiable or boilerplate ACs (ADR-0007) and suspicious inner
  overrides (ADR-0012).
- Unmapped-code sweep: recently-touched files vs mapping coverage → triage
  new-code-needing-specs vs dead-code.
- Large scopes fan out via parallel subagents, one per spec cluster.

## The rules block (written by `init`)

```markdown
<!-- specz:rules:begin -->
## specz traceability rules
This project tracks requirements in `specz/` (see specz/SPECS.md).
- After producing any design or plan artifact, run /specz:capture to turn it
  into spec files (or write acceptance criteria in specz format directly).
- When starting work on a spec ID, run /specz:context to load its slice.
- While writing code, maintain mappings: every source file starts with a
  `SPECZ:` line (or has a `.specz` sidecar); annotate inner units only when
  their spec set differs (see /specz:map).
- When a task is complete, run /specz:reconcile to verify acceptance
  criteria and update spec status.
- Never edit `status: done`/`synced:` by hand, or the SPECS.md index block.
<!-- specz:rules:end -->
```

## Deterministic core — pinned once, repeated verbatim

Two definitions must be word-for-word identical in every skill that carries
them:

- **Body hash** (`reconcile` writes it, `check` verifies it): take the
  content after the closing `---` of the frontmatter block; strip leading and
  trailing blank lines; `shasum -a 256`; keep the first 8 hex characters.
  Both skills carry the identical command pipeline.
- **Grammar regexes** (`capture`, `map`, `check`): ID
  `spz-[a-z0-9]{2,5}-[a-z0-9]{2}`; mapping line
  `SPECZ: <id>[, <id>]*` (checker accepts flexible whitespace; skills write
  canonical form).

## Testing

`tests/fixture/webapp/` — a committed fake app (~6 files: two source files
in different comment syntaxes, `package.json` as the uncommentable case, a
config file, and `plan.md` as a capture input).

Each flow is verified by a subagent that receives only the skill text plus a
temp-dir copy of the fixture:

| Flow | Pass condition |
|------|----------------|
| init | `specz/` + config.yaml + SPECS.md + rules block created correctly |
| capture | `plan.md` → well-formed spec files, valid IDs, index updated |
| map | file defaults + a correct inner override + `package.json.specz` |
| check | all seeded errors detected (dangling ID, orphan sidecar, stale index, edited done-spec), no false positives |
| reconcile | ACs ticked, `todo → done`, `synced` matches independent hash |
| context | slice contains the spec, its 1-hop refs, mapped files — nothing else |
| audit | seeded AC-vs-code lie detected |

Findings loop back into skill wording until every flow passes.

## New ADRs

- **ADR-0013:** distribution as a Claude Code plugin (plugin.json +
  marketplace.json); concretizes ADR-0011, still zero scripts.
- **ADR-0014:** tailored self-contained skill content over a shared
  conventions reference; accepts bounded duplication to remove skippable
  indirection.

## Out of scope (v1)

Folder/region mapping (ADR-0008), PostToolUse hook and bundled checker
script (ADR-0011), typed references (ADR-0003), EARS/Gherkin enforcement
(ADR-0007), status roll-ups (ADR-0003).
