# ADR-0005: specz Folder Layout

- Status: Accepted
- Date: 2026-07-07

## Context

Since ADR-0002, IDs carry a frozen domain segment, so filenames self-group —
raising the question whether domain folders are redundant, free-form, or
enforced. Candidates:

1. Flat folder (segment is the only grouping)
2. Free-form domain folders, conventionally mirroring segments
3. Enforced folders (path mechanically derived from segment)

## Decision

Option 2: **free-form folders with a segment-mirroring convention.**

```
specz/
  SPECS.md            # outline file
  config.yaml         # segment registry, settings
  auth/
    spz-auth-bz.md
    sso/
      spz-auth-k4.md  # nesting allowed
  perf/
    spz-perf-c1.md
```

- `/specz:init` creates one folder per registered segment and places specs
  accordingly — the *convention*.
- Folders are **not enforced** and carry no semantic meaning (ADR-0003).
  Specs may live anywhere under `specz/`, nest arbitrarily deep, and move
  freely without touching IDs, references, or code comments.
- The checker **warns** (never errors) when a spec lives outside the folder
  matching its segment — surfacing confusion without blocking restructuring.
- ID→file resolution is a lookup (`rg --files -g "spz-auth-bz.md"`), not
  string concatenation.

Rejected:

- **Flat folder**: zero redundancy and trivial ID→path, but hundreds of
  specs become a wall, sub-domain nesting is impossible, and GitHub's UI
  truncates large directories.
- **Enforced folder=segment**: one truth and zero lookup, but it re-couples
  the immutable ID to the mutable file tree — a stale segment would force a
  lying folder or an ID rename, contradicting accepted ADR-0002.

## Consequences

- Large spec sets stay navigable for humans and agents; domains can grow
  sub-folders without new registry segments.
- Two grouping mechanisms (segment, folder) can disagree; accepted as a
  warning-level concern.
- Tools must resolve IDs by search, not by path construction.
