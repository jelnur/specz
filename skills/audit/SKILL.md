---
name: audit
description: Use for deliberate semantic review of a specz project — judges whether mapped code truly satisfies acceptance criteria, flags weak criteria and suspicious overrides, and triages unmapped or dead code. Read-only.
---

# specz audit — Semantic verification

**Announce:** "Using specz:audit for semantic review of <scope>."

`check` asks *is the structure consistent?* — audit asks *is it true?* Run `/specz:check` first; structural errors make semantic review unreliable. Read-only: findings route to other skills, audit changes nothing. No `specz/` directory → stop and tell the user to run `/specz:init`.

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
