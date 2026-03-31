# SIEM-Detection-as-Code Documentation

This `docs/` directory contains the architecture documents, rendering-flow notes, and historical review material for the repository.

## Source Of Truth

- Use `docs/architecture/` as the primary architecture reference.
- Use `docs/en/architecture/` when you need the English mirror.
- Use `docs/note/` for repo-local notes and historical context; use `log/` for local task and review logs.

Documentation updates should reflect the current project state without changing the repository's architectural direction unless that change is explicitly intended.

## Documentation Structure

```text
docs/
|-- README.md
|-- README.vi.md
|-- architecture/
|   |-- project-architecture.md
|   |-- rule-rendering-flows.md
|   |-- tenants-relationship.md
|   |-- mappings-relationship.md
|   `-- execution-relationship.md
|-- en/
|   `-- architecture/
|-- note/
|   |-- base-note.txt
|   `-- SIEM-DaC-Idea.md
`-- ../log/
    `-- YYYY-MM-DD/
        `-- <log-type>/
```

## Recommended Reading Order

If you want the current architecture:

1. `architecture/project-architecture.md`
2. `architecture/rule-rendering-flows.md`
3. `architecture/tenants-relationship.md`
4. `architecture/mappings-relationship.md`
5. `architecture/execution-relationship.md`

If you want the repository-local Codex workflow helpers:

1. `codex-skills.md`
2. `.codex/skills/*/SKILL.md`

If you want historical drift and implementation context:

1. `../log/2026-03-23/repo-gap-review/repo-gap-review.md`
2. `../log/YYYY-MM-DD/project-root-code-maintainer/*.md`

## Current Status

The current project state is:

- architecture documents are stable and should be preserved
- `execution/` is again a first-class architecture layer and is documented under `architecture/execution-relationship.md`
- the hardcoded-query render flow is operational in `project-root/`
- rendered tenant artifacts now use the artifact envelope documented in `artifacts/default.yml`
- some `legacy/` folders remain for compatibility and historical reference

## Summary

Use this folder to understand the repository before changing code or data. Architecture lives in `docs/architecture/`; repo-local notes stay in `docs/note/`; local task and review logs now live in `log/`.
