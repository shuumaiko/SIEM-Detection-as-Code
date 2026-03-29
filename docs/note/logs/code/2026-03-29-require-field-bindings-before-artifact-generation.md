# Code Log: Require Field Bindings Before Artifact Generation

## Request Summary

Prevent blind artifact generation by requiring real tenant field mappings before a device or dataset can produce a rendered rule.

## Business Definition

- Goal: only generate tenant artifacts for targets that have both ingest wiring and an actual field mapping contract.
- User outcome: datasets like `eset-ra-alerts` are skipped during `gen-artifact` until the tenant provides a usable `bindings/fields` mapping.
- Entry command: `python project-root/main.py gen-artifact --tenant-id <tenant>`.
- Main input: source rules, tenant devices and logsources, ingest bindings, and field bindings.
- Main output artifact: per-rule tenant artifacts only for targets that have field mappings.
- Affected flow steps:
  1. export use case orchestration
  2. deployment builder resolves tenant targets
  3. target resolution now requires field bindings
  4. artifact and deployment outputs only include validated targets
- Ownership layers:
  - `app/services/rule_deployment_builder.py`
  - `tests/test_export_rules.py`
- Validation plan: targeted pytest for export flow, then rerun `gen-artifact` for tenant `lab`.
- Log file path: `docs/note/logs/code/2026-03-29-require-field-bindings-before-artifact-generation.md`.

## Function Flow Summary

1. `ExportRulesUseCase.prepare_export()` still delegates target resolution to `RuleDeploymentBuilder`.
2. `RuleDeploymentBuilder._collect_ingest_targets()` now calls `_has_field_mapping()` before accepting a dataset target.
3. `_has_field_mapping()` treats either a dataset-specific mapping or a non-empty `_default` mapping as sufficient proof that the tenant has provided real field bindings.
4. Targets with only ingest bindings are skipped, which prevents artifact and deployment generation for unbound datasets.

## Files Changed

- `project-root/app/services/rule_deployment_builder.py`
- `project-root/tests/test_export_rules.py`

## Tests Run

- Pending after implementation in this log entry.

## Risks And Follow-Ups

- Existing tenants that relied on ingest-only generation will now produce fewer artifacts until field bindings are added.
- If the team later wants stricter validation, `_has_field_mapping()` can evolve from “any non-empty field mapping” to “required fields covered for the specific rule pack.”
