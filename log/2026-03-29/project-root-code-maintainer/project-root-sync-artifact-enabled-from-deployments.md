# Code Log: Sync Artifact Enabled State From Rule Deployments

## Request Summary

Use the `project-root-code-maintainer` flow to update rendered tenant artifacts so their final `enabled` state reflects `tenants/<tenant>/deployments/rule-deployments.yaml` after export.

## Business Definition

- Goal: ensure persisted artifacts expose the tenant's final deployment decision instead of keeping only the execution-layer default for `enabled`.
- User outcome: after running `export-rules`, each artifact shows the same enabled or disabled state as the saved deployment manifest.
- Entry command: `python project-root/main.py export-rules --tenant-id <tenant>`.
- Main input data: `rules/`, tenant bindings, execution config, and `tenants/<tenant>/deployments/rule-deployments.yaml`.
- Main output artifact: `artifacts/<tenant>/tenant-rules/**/*.yml` with `x_<siem>.targets.enabled` synchronized from the deployment manifest.
- Affected flow steps:
  1. build render candidates
  2. write artifact files
  3. save deployment manifest
  4. reload tenant deployments
  5. sync enabled state back into persisted artifacts
- Correct ownership:
  - `app/usecases`: orchestrate the reread and sync sequence
  - `app/services`: expose artifact state sync through the rule service
  - `infrastructure/repositories`: rewrite artifact files on disk
- Validation plan: targeted pytest coverage for export flow and deployment builder behavior.
- Log file path: `log/2026-03-29/project-root-code-maintainer/project-root-sync-artifact-enabled-from-deployments.md`.

## Function Flow Summary

1. `interfaces.cli.run_cli()` dispatches `export-rules`.
2. `ExportRulesUseCase.prepare_export()` renders source rules and persists artifact files.
3. The same use case saves `rule-deployments.yaml`.
4. `ExportRulesUseCase.prepare_export()` reloads the tenant aggregate from disk so the just-written deployment manifest becomes the source of truth.
5. `RuleService.sync_artifact_enabled_states()` delegates to the rule repository.
6. `FileRuleRepository.sync_artifact_enabled_states()` rewrites each saved artifact and sets `x_<siem>.targets.enabled` from the deployment manifest entry keyed by artifact `id`.

## Files Changed

- `project-root/domain/repositories/rule_repository.py`
- `project-root/app/services/rule_service.py`
- `project-root/app/usecases/export_rules.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/tests/test_export_rules.py`

## Tests Run

- `..\.venv\Scripts\python.exe -m pytest tests/test_export_rules.py tests/test_rule_deployment_builder.py -o cache_dir=.pytest_cache_local` from `project-root/`

## Risks And Follow-ups

- The sync logic currently updates the SIEM-specific `targets.enabled` field only. If a future artifact contract introduces a separate top-level deployment state, the sync step should update both locations consistently.
- The lookup key prefers artifact `id`, then falls back to `source_rule.rule_id`. This preserves current split-artifact behavior where deployment IDs may be target-scoped.

## Assumptions

- The deployment manifest is the final tenant decision for whether a rendered artifact should be active, even when execution defaults or rule overrides set a different `enabled` value earlier in the pipeline.

