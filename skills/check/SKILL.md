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
