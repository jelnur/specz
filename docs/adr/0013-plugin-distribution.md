# ADR-0013: Distribution as a Claude Code Plugin

- Status: Accepted
- Date: 2026-07-08
- Concretizes: ADR-0011 (pure-markdown skills; this pins the install shape)

## Context

ADR-0011 decided specz ships as markdown skills only, but left the concrete
repo layout and install story open. Candidates: a bare folder of markdown
files users copy by hand, a Claude Code plugin, or both documented in
parallel.

## Decision

**Claude Code plugin layout**: `.claude-plugin/plugin.json` (plugin name
`specz`) plus a single-entry `.claude-plugin/marketplace.json`, with skills
at `skills/<name>/SKILL.md`.

- Install: `/plugin marketplace add <this repo>` then install `specz`;
  skills invoke as `/specz:<name>` — matching the naming ADR-0010 already
  uses.
- Still pure markdown: the manifests are metadata only; no scripts, hooks,
  or runtime dependencies enter the package (ADR-0011 holds).

Rejected:

- **Bare skills folder**: zero platform-specific files, but no namespaced
  commands (drifts from ADR-0010 naming), manual per-project install, no
  marketplace story.
- **Plugin + documented copy path**: covers other-agent users, but two
  install paths to keep in sync; the copy path stays possible regardless
  (the skills are plain markdown) and can be documented when someone needs
  it.

## Consequences

- Claude Code users get one-command install and the `/specz:` namespace.
- Two small JSON manifests are Claude-Code-specific; other agents ignore
  them and can consume `skills/*/SKILL.md` directly.
- Versioning rides `plugin.json`'s `version` field.
