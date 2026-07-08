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
(if empty because the work is already committed, use `git diff --name-only <base>..HEAD` over the task's commits) then collect the IDs on those files' `SPECZ:` lines and sidecars.

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
