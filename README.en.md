# SIEM-Detection-as-Code

This repository manages `Detection as Code` for a multi-tenant SOC environment, with a structure that separates detection logic, field normalization, execution metadata, tenant-specific configuration, and SIEM-specific output artifacts.

## What This Repository Is

`SIEM-Detection-as-Code` should be read as an architecture and repository model for building `Detection as Code` in multi-tenant environments.

The main idea is that a detection program should not be forced into a single flat layer of rules. In real SOC operations, the same detection intent often needs to be reused across:

- multiple tenants
- multiple device and logsource combinations
- multiple SIEM field naming schemes
- multiple deployment targets or execution formats

This repository therefore treats detection engineering as a layered system:

- `rules/` expresses detection intent
- `mappings/` expresses canonical field contracts
- `execution/` expresses SIEM-specific execution policy and metadata
- `tenants/` expresses tenant-specific deployment context
- `artifacts/` expresses rendered tenant output
- `project-root/` provides the engine that reads, validates, renders, and exports that model

In other words, this is not only a rule collection. It is a reference architecture for separating reusable detection knowledge from tenant-specific operational detail.

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
- `execution/` stores SIEM execution defaults and per-rule overrides
- `tenants/` stores tenant-specific real-world configuration
- `artifacts/` stores rendered output per tenant
- `project-root/` contains the application engine used to read, validate, render, and deploy

## Why Multi-Tenant Detection-as-Code

In a single-tenant setup, it is still possible to manage detections as a relatively direct mapping from rule logic to SIEM query. In a multi-tenant environment, that approach becomes harder to scale because:

- one detection may need different field bindings per tenant
- one tenant may have different devices, datasets, or parser behavior than another
- the same logical rule may need different enablement, filters, or deployment decisions per tenant
- the execution format may differ from the content model used to preserve detection meaning

This repository is designed around that separation problem.

The architecture aims to answer a practical question:

How can one detection definition remain reusable, while still being rendered into tenant-specific output that reflects real differences in ingestion, fields, filtering, and SIEM deployment?

The repository structure is the answer proposed by this project.

## Current Status

The architecture documentation has been updated to the new model under `docs/architecture/`, but the implementation in `project-root/` is still in transition and does not yet fully reflect that architecture.

This means:

- the repository structure and documented data relationships are currently the main reference
- some older code paths may not work correctly after the architecture changes
- hardcoded SIEM queries, especially on the Splunk side, are still used as temporary execution artifacts
- this README is intentionally architecture-first and content-first, rather than a full end-to-end runtime guide

For deeper details, see:

- `docs/architecture/project-architecture.md`
- `docs/architecture/rule-rendering-flows.md`
- `docs/architecture/tenants-relationship.md`
- `docs/architecture/mappings-relationship.md`
- `docs/architecture/execution-relationship.md`

## Architectural View

The system can be understood through 4 main axes.

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
- `overrides/`: tenant-specific execution or filter tuning applied during rendering
- `deployments/rule-deployments.yaml`: manifest for enabling or disabling rules by SIEM

This axis answers operational questions such as:

- which log sources a tenant has
- which datasets are active
- how those datasets are ingested into the SIEM
- which rules are enabled for the tenant
- which filters or tuning should be applied when rendering from base rules

### 3. Execution Configuration Axis

This axis describes how a semantic rule is operated on a specific SIEM:

- `execution/<siem>/defaults.yaml`: default execution policy for the SIEM
- `execution/<siem>/rule-overrides.yaml`: rule-specific execution overrides
- hardcoded SIEM query payloads that remain valid transition-stage execution artifacts

This axis answers questions such as:

- how often a rule should run
- what lookback window should be used
- what severity, risk score, or notable behavior should be attached
- how execution metadata stays separate from the semantic rule definition

### 4. Operations and Output Axis

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
- `overrides` tune execution or filter behavior during rendering
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
- hardcoded queries preserve transition-stage execution logic
- `execution/` preserves reusable execution metadata such as schedule, severity, and risk score

## High-Level Processing Flow

At the architecture level, the project pipeline is currently understood as:

1. Load tenant configuration from `tenants/<tenant>/`.
2. Resolve `tenant_id`, `siem_id`, devices, and datasets.
3. Load base rules from `rules/`.
4. Load detection mappings from `mappings/detections/`.
5. Resolve ingest bindings from `tenants/.../bindings/ingest/`.
6. Resolve field bindings from `tenants/.../bindings/fields/`.
7. Resolve execution policy from `execution/<siem>/`.
8. Apply tenant filters or tenant overrides when present.
9. Read `deployments/rule-deployments.yaml` to select the enabled rule set for the tenant.
10. Render output into `artifacts/<tenant>/tenant-rules/`.
11. If needed, use adapters in `project-root/` to export or deploy to the target SIEM.

## Repository Structure

```text
.
|-- artifacts/
|   `-- <tenant>/
|       `-- tenant-rules/
|           `-- detections/
|-- docs/
|   `-- architecture/
|-- execution/
|   `-- <siem>/
|       |-- defaults.yaml
|       |-- rule-overrides.yaml
|       `-- legacy/
|-- mappings/
|   `-- detections/
|-- project-root/
|   |-- app/
|   |-- domain/
|   |-- infrastructure/
|   |-- interfaces/
|   `-- main.py
|-- rules/
|   |-- detections/
|   `-- analysts/
|-- schema/
|-- tenants/
|   `-- <tenant>/
|       |-- tenant.yaml
|       |-- devices/
|       |-- logsources/
|       |-- bindings/
|       |   |-- ingest/
|       |   `-- fields/
|       |-- overrides/
|       |-- filters/
|       `-- deployments/
`-- tests/
```

Short meaning:

- `rules/` is the source of truth for core detection content
- `mappings/` is the source of truth for shared content-layer field mapping
- `execution/` is the source of truth for reusable SIEM execution policy
- `tenants/` is the source of truth for tenant deployment configuration
- `artifacts/` is rendered output, not the long-term hand-edited source

## Primary References

When working with the repository in its current state, the recommended reading order is:

1. `docs/architecture/project-architecture.md`
2. `docs/architecture/rule-rendering-flows.md`
3. `docs/architecture/tenants-relationship.md`
4. `docs/architecture/mappings-relationship.md`
5. `docs/architecture/execution-relationship.md`
6. `rules/`, `mappings/`, `execution/`, `tenants/`, `artifacts/`
7. `project-root/` as an implementation layer that is still being aligned to the new architecture

## Contributor Notes

- Treat `rules/`, `mappings/`, `execution/`, and `tenants/` as the main data layers of the repository.
- Do not treat `artifacts/` as the long-term place for manual edits; it is tenant-rendered output.
- For OCSF-driven mapping work, prefer cloning `ocsf-schema` into `.tmp/ocsf-schema` so the `detection-mapping-ocsf` skill can use a stable local reference.
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
- `execution/` stores SIEM execution policy and metadata
- `tenants/` stores the real deployment state of each tenant
- `artifacts/` stores rendered output
- `project-root/` is the engine that is gradually being aligned to this architecture

At this stage, the architecture documentation is more stable than the runtime implementation. This README is therefore intended to reflect the current data model and the correct way to understand the repository under the new architectural version.
