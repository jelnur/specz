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

Always write exactly this form. Every ID matches `spz-[a-z0-9]{2,5}-[a-z0-9]{2}` (ADR-0002). A bare ID in a comment without the `SPECZ:` marker is a *mention*, not a mapping — tooling ignores it.

## Workflow

For each file you created or edited:

1. **In scope?** Skip files matching `ignore:` globs.
2. **New file** → add the file-default line (or sidecar) listing the spec IDs it serves. Get the IDs from the task's `/specz:context` slice or the SPECS.md index — never from memory.
3. **Edited file** → does the file default still hold? Did an edited unit's spec set diverge from the default (add an override) or converge back (remove it)?
4. **Renamed file** → rename its sidecar with it (`old.json.specz` left behind is a structural error).
5. **Validate every ID you write:** it must resolve to a spec file (`rg --files specz/ -g "<id>.md"`) whose status is not `archived`.
