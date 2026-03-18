# SIEM-Detection-as-Code Documentation

This `docs/` directory contains the architecture and supporting notes for the `SIEM-Detection-as-Code` repository.

The current documentation is organized around the new repository architecture, with separate Vietnamese and English architecture documents so the team can maintain both views in parallel.

## Documentation Structure

```text
docs/
|-- README.md
|-- architecture/
|   |-- project-architecture.md
|   |-- tenants-relationship.md
|   `-- mappings-relationship.md
|-- en/
|   `-- architecture/
|       |-- project-architecture.md
|       |-- tenants-relationship.md
|       `-- mappings-relationship.md
`-- note/
    |-- base-note.txt
    `-- SIEM-DaC-Idea.md
```

## What Each Area Contains

### `architecture/`

Vietnamese architecture documents for the current repository model:

- `project-architecture.md`: overall project architecture
- `tenants-relationship.md`: tenant-layer structure and relationships
- `mappings-relationship.md`: mapping-layer scope, contracts, and direction

### `en/architecture/`

English versions of the main architecture documents, kept in a mirrored structure:

- `project-architecture.md`
- `tenants-relationship.md`
- `mappings-relationship.md`

### `note/`

Working notes and earlier thinking that provide historical context or raw design ideas:

- `base-note.txt`
- `SIEM-DaC-Idea.md`

These notes are useful for reference, but the main architecture source of truth should be the documents under `architecture/` and `en/architecture/`.

## Recommended Reading Order

### If you want the current architecture overview

1. `architecture/project-architecture.md`
2. `architecture/tenants-relationship.md`
3. `architecture/mappings-relationship.md`

### If you want the English version

1. `en/architecture/project-architecture.md`
2. `en/architecture/tenants-relationship.md`
3. `en/architecture/mappings-relationship.md`

### If you want historical context

1. `note/base-note.txt`
2. `note/SIEM-DaC-Idea.md`

## Documentation Intent

The documentation in this folder reflects the current direction of the repository:

- keep `Detection as Code` as the core operating model
- move away from manual rule deployment and manual rule management
- standardize how rules, mappings, tenant configuration, and rendered artifacts relate to each other
- provide a clearer architecture reference while implementation code is still catching up

## Current Status

At this stage:

- the architecture documents are more reliable than older implementation assumptions
- `docs/architecture/` is the primary reference in Vietnamese
- `docs/en/architecture/` is the primary reference in English
- some older note files may still use legacy naming such as `SIEM-DaC`

## Summary

Use this folder as the entry point for understanding how `SIEM-Detection-as-Code` is structured today.

For architecture, start from `architecture/` or `en/architecture/`. For older thinking and design history, use `note/`.
