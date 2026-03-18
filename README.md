# SIEM-Detection-as-Code

This repository manages `Detection as Code` for a multi-tenant SOC environment, with a structure that separates detection logic, field normalization, tenant-specific configuration, and SIEM-specific deployment artifacts.

## Objectives

`SIEM-Detection-as-Code` is designed to:

- separate detection logic from vendor-specific log formats
- separate detection logic from SIEM-specific implementation
- manage detection rules as code
- support validation, rendering, export, and deployment per tenant
- improve reuse of detection content across multiple tenants

From an architectural point of view, this repository is not just a collection of YAML rules. It is a layered model for organizing detection content, where:

- `rules/` stores core detection knowledge
- `mappings/` stores the field normalization layer
- `tenants/` stores tenant-specific real-world configuration
- `artifacts/` stores rendered output per tenant
- `project-root/` contains the application engine used to read, validate, render, and deploy

## Current Status

The architecture documentation has been updated to the new model under `docs/architecture/`, but the implementation in `project-root/` is still in transition and does not yet fully reflect that architecture.

This means:

- the repository structure and documented data relationships are currently the main reference
- some older code paths may not work correctly after the architecture changes
- hardcoded SIEM queries, especially on the Splunk side, are still used as temporary execution artifacts
- this README is intentionally architecture-first and content-first, rather than a full end-to-end runtime guide

For deeper details, see:

- `docs/architecture/project-architecture.md`
- `docs/architecture/tenants-relationship.md`
- `docs/architecture/mappings-relationship.md`

## Architectural View

The system can be understood through 3 main axes.

### 1. Detection Content Axis

This is the layer that manages detection knowledge:

- `rules/`: base detection rules by category and product
- `mappings/detections/`: mappings from source rule fields to canonical fields
- `tenants/.../bindings/fields/`: mappings from canonical fields to tenant SIEM fields

The goal of this axis is to keep detection logic stable enough to be reused, instead of coupling it directly to parser output or field naming from a specific tenant.

### 2. Tenant Configuration Axis

This axis describes the real operating environment of each tenant:

- `tenant.yaml`: tenant identity, `siem_id`, and operational metadata
- `devices/`: devices or platforms that produce logs
- `logsources/`: logical datasets for each device
- `bindings/ingest/`: mappings from `dataset_id` to real ingestion targets such as `index` and `sourcetype`
- `bindings/fields/`: mappings from canonical fields to actual SIEM fields
- `filters/`: tenant-specific filters applied during rendering
- `deployments/rule-deployments.yaml`: manifest for enabling or disabling rules by SIEM

This axis answers operational questions such as:

- which log sources a tenant has
- which datasets are active
- how those datasets are ingested into the SIEM
- which rules are enabled for the tenant
- which filters should be applied when rendering from base rules

### 3. Operations and Output Axis

This axis supports validation, build, export, and deployment:

- `project-root/`: CLI, use cases, services, repositories, and adapters
- `schema/`: contracts used to validate rules and tenant configuration
- `tests/`: quality gates such as smoke tests, validators, and structure checks
- `artifacts/`: rendered or exported output for each tenant

## Core Data Model

The current architecture revolves around 4 main linking keys:

| Key | Meaning |
| --- | --- |
| `tenant_id` | tenant identifier |
| `device_id` | identifier of the device or platform producing logs |
| `dataset_id` | identifier of a device's logical dataset |
| `siem_id` | target SIEM identifier |

Main relationships in the tenant layer:

- a `tenant` owns `devices`
- each `device` has a `logsource`
- a `logsource` declares one or more `dataset_id`
- `bindings/ingest` links `dataset_id` to real ingestion targets on the SIEM
- `bindings/fields` links canonical fields to the tenant's actual SIEM fields
- `filters` refine base rules during rendering
- `deployments` decide which rules continue through the pipeline

## The Role of `mappings/`

In the current architecture, `mappings/` should not be interpreted as a layer that solves the entire path from raw logs to final SIEM fields. Instead, it acts as a field contract layer so the content team can normalize detection vocabulary and connect detection logic to the actual fields available for each tenant.

The practical field pipeline currently looks like this:

```text
source rule field <=> canonical field <=> tenant SIEM field
```

Where:

- `source rule field` is a field from the original rule source or legacy content
- `canonical field` is the project's internal standard vocabulary
- `tenant SIEM field` is the actual field currently available in the tenant's SIEM

This approach helps:

- ingest rules coming from different field vocabularies
- reduce dependence on personal naming conventions
- support tenant-based rendering even when the generic converter is still incomplete
- preserve a stable semantic contract between the content team and the deployment team

## The Role of Hardcoded SIEM Queries

In the current state of the project, hardcoded queries such as SPL are still considered valid execution artifacts in the pipeline.

This is an intentional trade-off:

- the generic converter from standard detection rules to SIEM-specific rules is not yet stable
- the pipeline still needs output that can be reviewed, exported, or deployed
- detection intent and canonical fields remain in the content layer, while hardcoded queries temporarily handle execution

In short:

- canonical fields preserve `meaning`
- hardcoded queries preserve `execution`

## High-Level Processing Flow

At the architecture level, the project pipeline is currently understood as:

1. Load tenant configuration from `tenants/<tenant>/`.
2. Resolve `tenant_id`, `siem_id`, devices, and datasets.
3. Load base rules from `rules/`.
4. Load detection mappings from `mappings/detections/`.
5. Resolve ingest bindings from `tenants/.../bindings/ingest/`.
6. Resolve field bindings from `tenants/.../bindings/fields/`.
7. Apply tenant filters from `tenants/.../filters/`.
8. Read `deployments/rule-deployments.yaml` to select the enabled rule set for the tenant.
9. Render output into `artifacts/<tenant>/tenant-rules/`.
10. If needed, use adapters in `project-root/` to export or deploy to the target SIEM.

## Repository Structure

```text
.
|-- artifacts/
|   `-- <tenant>/
|       `-- tenant-rules/
|           `-- detections/
|-- docs/
|   `-- architecture/
|-- mappings/
|   `-- detections/
|-- project-root/
|   |-- app/
|   |-- domain/
|   |-- infrastructure/
|   |-- interfaces/
|   `-- main.py
|-- rules/
|   `-- detections/
|-- schema/
|-- tenants/
|   `-- <tenant>/
|       |-- tenant.yaml
|       |-- devices/
|       |-- logsources/
|       |-- bindings/
|       |   |-- ingest/
|       |   `-- fields/
|       |-- filters/
|       `-- deployments/
`-- tests/
```

Short meaning:

- `rules/` is the source of truth for core detection content
- `mappings/` is the source of truth for shared content-layer field mapping
- `tenants/` is the source of truth for tenant deployment configuration
- `artifacts/` is rendered output, not the long-term hand-edited source

## Primary References

When working with the repository in its current state, the recommended reading order is:

1. `docs/architecture/project-architecture.md`
2. `docs/architecture/tenants-relationship.md`
3. `docs/architecture/mappings-relationship.md`
4. `rules/`, `mappings/`, `tenants/`, `artifacts/`
5. `project-root/` as an implementation layer that is still being aligned to the new architecture

## Contributor Notes

- Treat `rules/`, `mappings/`, and `tenants/` as the main data layers of the repository.
- Do not treat `artifacts/` as the long-term place for manual edits; it is tenant-rendered output.
- When adding a new rule, try to identify clearly:
  - the detection intent
  - the source rule fields being used
  - the canonical fields required
  - the tenant bindings needed to render for the target tenant
- When updating documentation or structure, keep it aligned with the architecture documents under `docs/architecture/`.

## Summary

`SIEM-Detection-as-Code` is currently organized around this model:

- `rules/` stores detection knowledge
- `mappings/` stores the field contract
- `tenants/` stores the real deployment state of each tenant
- `artifacts/` stores rendered output
- `project-root/` is the engine that is gradually being aligned to this architecture

At this stage, the architecture documentation is more stable than the runtime implementation. This README is therefore intended to reflect the current data model and the correct way to understand the repository under the new architectural version.
