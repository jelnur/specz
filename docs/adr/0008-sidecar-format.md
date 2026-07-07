# ADR-0008: Sidecar Files for Uncommentable Files

- Status: Accepted
- Date: 2026-07-07
- Amends: ADR-0001 (replaces the working name `.smap` and pins the format)

## Context

ADR-0001 chose reference-only sidecars for uncommentable files but left
naming, placement, and format open, floating `.smap` as a working name and
folder/region coverage as possibilities. Candidates considered:

1. One dotfile per directory (`.gitignore`-style, `.` for the folder,
   `#fragment` for regions) — one mechanism for all cases
2. One sidecar per uncommentable file, no folder or region mapping
3. One repo-level map file

## Decision

Option 2, chosen for v1 simplicity: **each uncommentable file gets its own
sidecar; folders and regions are out of scope for v1.**

- **Naming:** target filename plus a `.specz` extension —
  `package.json` → `package.json.specz`, placed in the same directory.
  The `.smap` extension is dropped; no new extension vocabulary beyond the
  framework's own name.
- **Format:** plain text, one spec ID per line, nothing else:

  ```
  spz-infra-bb
  spz-sec-k9
  ```

- **No folder mapping** in v1: mappings attach to files only. Folder-level
  needs (e.g. a test directory serving one spec) are expressed by inline
  comments in the files inside it, or deferred.
- **No region mapping** in v1: a sidecar always refers to the whole target
  file. Partially-relevant files (e.g. a CSV header) map wholesale.

Rejected (for v1):

- **Per-directory dotfile**: covers folders/regions/binaries with one
  mechanism and survives folder moves for free, but is a hidden file with
  mixed entries and more format to specify — more machinery than v1 needs.
- **Repo-level map**: the central manifest already rejected in ADR-0001
  (invisible at edit point, rename-fragile, conflict hub).

## Consequences

- Format is trivial to parse, write, and merge; per-target files keep
  conflicts near zero; sidecars are visible in every directory listing.
- Discovery: `glob **/*.specz`; the checker pairs each sidecar with its
  target (strip the extension) and flags orphans — a rename that leaves
  `old-name.json.specz` behind is a structural error.
- Config-heavy directories accumulate one sidecar per mapped file;
  accepted as v1 cost.
- Folder and region mapping remain open as post-v1 extensions; if added,
  they must not break the `<file>.specz` contract (a per-directory file or
  fragment syntax can layer on later).
- ADR-0001's mechanism decision stands; only the name (`.specz`, not
  `.smap`) and scope (files only) are refined here.
