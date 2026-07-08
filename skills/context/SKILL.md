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
