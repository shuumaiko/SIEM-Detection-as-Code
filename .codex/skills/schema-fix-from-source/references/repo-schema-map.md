# Repo Schema Map

Use this file as the first lookup when deciding what schema to edit.

## Rule Files

- Detection-style rule samples:
  - `rules/detections/**/*.yml`
  - `rules/detections/**/*.yaml`
- Analyst-style rule samples:
  - `rules/analysts/**/*.yml`
  - `rules/analysts/**/*.yaml`
- Current schema targets:
  - `schema/rules/base_rule.schema.json`
  - `schema/rules/correlation_rule.schema.json`
  - `schema/rules/rule_file.schema.json`

Current repo examples show drift that must be modeled from source files:

- `rules/detections/network/firewall/base/fw_external_connection.yaml` uses a single YAML document and `rule_type: base`.
- `rules/analysts/network/firewall/base/net_fw_request_reached_over_threshold.yaml` uses a single YAML document, `rule_type: analyst`, `correlation`, and `x_query`.

Decision hint:

- Split schemas if detection and analyst rules continue to have materially different top-level blocks.
- Use one rule entry schema if the user explicitly wants a unified contract and the discriminator strategy stays readable.

## Mapping Files

- Detection mapping samples:
  - `mappings/detections/**/*.fields.yaml`
  - `mappings/detections/**/*.fields.yml`
- Current schema target:
  - `schema/mappings/detection_fields.schema.json`

Decision hint:

- Keep one shared schema when mapping files share the same envelope and only differ in content.

## Tenant Files

- Tenant root:
  - `tenants/*/tenant.yaml`
- Devices:
  - `tenants/*/devices/*.yaml`
- Logsources:
  - `tenants/*/logsources/*.yaml`
- Ingest bindings:
  - `tenants/*/bindings/ingest/*.yaml`
- Field bindings:
  - `tenants/*/bindings/fields/*.yml`
  - `tenants/*/bindings/fields/*.yaml`
- Deployments:
  - `tenants/*/deployments/*.yaml`

Current schema targets:

- `schema/tenants/tenant.schema.json`
- `schema/tenants/device.schema.json`
- `schema/tenants/logsource.schema.json`
- `schema/tenants/binding.schema.json`
- `schema/tenants/field_binding.schema.json`
- `schema/tenants/rule_deployments.schema.json`

Decision hint:

- Keep per-file-type schemas for tenant data unless the user explicitly requests consolidation.

## Artifact Files

- Artifact template:
  - `artifacts/default.yml`
- Current rendered samples:
  - `artifacts/*/tenant-rules/**/*.yml`
  - `artifacts/*/tenant-rules/**/*.yaml`
- Current schema target:
  - `schema/artifacts/artifact.schema.json`

Decision hint:

- Prefer one artifact envelope schema per rendered artifact family.
- Treat `artifacts/default.yml` and the current render flow as the contract source of truth.
- Call out drift when older rendered samples still look like flattened source rules instead of the documented envelope.

## Notes To Reuse

- Read `log/2026-03-23/repo-gap-review/repo-gap-review.md` when the task is about rule schema drift or split-vs-unified rule contracts.
- Stay outside `project-root/`; schema design here is repository-contract work, not runtime-engine work.
