# specz — spec traceability AI framework

specz is a traceability layer that wraps around whichever dev framework does
the thinking (superpowers, gstack, or plain chat). It owns spec format,
mapping, and consistency — never brainstorming, planning, or implementation.

## Install (Claude Code)

    /plugin marketplace add <this repo url or path>
    /plugin install specz

Then in your project: `/specz:init`.

## Skills

| Skill | Stage | What it does |
|-------|-------|--------------|
| /specz:init | adoption | create specz/, install rules block; brownfield: draft specs gated on review |
| /specz:capture | capture | design/plan artifact → spec files with IDs and acceptance criteria |
| /specz:context | context | load a spec, its [[refs]], and mapped code for an ID |
| /specz:map | mapping | maintain SPECZ: lines and .specz sidecars while coding |
| /specz:reconcile | reconcile | verify ACs, flip todo→done, write the synced hash; repair drift |
| /specz:check | verify | deterministic structural checks (CI-friendly) |
| /specz:audit | verify | semantic review: does code satisfy the ACs? |

Decisions live in `docs/adr/`. The skill-verification fixture lives in
`tests/fixture/webapp/`.
