# Code Log: Align Artifact Render Flow With Deployable Rule Semantics

## Request Summary

Use the `project-root-code-maintainer` flow to fix artifact generation so rendered rules expose the real SIEM-facing rule name, base rules are not exported as standalone artifacts, analyst rules are rendered into artifacts, and the saved file shape matches the `artifacts/default.yml` envelope template.

## Business Definition

- Goal: make rendered tenant artifacts match the documented render model where deployable output contains tenant-ready rule names, analyst correlation content is rendered, base rules remain reusable semantic building blocks instead of standalone deployable artifacts, and each artifact is emitted in the repository's envelope format.
- User outcome: `export-rules` should produce `artifacts/<tenant>/tenant-rules/` with deployable detection and analyst artifacts, while skipping standalone output for `rule_type: base`.
- Entry command: `python project-root/main.py export-rules --tenant-id <tenant>`.
- Main input data: `rules/detections/`, `rules/analysts/`, `tenants/<tenant>/`, execution config, and tenant ingest bindings.
- Main output artifact: `artifacts/<tenant>/tenant-rules/detections/**` plus `artifacts/<tenant>/tenant-rules/analysts/**`.
- Affected flow steps:
  1. source rule discovery
  2. export payload flattening
  3. ingest target resolution
  4. artifact document shaping
  5. artifact persistence
- Correct ownership:
  - `infrastructure/repositories`: source-rule discovery and artifact file layout
  - `app/services/export_service.py`: renderable payload shaping and analyst logsource derivation
  - `app/services/rule_artifact_service.py`: deployable artifact naming
- Validation plan: update targeted export-flow tests and repository-path tests, then run them if Python runtime is available.
- Log file path: `log/2026-03-29/project-root-code-maintainer/project-root-artifact-render-analyst-flow.md`.

## Function Flow Summary

1. `interfaces.cli.run_cli()` dispatches `export-rules`.
2. `ExportRulesUseCase.execute()` loads the tenant and current render candidates.
3. `FileRuleRepository.list_render_candidates()` now scans both `rules/detections/` and `rules/analysts/`.
4. `ExportService.export_rules()` keeps base rules available for analyst reference, derives analyst logsource scope from referenced source rules, and emits only deployable `detection` and `analyst` payloads.
5. `RuleDeploymentBuilder.build()` resolves tenant ingest targets and updates deployment names with the device prefix.
6. `RuleArtifactService.build_artifacts()` writes the final envelope document with `artifact_schema_version`, `artifact_type`, `source_rule`, `display_name`, `metadata`, and the SIEM-specific payload under `x_<siem>`.
7. `FileRuleRepository.save_rendered_for_tenant()` now writes under `artifacts/<tenant>/tenant-rules/` so both `detections/` and `analysts/` survive the render.
8. `RuleDeploymentBuilder._apply_query_targets()` now normalizes multiline query whitespace so rendered `search_query` values do not contain redundant blank lines.

## Files Changed

- `project-root/app/services/export_service.py`
- `project-root/app/services/rule_artifact_service.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/tests/test_export_rules.py`
- `project-root/tests/test_folder_architecture.py`

## Tests Run

- Could not run targeted pytest in this environment because the available `python.exe` launcher points to the Windows app alias and fails to execute the local runtime.

## Risks And Follow-ups

- Analyst logsource derivation currently assumes referenced source rules share one compatible `category/product/service` scope. Mixed-scope analyst correlations may need an explicit conflict strategy later.
- Rendered artifact `name` is now aligned to the deployable SIEM-facing title. If any downstream consumer still expects the old source slug in `name`, that consumer should be updated to use `id` or a dedicated source metadata field instead.

## Assumptions

- Base rules are semantic building blocks for analyst correlation and should not be materialized as standalone tenant artifacts unless a future requirement explicitly asks for that.

