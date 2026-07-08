<!-- specz:rules:begin -->
## specz traceability rules
This project tracks requirements in `specz/` (see specz/SPECS.md).
- After producing any design or plan artifact, run /specz:capture to turn it
  into spec files (or write acceptance criteria in specz format directly).
- When starting work on a spec ID, run /specz:context to load its slice.
- While writing code, maintain mappings: every source file starts with a
  `SPECZ:` line (or has a `.specz` sidecar); annotate inner units only when
  their spec set differs (see /specz:map).
- When a task is complete, run /specz:reconcile to verify acceptance
  criteria and update spec status.
- Never edit `status: done`/`synced:` by hand, or the SPECS.md index block.
<!-- specz:rules:end -->
