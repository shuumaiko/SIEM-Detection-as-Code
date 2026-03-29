# SIEM-Detection-as-Code Documentation

This `docs/` directory contains the architecture documents, rendering-flow notes, and historical review material for the repository.

## Source Of Truth

- Use `docs/architecture/` as the primary architecture reference.
- Use `docs/en/architecture/` when you need the English mirror.
- Use `docs/note/` for historical context, gap reviews, and change logs.

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
`-- note/
    |-- repo-gap-review-2026-03-23.md
    `-- logs/
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

1. `note/repo-gap-review-2026-03-23.md`
2. `note/logs/code/*.md`

## Current Status

The current project state is:

- architecture documents are stable and should be preserved
- the hardcoded-query render flow is operational in `project-root/`
- rendered tenant artifacts now use the artifact envelope documented in `artifacts/default.yml`
- some `legacy/` folders remain for compatibility and historical reference

## Summary

Use this folder to understand the repository before changing code or data. Architecture lives in `docs/architecture/`; history and transition notes live in `docs/note/`.
