# ADR-0011: Packaging — Pure-Markdown Skills

- Status: Accepted
- Date: 2026-07-08
- Amends: ADR-0010 (drops the PostToolUse check hook from v1)

## Context

The 7 skills (ADR-0010) need a distribution shape, and `check` needs an
execution story. ADR-0010 assumed a PostToolUse hook running a structural
check on edited files — but hooks execute commands, not skills, so that
design implies shipping an executable. Candidates:

1. Plugin of markdown skills + bundled checker script + hook definition
2. Pure-markdown skills only
3. Standalone CLI package (npm/pip) + thin skill wrappers

## Decision

Option 2, chosen for v1 simplicity and portability: **specz ships as
markdown skills only — no scripts, no hooks, no runtime dependencies.**

- All seven skills are prompt-only. `check` prescribes exact, reproducible
  command pipelines (`rg`, `shasum`, glob) that the agent executes via its
  shell tool; the *commands* are deterministic even though *invocation* is
  agent-driven.
- **v1 has no PostToolUse hook** (amending ADR-0010): the edit-time safety
  net is replaced by the convention layer (rules block) plus `check`
  running as part of `reconcile` and on demand.
- CI gating in v1 is the user's choice: run the same documented command
  pipeline directly in CI (it is a handful of `rg` invocations), or skip.
- Portability to other agents reduces to porting markdown files.

Rejected (for v1):

- **Plugin + bundled script**: honors the edit-time hook and gives CI a
  first-class executable, but forces a runtime choice (python3/node) and
  more release surface before the idea is proven. Remains the natural v2
  upgrade path — the `check` skill's command pipeline is the spec for that
  script.
- **Standalone CLI**: cleanest CI story but two artifacts to
  release-sync; heavier than validating the framework requires.

## Consequences

- Zero-install adoption: copy or install skills, run `/specz:init`.
- Forgotten mappings are caught at reconcile/check time, not edit time —
  a longer feedback loop, accepted for v1.
- `check` results are reproducible given the same tree; token cost of
  checking is bounded by the skill invoking shell commands rather than
  reading files into context.
- If v1 proves out, ADR-0010's hook + script design can be restored as a
  pure addition (no format changes): the skill's pipeline becomes the
  script, the script becomes the hook.
