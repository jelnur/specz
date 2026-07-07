# ADR-0001: Code↔Spec Mapping Mechanism

- Status: Accepted
- Date: 2026-07-07
- Amended by: ADR-0008 (sidecar naming `.specz` instead of `.smap`; v1 scope: files only, no folder/region mapping)

## Context

specz needs a bidirectional mapping between requirements and code that is
(a) cheap enough for agents to maintain as a side effect of normal work, and
(b) deterministic to check so rot is caught early. Three candidate designs:

1. Inline comments + full commented *clones* of uncommentable files (`.smap` clones)
2. Inline comments + *reference-only* `.smap` sidecar files
3. A single central manifest (`specz/map.yaml`), no inline comments

## Decision

Option 2: **inline comments + reference-only sidecars.**

- **Primary mechanism:** an inline `SPECZ:` comment line (using the file's
  native comment syntax) directly above the mapped function, class, or snippet,
  listing spec IDs comma-separated.
- **Secondary mechanism:** reference-only `.smap` sidecar files covering
  uncommentable files (e.g. `package.json`), whole folders, and partial-file
  regions (e.g. a CSV header). Sidecars contain only path/selector → spec-ID
  references — **never file content**.

Rejected:

- **Content clones** duplicate content, creating a second source of truth that
  desyncs on every content edit (every `npm install` would break the clone).
- **Central manifest** is invisible at the point of edit, fragile to renames,
  and concentrates merge conflicts in one file.

## Consequences

- Nothing needs re-syncing when file *content* changes; sidecars change only
  when *mappings* change.
- Mappings stay visible to agents and humans exactly where code is read or
  edited, and remain greppable with plain-text tools.
- The consistency checker must support two mechanisms (inline + sidecar).
- Open questions for future ADRs: sidecar naming and placement (file inside
  the folder vs. sibling), selector syntax for partial regions, exact `.smap`
  format.
