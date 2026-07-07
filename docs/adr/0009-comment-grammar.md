# ADR-0009: Inline Comment Grammar

- Status: Accepted
- Date: 2026-07-07

## Context

Inline comments are the primary mapping mechanism (ADR-0001). Every
annotated line in every codebase carries the marker forever, so its exact
grammar must be pinned. The marker's job is to distinguish a **mapping
declaration** from a casual mention of a spec ID in prose or doc comments —
`rg spz-auth-bz` finds both; the checker must see only the former.

## Decision

**Uppercase `SPECZ:` marker, comma-separated lowercase IDs, native comment
syntax, on the line directly above the mapped code:**

```
<comment-leader> SPECZ: <id>[, <id>]*
```

```python
# SPECZ: spz-auth-bz, spz-perf-c1
def login(user, pw): ...
```

```javascript
// SPECZ: spz-ui-k2
function render() { ... }
```

- The marker is always uppercase `SPECZ:` (with colon); IDs stay lowercase
  (ADR-0002) — the case contrast separates anchor from payload at a glance,
  and the marker pops like `TODO:`/`FIXME:`, which editors already
  highlight by convention.
- One space after the colon; IDs separated by comma-space. The checker
  accepts flexible whitespace but skills always write the canonical form.
- The comment uses the file's native comment leader (`#`, `//`, `--`,
  `<!-- -->`, …) and sits directly above the function/class/snippet it
  maps (ADR-0001).
- `rg "SPECZ:"` lists every mapping declaration in the repo and nothing
  else; prose references to an ID without the marker are mentions, not
  mappings.

Rejected:

- **Lowercase `specz:`**: consistent aesthetic but reads like prose — no
  editor convention treats it as an anchor.
- **No marker (bare IDs in a comment)**: shortest, but declaration and
  mention become indistinguishable — checker false-positives on doc
  comments.

## Consequences

- One-grep inventories: `rg "SPECZ:"` (all mapped code),
  `rg "SPECZ:.*spz-auth"` (all auth-mapped code).
- The checker validates that every ID on a `SPECZ:` line exists and is not
  archived; unregistered segments are caught per ADR-0002.
- Doc comments may mention IDs freely without confusing tooling.
