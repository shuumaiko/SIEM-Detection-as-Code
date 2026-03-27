# Repo Map

## Core Layers

- `rules/`: reusable detection content and rule taxonomy.
- `mappings/`: canonical field contracts between source rule fields and tenant fields.
- `tenants/`: tenant-specific devices, logsources, bindings, filters, overrides, and deployments.
- `artifacts/`: rendered tenant output.
- `project-root/`: Python engine, CLI, validators, repositories, and tests.

## Important Stable Paths

- `project-root/interfaces/cli.py`: supported CLI commands.
- `project-root/tests/test_validate_tenant_config.py`: tenant validation smoke check.
- `project-root/tests/test_folder_architecture.py`: structural expectations for tenant and artifact paths.
- `schema/tenants/`: tenant validation schemas.
- `schema/rules/`: rule validation schemas.

## Quick Decision Guide

- If the user changes reusable logic, start in `rules/`.
- If the user changes field naming or field portability, inspect `mappings/` and `tenants/.../bindings/fields/`.
- If the user changes where data is ingested, inspect `tenants/.../logsources/` and `tenants/.../bindings/ingest/`.
- If the user changes enablement or deployment scope, inspect `tenants/.../deployments/rule-deployments.yaml`.
- If the user changes validation behavior, inspect `project-root/app/services/`, `schema/`, and `project-root/tests/`.

## Common Guardrails

- Do not treat `artifacts/` as the source of truth for semantic content.
- Do not break the alignment between tenant datasets and ingest bindings.
- Do not move tenant-specific tuning into shared base rules without a strong reason.
- Do not leave tests stale after changing path conventions or validation rules.
