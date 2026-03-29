# Code Log: Restore Per-Rule Artifacts And Move Summary To CLI

## Request Summary

Revert the mistaken summary-only artifact behavior. Keep generated tenant artifacts under `artifacts/<tenant>/tenant-rules/` as before, but change the CLI output so it returns only basic metadata such as generated rule counts and deployed logsource scope. Rename the command from `export-rules` to `gen-artifact`.

## Business Definition

- Goal: preserve materialized per-rule tenant artifacts while making the command output focus on operator-facing summary metadata.
- User outcome: operators can regenerate deployable artifacts and immediately see a compact summary without replacing the artifact layer with a single export summary file.
- Entry command: `python project-root/main.py gen-artifact --tenant-id <tenant>`.
- Main input: source rules under `rules/`, tenant config under `tenants/`, and execution metadata under `legacy/execution/`.
- Main outputs:
  - per-rule artifacts under `artifacts/<tenant>/tenant-rules/`
  - deployment manifest at `tenants/<tenant>/deployments/rule-deployments.yaml`
  - CLI and API summary JSON with basic deployment metadata
- Affected flow steps:
  1. CLI command dispatch
  2. export use case orchestration
  3. per-rule artifact rendering
  4. artifact persistence
  5. summary payload returned to caller
- Ownership layers:
  - `interfaces`: add `gen-artifact` command and keep `export-rules` as compatibility alias
  - `app/usecases`: orchestrate artifact generation and build CLI summary
  - `app/services`: build per-rule artifact envelopes
  - `infrastructure/repositories`: persist and reload tenant artifact files
- Validation plan: run targeted pytest for export flow and repository behavior, then run the CLI command for tenant `lab`.
- Log file path: `docs/note/logs/code/2026-03-29-gen-artifact-cli-summary-correction.md`.

## Function Flow Summary

1. `interfaces.cli.run_cli()` now treats `gen-artifact` as the primary command and keeps `export-rules` as a legacy alias.
2. `app.usecases.export_rules.ExportRulesUseCase.prepare_export()` still renders mapped rules, saves per-rule artifacts, refreshes `rule-deployments.yaml`, and now returns a compact summary payload instead of a saved summary document.
3. `app.services.rule_artifact_service.RuleArtifactService.build_artifacts()` again emits one `tenant_rule` artifact per rendered rule, using the source rule path as the artifact-relative path.
4. `infrastructure.repositories.file_rule_repository.FileRuleRepository.save_rendered_for_tenant()` again writes to `artifacts/<tenant>/tenant-rules/`, while keeping the multiline YAML dumper so `search_query` stays readable.
5. `FileRuleRepository.list_for_tenant()` now reads those per-rule artifacts directly for downstream deploy flows.

## Files Changed

- `project-root/app/services/rule_artifact_service.py`
- `project-root/app/usecases/export_rules.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/interfaces/cli.py`
- `project-root/interfaces/api.py`
- `project-root/tests/test_export_rules.py`
- `project-root/tests/test_folder_architecture.py`

## Tests Run

- Pending after code change in this log entry.

## Risks And Follow-Ups

- `export-rules` is still kept as a compatibility alias for now to avoid breaking existing usage abruptly.
- If the team wants a hard rename later, remove the alias in a dedicated compatibility cleanup.
