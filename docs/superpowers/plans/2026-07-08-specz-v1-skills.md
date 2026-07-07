# specz v1 Skills Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Ship the seven pure-markdown specz skills as a Claude Code plugin, verified against a committed fixture project.

**Architecture:** Prompt-only skills (no scripts, no hooks — ADR-0011) packaged as a plugin (`.claude-plugin/` manifests + `skills/*/SKILL.md`). Each SKILL.md is tailored self-contained: it inlines exactly the format rules it needs, citing ADRs (ADR-0014). Verification is behavioral: per flow, a subagent gets only the skill text plus a temp copy of `tests/fixture/webapp/` and its output is checked against pass conditions.

**Tech Stack:** Markdown, YAML/JSON manifests, `rg`/`awk`/`shasum` command pipelines (BSD/macOS-compatible). No runtime dependencies.

**Spec:** `docs/superpowers/specs/2026-07-08-specz-skills-design.md`

---

## Pinned definitions (normative — copy verbatim wherever a task says so)

**PIN-1 — ID grammar (ADR-0002):** `spz-[a-z0-9]{2,5}-[a-z0-9]{2}` (segment 2–5 chars from the registry; suffix 2 random chars).

**PIN-2 — Mapping line, canonical form (ADR-0009):** `<comment-leader> SPECZ: <id>[, <id>]*` — uppercase `SPECZ:`, one space after the colon, lowercase IDs separated by comma-space. Checker accepts flexible whitespace: `SPECZ:\s*spz-`.

**PIN-3 — Body hash (ADR-0004):** first 8 hex chars of SHA-256 over the body (content after the closing `---` of frontmatter, leading/trailing blank lines stripped):

```bash
awk '
  /^---$/ { if (fm < 2) { fm++; next } }
  fm == 2 {
    if ($0 ~ /^[[:space:]]*$/) { if (started) pend = pend $0 "\n" }
    else { printf "%s%s\n", pend, $0; pend = ""; started = 1 }
  }
' "<spec-file>" | shasum -a 256 | cut -c1-8
```

**PIN-4 — Index block (ADR-0006):** everything between `<!-- specz:index:begin -->` and `<!-- specz:index:end -->` in `specz/SPECS.md`. Regeneration rebuilds a table `| id | title | status | path |` from every spec file's frontmatter + H1, path relative to `specz/`, **rows sorted lexicographically by id**. Nothing outside the fence is touched.

**PIN-5 — Rules block** (what `init` writes into agent instructions):

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

**PIN-6 — Spec file template (ADR-0007):**

```markdown
---
id: <spz-...>
type: functional | non-functional
status: draft | todo | done | archived
---
# <Title>

## Description
<intent and context; [[spz-...]] references woven into prose>

## Acceptance Criteria
- [ ] <individually verifiable statement>
- [ ] <individually verifiable statement>
```

(`synced: <8-hex>` appears in frontmatter only on `done` specs, written only by reconcile.)

---

### Task 1: Plugin manifests

**Files:**
- Create: `.claude-plugin/plugin.json`
- Create: `.claude-plugin/marketplace.json`

- [ ] **Step 1: Write plugin.json**

```json
{
  "name": "specz",
  "description": "Spec traceability layer: capture requirements into specz format, map code to specs, and keep them reconciled. Wraps around whichever framework does the thinking.",
  "version": "0.1.0",
  "author": {
    "name": "Elnur Jabarov"
  }
}
```

- [ ] **Step 2: Write marketplace.json**

```json
{
  "name": "specz-marketplace",
  "owner": {
    "name": "Elnur Jabarov"
  },
  "plugins": [
    {
      "name": "specz",
      "source": "./",
      "description": "Spec traceability layer: capture, map, reconcile, check, audit."
    }
  ]
}
```

- [ ] **Step 3: Verify both parse as JSON**

Run: `python3 -m json.tool .claude-plugin/plugin.json && python3 -m json.tool .claude-plugin/marketplace.json`
Expected: both echoed back, exit 0.

- [ ] **Step 4: Commit**

```bash
git add .claude-plugin && git commit -m "Add plugin and marketplace manifests"
```

---

### Task 2: ADR-0013 and ADR-0014

**Files:**
- Create: `docs/adr/0013-plugin-distribution.md`
- Create: `docs/adr/0014-self-contained-skills.md`

- [ ] **Step 1: Write ADR-0013**

```markdown
# ADR-0013: Distribution as a Claude Code Plugin

- Status: Accepted
- Date: 2026-07-08
- Concretizes: ADR-0011 (pure-markdown skills; this pins the install shape)

## Context

ADR-0011 decided specz ships as markdown skills only, but left the concrete
repo layout and install story open. Candidates: a bare folder of markdown
files users copy by hand, a Claude Code plugin, or both documented in
parallel.

## Decision

**Claude Code plugin layout**: `.claude-plugin/plugin.json` (plugin name
`specz`) plus a single-entry `.claude-plugin/marketplace.json`, with skills
at `skills/<name>/SKILL.md`.

- Install: `/plugin marketplace add <this repo>` then install `specz`;
  skills invoke as `/specz:<name>` — matching the naming ADR-0010 already
  uses.
- Still pure markdown: the manifests are metadata only; no scripts, hooks,
  or runtime dependencies enter the package (ADR-0011 holds).

Rejected:

- **Bare skills folder**: zero platform-specific files, but no namespaced
  commands (drifts from ADR-0010 naming), manual per-project install, no
  marketplace story.
- **Plugin + documented copy path**: covers other-agent users, but two
  install paths to keep in sync; the copy path stays possible regardless
  (the skills are plain markdown) and can be documented when someone needs
  it.

## Consequences

- Claude Code users get one-command install and the `/specz:` namespace.
- Two small JSON manifests are Claude-Code-specific; other agents ignore
  them and can consume `skills/*/SKILL.md` directly.
- Versioning rides `plugin.json`'s `version` field.
```

- [ ] **Step 2: Write ADR-0014**

```markdown
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
```

- [ ] **Step 3: Commit**

```bash
git add docs/adr/0013-plugin-distribution.md docs/adr/0014-self-contained-skills.md
git commit -m "Add ADR-0013 (plugin distribution) and ADR-0014 (self-contained skills)"
```

---

### Task 3: Fixture project

A fake webapp in the *already-initialized* state (specz adopted, some specs done, one seeded semantic lie for audit). Raw-state variants for the init test are derived at test time by deletion.

**Files:**
- Create: `tests/fixture/webapp/src/auth.py`
- Create: `tests/fixture/webapp/src/render.js`
- Create: `tests/fixture/webapp/package.json`
- Create: `tests/fixture/webapp/package.json.specz`
- Create: `tests/fixture/webapp/plan.md`
- Create: `tests/fixture/webapp/CLAUDE.md`
- Create: `tests/fixture/webapp/specz/config.yaml`
- Create: `tests/fixture/webapp/specz/SPECS.md`
- Create: `tests/fixture/webapp/specz/auth/spz-auth-bz.md`
- Create: `tests/fixture/webapp/specz/sec/spz-sec-k9.md`
- Create: `tests/fixture/webapp/specz/ui/spz-ui-k2.md`
- Create: `tests/fixture/webapp/specz/infra/spz-infra-bb.md`

- [ ] **Step 1: Write the source files**

`src/auth.py` — note `MAX_FAILURES = 3` is the deliberate audit target (spec says 5). Do NOT add a comment saying so:

```python
# SPECZ: spz-auth-bz

MAX_FAILURES = 3
LOCK_MINUTES = 15


def login(user, password):
    """Authenticate a user with email and password."""
    if verify(user, password):
        user.failures = 0
        return issue_session(user)
    record_failure(user)
    return None


# SPECZ: spz-auth-bz, spz-sec-k9
def record_failure(user):
    user.failures += 1
    if user.failures >= MAX_FAILURES:
        lock_account(user, minutes=LOCK_MINUTES)
```

`src/render.js`:

```javascript
// SPECZ: spz-ui-k2

function renderLoginForm() {
  return `
    <form method="post" action="/api/login">
      <input type="email" name="email" required>
      <input type="password" name="password" required>
      <button type="submit">Log in</button>
    </form>`;
}

module.exports = { renderLoginForm };
```

`package.json`:

```json
{
  "name": "webapp",
  "version": "1.0.0",
  "dependencies": {
    "express": "^4.18.0"
  }
}
```

`package.json.specz`:

```
spz-infra-bb
```

- [ ] **Step 2: Write plan.md (capture input) and CLAUDE.md**

`plan.md`:

```markdown
# Sprint plan: account recovery & abuse protection

## Password reset
Users can request a password-reset email. The reset link contains a
single-use token that expires after 30 minutes.

## Login rate limiting
To slow credential stuffing, an IP may make at most 10 login attempts
per minute; further attempts get HTTP 429.
```

`CLAUDE.md`: exactly PIN-5 (the rules block), nothing else.

- [ ] **Step 3: Write specz/config.yaml and specz/SPECS.md**

`specz/config.yaml`:

```yaml
# specz configuration (ADR-0002 segment registry, ADR-0012 scope)
segments:
  auth: authentication, sessions, identity
  sec: security hardening, abuse protection
  ui: user interface, presentation
  infra: build, dependencies, environments
ignore:
  - "*.md"
  - "*.specz"
  - "specz/**"
  - "node_modules/**"
  - "*.lock"
```

`specz/SPECS.md`:

```markdown
# webapp Specs

A demo web application: email+password login with abuse protection.

## Domains

- auth: login and sessions
- sec: lockout and rate limiting
- ui: forms and rendering
- infra: dependencies

## Conventions

None yet.

<!-- specz:index:begin -->
| id | title | status | path |
|----|-------|--------|------|
| spz-auth-bz | Login with email+password | done | auth/spz-auth-bz.md |
| spz-infra-bb | Web framework dependency | done | infra/spz-infra-bb.md |
| spz-sec-k9 | Account lockout policy | todo | sec/spz-sec-k9.md |
| spz-ui-k2 | Login form | todo | ui/spz-ui-k2.md |
<!-- specz:index:end -->
```

- [ ] **Step 4: Write the four spec files**

`specz/auth/spz-auth-bz.md` (write `synced: 00000000` for now; Step 5 fixes it):

```markdown
---
id: spz-auth-bz
type: functional
status: done
synced: 00000000
---
# Login with email+password

## Description
Users authenticate with email and password. Repeated failures trigger the
lockout policy defined in [[spz-sec-k9]].

## Acceptance Criteria
- [x] valid credentials → session issued
- [x] 5 consecutive failures → account locked for 15 minutes
- [x] a successful login resets the failure counter
```

`specz/sec/spz-sec-k9.md`:

```markdown
---
id: spz-sec-k9
type: non-functional
status: todo
---
# Account lockout policy

## Description
Brute-force protection for authentication endpoints; enforced by the login
flow ([[spz-auth-bz]]).

## Acceptance Criteria
- [ ] 5 consecutive failures locks the account
- [ ] a lock expires after 15 minutes
```

`specz/ui/spz-ui-k2.md`:

```markdown
---
id: spz-ui-k2
type: functional
status: todo
---
# Login form

## Description
The login page renders a form for the credentials flow ([[spz-auth-bz]]).

## Acceptance Criteria
- [ ] form includes an email field and a password field
- [ ] submitting posts credentials to /api/login
```

`specz/infra/spz-infra-bb.md` (write `synced: 00000000`; Step 5 fixes it):

```markdown
---
id: spz-infra-bb
type: non-functional
status: done
synced: 00000000
---
# Web framework dependency

## Description
The app is served with Express.

## Acceptance Criteria
- [x] express is declared as a dependency at major version 4
```

- [ ] **Step 5: Compute real synced hashes**

For each of the two `done` specs, run PIN-3 with `<spec-file>` set to the file path, and replace `00000000` in that file's frontmatter with the 8-char output. Note: the hash covers only the body (after frontmatter), so editing the frontmatter does not change it — no recompute loop.

- [ ] **Step 6: Verify fixture self-consistency**

```bash
F=tests/fixture/webapp
# every referenced id has a spec file (expect 4 files, no output from the loop)
for id in spz-auth-bz spz-sec-k9 spz-ui-k2 spz-infra-bb; do
  ls $F/specz/*/$id.md >/dev/null || echo "MISSING $id"
done
# recomputed hashes match synced (expect two lines of OK)
for f in $F/specz/auth/spz-auth-bz.md $F/specz/infra/spz-infra-bb.md; do
  h=$(awk '/^---$/{if(fm<2){fm++;next}} fm==2{if($0~/^[[:space:]]*$/){if(started)pend=pend $0 "\n"}else{printf "%s%s\n",pend,$0;pend="";started=1}}' "$f" | shasum -a 256 | cut -c1-8)
  grep -q "synced: $h" "$f" && echo "OK $f" || echo "HASH MISMATCH $f"
done
```

Expected: no `MISSING`, two `OK` lines.

- [ ] **Step 7: Commit**

```bash
git add tests/fixture && git commit -m "Add fixture webapp for skill verification"
```

---

### Task 4: skills/capture/SKILL.md

**Files:**
- Create: `skills/capture/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Verify frontmatter and pinned content**

Run: `head -5 skills/capture/SKILL.md`
Expected: frontmatter with `name: capture` and a `description:` starting "Use after".
Run: `rg -c "spz-<segment>-<suffix>" skills/capture/SKILL.md`
Expected: ≥ 1.

- [ ] **Step 3: Commit**

```bash
git add skills/capture && git commit -m "Add capture skill"
```

---

### Task 5: skills/map/SKILL.md

**Files:**
- Create: `skills/map/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
---
name: map
description: Use while or after writing code in a specz project — maintains SPECZ: mapping lines and .specz sidecars so code stays traceable to specs, using the file-default + override rule.
---

# specz map — Maintain code↔spec mappings

**Announce:** "Using specz:map to maintain spec mappings."

## When NOT to use
- No `specz/` directory → stop and tell the user to run `/specz:init`.
- The code implements a requirement no spec covers → tell the user; new requirements go through `/specz:capture`. **Never invent an ID.**

## The two-level rule (ADR-0012)

1. **File default (mandatory).** Every in-scope source file carries a whole-file mapping:
   - Commentable file → a `SPECZ:` line at the top (after shebang/license header if present).
   - Uncommentable file (JSON, CSV, lockfile-like) → a sidecar named `<filename>.specz` in the same directory (ADR-0008). Sidecar content: one spec ID per line, nothing else:

     ```
     spz-infra-bb
     spz-sec-k9
     ```

2. **Inner override (exceptional).** A function/class/snippet gets its own `SPECZ:` line directly above it ONLY when its spec set is narrower, extra, or different from the file default. An override states the unit's **complete** set — it replaces the default, never extends it. Un-annotated units inherit the file default.

**Decision test** before annotating a unit: *does this unit serve a different set of specs than the file default?* No → no annotation. Cross-cutting NFRs (perf, security) map once at file level, never per function.

**In scope** = source files not matching the `ignore:` globs in `specz/config.yaml`.

## Canonical form (ADR-0009)

`<comment-leader> SPECZ: <id>[, <id>]*` — uppercase `SPECZ:` with colon, one space after the colon, lowercase IDs separated by comma-space, using the file's native comment syntax:

```python
# SPECZ: spz-auth-bz, spz-perf-c1
```
```javascript
// SPECZ: spz-ui-k2
```
```html
<!-- SPECZ: spz-docs-aa -->
```

Always write exactly this form. A bare ID in a comment without the `SPECZ:` marker is a *mention*, not a mapping — tooling ignores it.

## Workflow

For each file you created or edited:

1. **In scope?** Skip files matching `ignore:` globs.
2. **New file** → add the file-default line (or sidecar) listing the spec IDs it serves. Get the IDs from the task's `/specz:context` slice or the SPECS.md index — never from memory.
3. **Edited file** → does the file default still hold? Did an edited unit's spec set diverge from the default (add an override) or converge back (remove it)?
4. **Renamed file** → rename its sidecar with it (`old.json.specz` left behind is a structural error).
5. **Validate every ID you write:** it must resolve to a spec file (`rg --files specz/ -g "<id>.md"`) whose status is not `archived`.
````

- [ ] **Step 2: Verify the canonical example matches PIN-2**

Run: `rg -n "SPECZ: spz-auth-bz, spz-perf-c1" skills/map/SKILL.md`
Expected: 1 hit.

- [ ] **Step 3: Commit**

```bash
git add skills/map && git commit -m "Add map skill"
```

---

### Task 6: skills/context/SKILL.md

**Files:**
- Create: `skills/context/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
---
name: context
description: Use when starting work on a spec ID, or when asked what code serves a requirement — loads the spec, its 1-hop [[references]], and all mapped code paths as a compact slice. Read-only.
---

# specz context — Load the precise slice for an ID

**Announce:** "Using specz:context to load the slice for <id>."

Read-only: change no files. Load the precise slice, not "everything that might be related".

## Workflow (per requested ID)

### 1. Resolve the spec
By search, never by path construction (specs move freely — ADR-0005):
```bash
rg --files specz/ -g "<id>.md"
```
No hit → report "unknown ID <id>" and stop for that ID. Do not guess.

### 2. Load the 1-hop neighborhood (ADR-0003)
Read the spec. Collect every `[[spz-...]]` reference in its body; resolve and read each referenced spec. One hop only, unless the user explicitly asks for transitive.

### 3. Find mapped code
The uppercase `SPECZ:` marker distinguishes a mapping *declaration* from a prose *mention* (ADR-0009) — only marker lines count.
```bash
# inline mappings (code files)
rg -n "SPECZ:.*<id>" --glob '!specz/**'
# sidecar mappings; each sidecar maps its target file = its own path minus .specz
rg -l "^<id>$" -g '*.specz'
```
Classify inline hits: a hit at the top of a file is the *file default* (whole file serves the spec); a hit directly above a function/class is an *override* (that unit's complete spec set — ADR-0012).

### 4. Output the slice
- The requested spec's body, verbatim.
- Neighbors: `id — title — status`, one line each (not full bodies).
- Mapped code: file paths; for overrides, `file:line` plus the unit name.
- The spec's `status`. If `done`, note that current sync state is only known by running `/specz:check`.

Nothing else — no unrelated specs, no speculative file reads.
````

- [ ] **Step 2: Verify read-only language present**

Run: `rg -c "Read-only" skills/context/SKILL.md`
Expected: ≥ 1.

- [ ] **Step 3: Commit**

```bash
git add skills/context && git commit -m "Add context skill"
```

---

### Task 7: skills/check/SKILL.md

**Files:**
- Create: `skills/check/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
---
name: check
description: Use to verify specz structural consistency (CI-style, deterministic, no LLM judgment) — dangling IDs, unregistered segments, orphan sidecars, stale index, hash drift, missing mappings. Read-only.
---

# specz check — Deterministic structural verification

**Announce:** "Using specz:check to run structural verification."

Read-only. Run the pipeline below exactly; the commands are the contract (they can be pasted into CI — ADR-0011). Report findings; repair is `/specz:reconcile`'s job. No `specz/` directory → stop and tell the user to run `/specz:init`.

## Setup

```bash
cd "$(git rev-parse --show-toplevel)"
```
Build three lists used throughout:
- **SPEC_FILES**: `rg --files specz/ -g 'spz-*.md'`
- **KNOWN_IDS**: the basenames of SPEC_FILES minus `.md`.
- **ARCHIVED_IDS**: `rg -l "^status: archived" specz/ -g 'spz-*.md'` → basenames minus `.md`.
- **SEGMENTS**: keys under `segments:` in `specz/config.yaml`.
- **IN_SCOPE**: all repo files (`git ls-files --cached --others --exclude-standard` — includes untracked) minus `specz/**` minus the `ignore:` globs from `specz/config.yaml`.

## Checks

Run every check; collect findings as you go.

**C1 — Dangling IDs (error).** Every referenced ID must be in KNOWN_IDS. Referenced IDs come from three sources:
```bash
# a) inline mapping lines (extract only ID-shaped tokens; malformed tokens are C2's job)
rg -oN --no-filename "SPECZ:.*" --glob '!specz/**' | rg -o "spz-[a-z0-9]+-[a-z0-9]+" | sort -u
# b) spec-to-spec references
rg -oN --no-filename "\[\[(spz-[a-z0-9]+-[a-z0-9]+)\]\]" -r '$1' specz/ | sort -u
# c) sidecars
rg -oN --no-filename "^spz-[a-z0-9]+-[a-z0-9]+$" -g '*.specz' . | sort -u
```

**C2 — Grammar and segment (error).** Every ID (referenced or in KNOWN_IDS) must match `spz-[a-z0-9]{2,5}-[a-z0-9]{2}` and its segment (the middle part) must be in SEGMENTS (ADR-0002). Additionally, any `SPECZ:` line in an in-scope file whose payload contains tokens that are not valid IDs (check the raw lines from `rg -n "SPECZ:" --glob '!specz/**'`) is an error.

**C3 — Orphan sidecars (error).** For every `*.specz` file, the target (its own path minus the `.specz` suffix) must exist:
```bash
for s in $(rg --files -g '*.specz'); do [ -f "${s%.specz}" ] || echo "ORPHAN $s"; done
```

**C4 — Stale index (error).** Regenerate the expected index in memory (ADR-0006): a row `| id | title | status | path |` per spec file (title = its H1 text, path relative to `specz/`), rows sorted lexicographically by id. Compare with the actual content between `<!-- specz:index:begin -->` and `<!-- specz:index:end -->` in `specz/SPECS.md`. Any difference (including hand-edits) → stale.

**C5 — Missing required sections (error).** (ADR-0007)
```bash
rg --files-without-match "^## Description" specz/ -g 'spz-*.md'
rg --files-without-match "^## Acceptance Criteria" specz/ -g 'spz-*.md'
```

**C6 — Status/frontmatter validity (error).** Every spec's `status:` is one of `draft|todo|done|archived`; every `done` spec has `synced:`; no non-`done` spec has `synced:` (ADR-0004).

**C7 — Changed specs (error).** For every `done` spec, recompute the body hash and compare to `synced:`; mismatch → report as **changed** (spec edited since last reconciliation — code possibly stale):
```bash
awk '
  /^---$/ { if (fm < 2) { fm++; next } }
  fm == 2 {
    if ($0 ~ /^[[:space:]]*$/) { if (started) pend = pend $0 "\n" }
    else { printf "%s%s\n", pend, $0; pend = ""; started = 1 }
  }
' "<spec-file>" | shasum -a 256 | cut -c1-8
```

**C8 — References to archived specs (error).** Any ID from C1's sources that is in ARCHIVED_IDS (archived specs' mapped code is dead by definition — ADR-0004).

**C9 — Unmapped files (error).** Every IN_SCOPE file must have a file-level mapping: either a `SPECZ:` line in the file or a `<file>.specz` sidecar (ADR-0012):
```bash
for f in <IN_SCOPE>; do
  rg -q "SPECZ:" "$f" || [ -f "$f.specz" ] || echo "UNMAPPED $f"
done
```

**C10 — Folder/segment mismatch (warning).** A spec whose first directory under `specz/` differs from its ID's segment (ADR-0005 — convention, never blocks).

## Report

```markdown
| check | finding | where |
|-------|---------|-------|
| C1 dangling id | spz-ui-zz | src/render.js:3 |
...
**check: N errors, M warnings — FAIL** (or: 0 errors, M warnings — PASS)
```
Errors fail; warnings never do. Suggest `/specz:reconcile` for repairs.
````

- [ ] **Step 2: Verify the hash pipeline is byte-identical to PIN-3**

Extract the awk pipeline from this SKILL.md and from the plan's PIN-3; diff them. Quick proxy:
Run: `rg -c 'pend = pend \$0 "\\\\n"' skills/check/SKILL.md` — expect 1; and visually confirm the block matches PIN-3 line-for-line.

- [ ] **Step 3: Commit**

```bash
git add skills/check && git commit -m "Add check skill"
```

---

### Task 8: skills/reconcile/SKILL.md

**Files:**
- Create: `skills/reconcile/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
---
name: reconcile
description: Use when a task is complete or to repair drift found by check/audit — verifies acceptance criteria against mapped code, flips todo→done, and writes the synced hash. The only writer of synced.
---

# specz reconcile — Verify, flip, anchor

**Announce:** "Using specz:reconcile to verify and update spec status."

Only this skill writes `synced`. **Re-anchoring without re-verifying every acceptance criterion is forbidden.** No `specz/` directory → stop and tell the user to run `/specz:init`.

## Inputs
Spec ID(s). If invoked as "the task is finished" with no IDs: infer them —
```bash
git diff --name-only HEAD
```
then collect the IDs on those files' `SPECZ:` lines and sidecars.

## Workflow (per spec; create a todo per step)

### 1. Load spec + mapped code
Resolve the spec (`rg --files specz/ -g "<id>.md"`), then find its code: `rg -n "SPECZ:.*<id>" --glob '!specz/**'` and `rg -l "^<id>$" -g '*.specz'`.

### 2. Verify each acceptance criterion
Against the actual code — read the implementation (and run the project's tests if it has them). Numbers, units, and limits must match exactly. Tick `- [x]` only with concrete evidence; cite the evidence (file:line or test name) in your report — evidence stays out of the spec file.

### 3. Apply the outcome
- **All ACs verified, status `todo`** → set `status: done`; compute the body hash (below) **after** all edits to the file (ticked boxes change the hash); add `synced: <hash>` to frontmatter.
- **Any AC unverifiable or unmet** → leave status and that box unchanged; report the gap. Never flip on partial verification.
- **Status `done` but drifted** (check reported *changed*): re-verify all ACs against current code. Still satisfied → recompute and rewrite `synced` (re-anchor). Not satisfied → report; fix code/mappings first, or with the user's consent flip back to `todo` and delete `synced`.
- **Requirement retired** → with the user's consent set `status: archived` and delete `synced`. Mapped code is dead by definition (ADR-0004): flag it for removal, and remove the ID from all `SPECZ:` lines and sidecars.

### 4. Regenerate the index if frontmatter changed (ADR-0006)
Rebuild the table between `<!-- specz:index:begin -->` and `<!-- specz:index:end -->` in `specz/SPECS.md` from every spec's frontmatter + H1: columns `| id | title | status | path |`, path relative to `specz/`, rows sorted lexicographically by id. Touch nothing outside the fence.

### 5. Run /specz:check
Finish by running the check pipeline and reporting its result alongside yours.

## Body hash (ADR-0004 — normative; identical pipeline in check)

First 8 hex chars of SHA-256 over the body: content after the closing `---` of frontmatter, leading and trailing blank lines stripped.

```bash
awk '
  /^---$/ { if (fm < 2) { fm++; next } }
  fm == 2 {
    if ($0 ~ /^[[:space:]]*$/) { if (started) pend = pend $0 "\n" }
    else { printf "%s%s\n", pend, $0; pend = ""; started = 1 }
  }
' "<spec-file>" | shasum -a 256 | cut -c1-8
```
````

- [ ] **Step 2: Verify hash pipelines are identical in reconcile and check**

```bash
diff <(sed -n '/^awk /,/cut -c1-8$/p' skills/reconcile/SKILL.md) \
     <(sed -n '/^awk /,/cut -c1-8$/p' skills/check/SKILL.md)
```
Expected: no output (identical).

- [ ] **Step 3: Commit**

```bash
git add skills/reconcile && git commit -m "Add reconcile skill"
```

---

### Task 9: skills/audit/SKILL.md

**Files:**
- Create: `skills/audit/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
---
name: audit
description: Use for deliberate semantic review of a specz project — judges whether mapped code truly satisfies acceptance criteria, flags weak criteria and suspicious overrides, and triages unmapped or dead code. Read-only.
---

# specz audit — Semantic verification

**Announce:** "Using specz:audit for semantic review of <scope>."

`check` asks *is the structure consistent?* — audit asks *is it true?* Run `/specz:check` first; structural errors make semantic review unreliable. Read-only: findings route to other skills, audit changes nothing.

## Scope
Confirm with the user: a segment, a folder, specific IDs, or all `done` specs. For more than ~10 specs, dispatch parallel subagents (one per segment or spec cluster), each returning findings in the report format below.

## Per-spec review

1. Load the spec and its mapped code (`rg -n "SPECZ:.*<id>" --glob '!specz/**'`; sidecars via `rg -l "^<id>$" -g '*.specz'`).
2. **Per acceptance criterion: does the code actually implement it?** Read the implementation, not comments or function names. Numbers, units, thresholds, and conditions must match exactly — a spec saying "5 failures" implemented as `MAX_FAILURES = 3` is a finding, whatever the checkbox claims.
3. **AC quality (ADR-0007):** a criterion that is vague, boilerplate, or not independently verifiable ("works correctly", "is fast") is a finding.
4. **Override plausibility (ADR-0012):** an inner `SPECZ:` line whose spec set doesn't match what the unit does (override correctness is semantic — check can't see it) is a finding.

## Unmapped-code sweep

1. Recently-touched in-scope files:
```bash
git log --since="30 days ago" --name-only --pretty=format: | sort -u
```
2. For each (skipping `ignore:` globs from `specz/config.yaml`): compare its mapped spec IDs against what the code now does.
   - Behavior with no covering spec → **new code needing capture**.
   - Code serving only archived specs, or clearly unused → **dead-code candidate**.

## Report (read-only)

```markdown
| spec | AC / unit | finding | severity | route |
|------|-----------|---------|----------|-------|
| spz-auth-bz | AC 2 | spec says 5 failures; auth.py uses MAX_FAILURES = 3 | high | /specz:reconcile |
```
Routes: unmet AC or drift → `/specz:reconcile`; missing requirement → `/specz:capture`; dead code → human decision. Do not fix anything yourself.
````

- [ ] **Step 2: Verify read-only language present**

Run: `rg -c "Read-only|read-only" skills/audit/SKILL.md`
Expected: ≥ 2.

- [ ] **Step 3: Commit**

```bash
git add skills/audit && git commit -m "Add audit skill"
```

---

### Task 10: skills/init/SKILL.md

**Files:**
- Create: `skills/init/SKILL.md`

- [ ] **Step 1: Write the file**

````markdown
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
````

- [ ] **Step 2: Verify the rules block is byte-identical to PIN-5 / fixture CLAUDE.md**

```bash
diff <(sed -n '/<!-- specz:rules:begin -->/,/<!-- specz:rules:end -->/p' skills/init/SKILL.md) \
     <(sed -n '/<!-- specz:rules:begin -->/,/<!-- specz:rules:end -->/p' tests/fixture/webapp/CLAUDE.md)
```
Expected: no output.

- [ ] **Step 3: Commit**

```bash
git add skills/init && git commit -m "Add init skill"
```

---

### Task 11: Cross-skill consistency check

**Files:** none (verification only)

- [ ] **Step 1: Duplicated definitions are identical**

```bash
# hash pipeline: reconcile == check (already checked in Task 8; re-run)
diff <(sed -n '/^awk /,/cut -c1-8$/p' skills/reconcile/SKILL.md) \
     <(sed -n '/^awk /,/cut -c1-8$/p' skills/check/SKILL.md)
# ID regex appears with the same body everywhere it is written
rg -n "spz-\[a-z0-9\]\{2,5\}-\[a-z0-9\]\{2\}" skills/
# index columns identical wherever stated
rg -n "\| id \| title \| status \| path \|" skills/ | wc -l
```
Expected: empty diff; the ID regex hits use identical text; index header appears in capture, check, reconcile, init (4+ hits).

- [ ] **Step 2: Every skill has frontmatter with name + "Use when/after/while/for" description**

```bash
for f in skills/*/SKILL.md; do head -4 "$f" | rg -q "^description: Use " && echo "OK $f" || echo "BAD $f"; done
```
Expected: 7 × OK.

- [ ] **Step 3: Fix any mismatch found, commit**

```bash
git add -A && git commit -m "Align duplicated definitions across skills" # only if changes were needed
```

---

## Fixture verification (Tasks 12–18)

Common setup for every verification task — copy the fixture to a temp git repo:

```bash
T=$(mktemp -d); cp -R tests/fixture/webapp/ "$T"; git -C "$T" init -q; git -C "$T" add -A; git -C "$T" -c user.email=t@t -c user.name=t commit -qm fixture; echo "$T"
```

Dispatch pattern (all tasks): run a **general-purpose subagent** whose prompt contains (a) the absolute path of the one skill file to read, (b) the temp dir as working directory, (c) the user-style request, (d) "Follow the skill exactly. Report what you did." The subagent must NOT be given the spec, the plan, or other skills — except where a task says otherwise. Evaluate pass conditions yourself afterward by inspecting the temp dir. **On failure: diagnose which skill wording caused it, fix the SKILL.md, commit the fix, and re-run this task with a fresh temp copy.**

### Task 12: Verify init (brownfield)

- [ ] **Step 1: Derive the raw (pre-specz) variant in the temp copy**

```bash
rm -rf "$T/specz" "$T/CLAUDE.md" "$T/package.json.specz"
sed -i '' '/SPECZ:/d' "$T"/src/*
```

- [ ] **Step 2: Dispatch** — request: "Adopt specz in this project." Skill: `skills/init/SKILL.md`.

- [ ] **Step 3: Evaluate pass conditions**

- `$T/specz/config.yaml` exists with `segments:` (each with a description) and `ignore:` lists.
- `$T/specz/SPECS.md` exists: narrative + index fence, index rows sorted by id and matching the drafted specs.
- `$T/CLAUDE.md` contains the rules block byte-identical to PIN-5 (diff against `tests/fixture/webapp/CLAUDE.md`).
- Drafted specs: every file matches `spz-[a-z0-9]{2,5}-[a-z0-9]{2}.md`, has `status: draft`, no `synced:`, both required sections.
- Source files re-annotated: `rg -c "SPECZ:" $T/src/auth.py $T/src/render.js` ≥ 1 each; `package.json` has a sidecar or the report explains why not.
- The subagent's report STOPPED at the review gate (no spec promoted past `draft`).

- [ ] **Step 4: Pass → mark done. Fail → fix skill wording, commit, re-run.**

### Task 13: Verify capture

- [ ] **Step 1: Fresh temp copy (initialized state, as committed).**
- [ ] **Step 2: Dispatch** — request: "Capture the requirements in plan.md into specz." Skill: `skills/capture/SKILL.md`.
- [ ] **Step 3: Evaluate pass conditions**

- ≥ 2 new spec files (password reset; rate limiting), each: valid ID with a **registered** segment, `status: todo`, no `synced:`, both required sections, ACs carrying the concrete numbers (30 minutes; 10/minute; HTTP 429).
- No existing spec file modified; `plan.md` unmodified (`git -C "$T" diff --name-only` shows only new files + SPECS.md).
- Index regenerated: new rows present, all rows sorted by id, nothing outside the fence changed.

- [ ] **Step 4: Pass/fail handling as in Task 12.**

### Task 14: Verify map

- [ ] **Step 1: Fresh temp copy; seed two unannotated files**

`$T/src/session.py`:
```python
def start_session(user):
    return {"user": user.id, "ttl": 3600}
```
`$T/settings.json`:
```json
{ "lockMinutes": 15 }
```

- [ ] **Step 2: Dispatch** — request: "I just wrote src/session.py and settings.json; both serve spz-sec-k9. Apply specz mapping." Skill: `skills/map/SKILL.md`.
- [ ] **Step 3: Evaluate pass conditions**

- `src/session.py` line 1 is exactly `# SPECZ: spz-sec-k9`; **no** per-function annotation added (set doesn't differ).
- `settings.json` untouched; `settings.json.specz` created containing exactly `spz-sec-k9`.
- No other file modified.

- [ ] **Step 4: Pass/fail handling as in Task 12.**

### Task 15: Verify check

- [ ] **Step 1: Fresh temp copy; seed exactly five findings**

```bash
printf '\n// SPECZ: spz-ui-zz\nfunction x() {}\n' >> "$T/src/render.js"   # C1 dangling (+C2 if segment unregistered — ui is registered, so C1 only)
printf 'spz-infra-bb\n' > "$T/src/old.json.specz"                          # C3 orphan
printf 'def helper():\n    return 1\n' > "$T/src/util.py"                  # C9 unmapped
sed -i '' 's/Users authenticate/People authenticate/' "$T/specz/auth/spz-auth-bz.md"  # C7 changed
sed -i '' 's/| spz-ui-k2 | Login form | todo |/| spz-ui-k2 | Login form | done |/' "$T/specz/SPECS.md"  # C4 stale index
```

- [ ] **Step 2: Dispatch** — request: "Run the specz structural check on this repo." Skill: `skills/check/SKILL.md`.
- [ ] **Step 3: Evaluate pass conditions**

- Report contains ALL five seeded findings: C1 `spz-ui-zz`; C3 `src/old.json.specz`; C4 stale index; C7 `spz-auth-bz` changed; C9 `src/util.py`.
- No false positives on the unseeded remainder (in particular: `spz-infra-bb` hash OK, `package.json` mapped via sidecar, C10 clean).
- Verdict is FAIL with an error count of 5; repo left unmodified (`git -C "$T" status --porcelain` shows only the seeds).

- [ ] **Step 4: Pass/fail handling as in Task 12.**

### Task 16: Verify reconcile

- [ ] **Step 1: Fresh temp copy.**
- [ ] **Step 2: Dispatch** — request: "I finished implementing spz-ui-k2 (the login form in src/render.js). Reconcile it." Skills: `skills/reconcile/SKILL.md` AND `skills/check/SKILL.md` (reconcile's step 5 invokes check).
- [ ] **Step 3: Evaluate pass conditions**

- `specz/ui/spz-ui-k2.md`: both ACs ticked `- [x]`, `status: done`, `synced:` present.
- Independently recompute the hash with PIN-3 on the final file → must equal the written `synced` value (this catches order bugs: hash must be computed after ticking).
- Index row for spz-ui-k2 now says `done`; row order still sorted by id; nothing outside the fence changed.
- Report cites evidence per AC and includes a check run result.

- [ ] **Step 4: Pass/fail handling as in Task 12.**

### Task 17: Verify context

- [ ] **Step 1: Fresh temp copy.**
- [ ] **Step 2: Dispatch** — request: "Load the specz context slice for spz-auth-bz." Skill: `skills/context/SKILL.md`.
- [ ] **Step 3: Evaluate pass conditions**

- Slice contains: full body of spz-auth-bz; neighbor line for spz-sec-k9 (id — title — status, not full body); `src/auth.py` as mapped code with the `record_failure` override called out (file:line).
- Slice does NOT contain spz-ui-k2, spz-infra-bb, render.js, or package.json.
- No file modified (`git -C "$T" status --porcelain` empty).

- [ ] **Step 4: Pass/fail handling as in Task 12.**

### Task 18: Verify audit

- [ ] **Step 1: Fresh temp copy.**
- [ ] **Step 2: Dispatch** — request: "Run a specz semantic audit of the auth segment." Skills: `skills/audit/SKILL.md` AND `skills/check/SKILL.md` (audit says run check first).
- [ ] **Step 3: Evaluate pass conditions**

- Findings include the seeded lie: spz-auth-bz AC 2 ("5 consecutive failures") vs `MAX_FAILURES = 3` in `src/auth.py`, routed to `/specz:reconcile`.
- No file modified.
- No fabricated findings about code that matches its spec (AC 1/3 of spz-auth-bz should not be flagged).

- [ ] **Step 4: Pass/fail handling as in Task 12.**

---

### Task 19: README and wrap-up

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Rewrite README.md**

```markdown
# specz — spec traceability AI framework

specz is a traceability layer that wraps around whichever dev framework does
the thinking (superpowers, gstack, or plain chat). It owns spec format,
mapping, and consistency — never brainstorming, planning, or implementation.

## Install (Claude Code)

    /plugin marketplace add <this repo url or path>
    /plugin install specz

Then in your project: `/specz:init`.

## Skills

| Skill | Stage | What it does |
|-------|-------|--------------|
| /specz:init | adoption | create specz/, install rules block; brownfield: draft specs gated on review |
| /specz:capture | capture | design/plan artifact → spec files with IDs and acceptance criteria |
| /specz:context | context | load a spec, its [[refs]], and mapped code for an ID |
| /specz:map | mapping | maintain SPECZ: lines and .specz sidecars while coding |
| /specz:reconcile | reconcile | verify ACs, flip todo→done, write the synced hash; repair drift |
| /specz:check | verify | deterministic structural checks (CI-friendly) |
| /specz:audit | verify | semantic review: does code satisfy the ACs? |

Decisions live in `docs/adr/`. The skill-verification fixture lives in
`tests/fixture/webapp/`.
```

- [ ] **Step 2: Final repo check**

```bash
ls skills/*/SKILL.md | wc -l    # expect 7
python3 -m json.tool .claude-plugin/plugin.json > /dev/null && echo OK
git status --porcelain           # expect only README.md staged-to-be
```

- [ ] **Step 3: Commit**

```bash
git add README.md && git commit -m "Document install and skill inventory"
```

---

## Done criteria

All 19 tasks checked; every fixture verification (12–18) passed on a clean run; duplicated definitions verified identical (Task 11); working tree clean.
