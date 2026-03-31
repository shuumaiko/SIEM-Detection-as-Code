# Code Log: Start Hardcoded Query Render Flow In `project-root/`

## Request Summary

Start repairing the `project-root/` engine so the flow can begin from current source rules and render output into `artifacts/<tenant>/tenant-rules/` using the hardcoded query approach.

## Business Definition

- Goal: make the current implementation follow the documented hardcoded-query render path instead of reading prebuilt artifacts as input.
- User outcome: running the render command from `project-root/` should materialize tenant artifacts from source rules and refresh `tenants/<tenant>/deployments/rule-deployments.yaml` with current rule IDs.
- Entry command: `python project-root/main.py export-rules --tenant-id <tenant>`.
- Main input data: `rules/detections/`, `tenants/<tenant>/`, `legacy/execution/<siem>/`, and mapping registry files.
- Main output artifact: `artifacts/<tenant>/tenant-rules/detections/**`.
- Correct ownership:
  - `interfaces/`: keep CLI unchanged as the entrypoint.
  - `app/usecases/`: coordinate the end-to-end render sequence.
  - `app/services/`: flatten source rules, resolve targets, and build artifact documents.
  - `infrastructure/`: load execution config and persist rendered files.
- Validation plan: add/update repository and use-case tests, then run the CLI once against `lab`.
- Log file path: `log/2026-03-28/project-root-code-maintainer/project-root-hardcoded-render-flow.md`.

## Function Flow Summary

1. `interfaces.cli.run_cli()` dispatches `export-rules`.
2. `ExportRulesUseCase.execute()` loads the tenant and source rules that expose hardcoded queries.
3. `ExportService.export_rules()` flattens source rules into render payloads.
4. `RuleDeploymentBuilder.build()` resolves ingest targets from tenant bindings and substitutes ingest placeholders in hardcoded queries.
5. `RuleArtifactService.build_artifacts()` merges execution defaults and tenant execution overrides, then builds final artifact documents with `x_splunk_es`.
6. `RuleService.save_rendered_rules_for_tenant()` persists rendered rules into `artifacts/<tenant>/tenant-rules/detections/`.
7. `TenantRepository.save_rule_deployments()` writes a refreshed deployment manifest keyed by the current rendered rule IDs.

## Files Changed

- `project-root/domain/models/rule.py`
- `project-root/domain/repositories/rule_repository.py`
- `project-root/app/services/rule_service.py`
- `project-root/app/services/export_service.py`
- `project-root/app/services/rule_deployment_builder.py`
- `project-root/app/services/rule_artifact_service.py`
- `project-root/app/usecases/export_rules.py`
- `project-root/infrastructure/file_loader/execution_config_loader.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/infrastructure/repositories/file_tenant_repository.py`
- `project-root/main.py`
- `project-root/tests/test_export_rules.py`
- `project-root/tests/test_folder_architecture.py`

## Tests Run

- `python -m pytest -o cache_dir=.pytest_cache_local tests/test_export_rules.py tests/test_folder_architecture.py tests/test_smoke.py` from `project-root/`
- `python main.py export-rules --tenant-id lab` from `project-root/`

## Important Outcomes

- `export-rules` now renders from current source rules instead of reading `artifacts/` as input.
- Rendered artifacts are now written to `artifacts/lab/tenant-rules/detections/...`.
- `rule-deployments.yaml` is regenerated from current rule IDs and no longer remains pinned to the legacy IDs used by the old sample file.
- Field-binding loading now understands `default_field_mapping` plus per-dataset `field_mapping`.

## Risks And Follow-ups

- Tenant filter overrides under `tenants/<tenant>/overrides/filter/` are not applied yet in this first hardcoded-query render phase.
- Analyst-layer query override flow is not implemented yet in this phase.
- `webaccess_ua_apt` still renders without resolved ingest targets because the current tenant sample data uses inconsistent device IDs between `devices/`, `logsources/`, and `bindings/` for the webserver path.
- Pytest can still emit cache warnings in this environment because the default cache/temp locations have restrictive permissions; the targeted tests passed despite that warning.

## Assumptions

- The user request `./project-code` refers to the active engine under `project-root/`.

