---
name: init
description: Use when adopting specz in a project (new or existing) — creates the specz/ structure (config.yaml, SPECS.md), installs the traceability rules block, and on brownfield codebases reverse-engineers draft specs gated on human review.
---

# specz init — Adopt specz in a project

**Announce:** "Using specz:init to bootstrap spec traceability."

## When to use
- Once per project, to adopt specz. Again later only to repair or update the rules block or config.

## When NOT to use
- `specz/` exists and the user wants new specs → `/specz:capture`.

## Workflow

Create a todo per numbered step.

### 1. Detect state
- `specz/` already exists → ask whether to update the rules block, update config, or abort. **Never overwrite existing spec files or the SPECS.md narrative.**
- Source files present (any code beyond docs/config)? Yes → brownfield: all steps apply. No → greenfield: steps 2–4 only.

### 2. Create specz/config.yaml

```yaml
# specz configuration (ADR-0002 segment registry, ADR-0012 scope)
segments:
  auth: authentication, sessions, identity
  sec: security hardening, secrets, access control
  perf: performance, latency, resource budgets
  api: external and internal API contracts
  ui: user interface, presentation
  data: persistence, schemas, migrations
  infra: build, deploy, environments
  test: test strategy and harnesses
  docs: documentation requirements
  core: cross-cutting domain logic
ignore:
  - "*.md"
  - "*.specz"
  - "specz/**"
  - "node_modules/**"
  - "vendor/**"
  - "dist/**"
  - "build/**"
  - "*.lock"
```

Tailor both lists to the project: drop segments that can't apply, extend `ignore:` with the project's vendored/generated paths. Segments are a controlled vocabulary (ADR-0002) — adding one later is an explicit edit here, never an ad-hoc invention.

### 3. Create specz/SPECS.md (ADR-0006)

```markdown
# <Project> Specs

<one-paragraph product vision — write it from what you know; the user owns it>

## Domains

- <segment>: <what lives there>

## Conventions

None yet.

<!-- specz:index:begin -->
| id | title | status | path |
|----|-------|--------|------|
<!-- specz:index:end -->
```

The narrative above the fence is human-owned. Everything between the index markers is machine-owned: only specz skills rewrite it, rows sorted lexicographically by id, path relative to `specz/`.

### 4. Create segment folders + install the rules block
- `mkdir` one folder under `specz/` per registered segment (convention only — specs may live anywhere under `specz/` and move freely; ADR-0005).
- Append the block below **verbatim** to the project's agent-instructions file: `CLAUDE.md`, or `AGENTS.md` if that is what the project uses; create `CLAUDE.md` if neither exists. If the markers already exist, replace the block between them instead of appending.

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

Greenfield ends here: report what was created and point the user at `/specz:capture` for their first specs.

### 5. (Brownfield) Survey the code
- In-scope files = all source files not matching `ignore:` globs.
- Identify the domains actually present; if one has no fitting segment, add it to `config.yaml` (2–5 lowercase alphanumerics + one-line description).

### 6. (Brownfield) Draft specs and annotate
Per observed behavior or requirement:
- Mint an ID (ADR-0002): `spz-<segment>-<suffix>`, suffix = two random characters from `a-z0-9`. Verify unused: `rg -l "spz-<segment>-<suffix>" specz/` must return nothing.
- Write `specz/<segment>/<id>.md`:

```markdown
---
id: <the minted id>
type: functional | non-functional
status: draft
---
# <Title>

## Description
<what the code does today, as intent; [[spz-...]] references where specs relate>

## Acceptance Criteria
- [ ] <individually verifiable statement observed from the code>
```

- Annotate the code (ADR-0012): every in-scope file gets a top `SPECZ:` line listing its spec IDs — canonical form `<comment-leader> SPECZ: <id>[, <id>]*` (uppercase marker, lowercase IDs, comma-space; ADR-0009). Uncommentable file → sidecar `<filename>.specz`, one ID per line. Inner units get their own line only when their spec set differs from the file default, stating the complete set.

### 7. (Brownfield) Regenerate index + STOP at the review gate
- Rebuild the index block in `specz/SPECS.md` (rule in step 3).
- **STOP.** Report every drafted spec. Generated specs stay `status: draft` until a human reviews each one and promotes it: to `todo` if not correctly implemented yet, or to `done` via `/specz:reconcile` if the code already satisfies it. Do not promote anything yourself.

## Failure behavior
- Cannot determine the instructions file → default to `CLAUDE.md` at repo root.
- Existing `specz/` content is updated only with explicit user consent.
