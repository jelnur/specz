---
name: capture
description: Use after producing a design or plan artifact, or when the user states requirements in prose — converts requirements into specz spec files (minted IDs, acceptance criteria) and regenerates the index.
---

# specz capture — Turn a design/plan into specs

**Announce:** "Using specz:capture to convert requirements into spec files."

## When to use
- A design doc, implementation plan, or prose request contains requirements not yet tracked in `specz/`.

## When NOT to use
- No `specz/` directory exists → stop and tell the user to run `/specz:init`.
- An existing requirement changed → edit its spec file directly, then run `/specz:reconcile`.

## Workflow

Create a todo per numbered step.

### 1. Extract requirements
Read the artifact. List discrete requirements: each must be independently verifiable; split "and"-joined statements into separate requirements. Ignore implementation detail that isn't a requirement.

### 2. Choose a segment (per requirement)
Segments are a controlled vocabulary in `specz/config.yaml` under `segments:` (ADR-0002). Pick the best fit. If none fits, propose adding one (2–5 lowercase alphanumerics + one-line description) and get the user's confirmation before editing `config.yaml`. **Never write an ID with an unregistered segment.**

### 3. Mint the ID (ADR-0002)
Format: `spz-<segment>-<suffix>`, suffix = two characters chosen at random from `a-z0-9` (non-sequential — do not increment).

Verify uniqueness (IDs are never reused, including archived specs):
```bash
rg -l "spz-<segment>-<suffix>" specz/
```
Any hit → mint a different suffix. IDs are immutable once written.

### 4. Write the spec file
Path: `specz/<segment>/<id>.md` (the segment folder is convention, not law — ADR-0005). Never overwrite an existing file. Template (ADR-0007):

```markdown
---
id: <the minted id>
type: functional | non-functional
status: todo
---
# <Title>

## Description
<intent and context>

## Acceptance Criteria
- [ ] <statement>
```

- The H1 is the title; there is no `title:` frontmatter.
- `type` describes the requirement kind; it never appears in the ID.
- New specs are `status: todo` (use `draft` only if the user says the design is not yet approved). No `synced:` field — only `/specz:reconcile` writes it.
- **Description:** intent and context. Reference related specs inline as `[[spz-...]]` (ADR-0003); verify each reference resolves: `rg --files specz/ -g "<id>.md"` must find it.
- **Acceptance Criteria:** unchecked `- [ ]` boxes; each criterion individually verifiable against code or behavior. Numbers, units, and limits belong in the criterion ("locks after 5 failures", not "handles failures correctly").

### 5. Regenerate the index (ADR-0006)
In `specz/SPECS.md`, rebuild the table between `<!-- specz:index:begin -->` and `<!-- specz:index:end -->` from every spec file's frontmatter + H1:

```
| id | title | status | path |
```
Path is relative to `specz/`; rows sorted lexicographically by id. Touch nothing outside the fence.

### 6. Report
Table of minted IDs (id, title, path). The source artifact stays untouched — the spec files are now the requirements of record.
