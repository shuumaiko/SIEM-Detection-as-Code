# Code Log: Refocus `export-rules` On Summary Artifact Output

## Request Summary

Change `export-rules` so it generates an export artifact that matches the command's operational purpose: summary metadata only, such as deployed rule counts and deployed logsource scope, instead of per-rule rendered rule documents.

## Business Definition

- Goal: make `export-rules` emit one tenant-level export artifact that summarizes what would be deployed, rather than materializing full per-rule execution documents.
- User outcome: operators can inspect one compact artifact to answer questions like how many rules are exported, which rule types are included, and which device or logsource targets are covered.
- Entry command: `python project-root/main.py export-rules --tenant-id <tenant>`.
- Main input data: current source rules under `rules/`, tenant config under `tenants/<tenant>/`, and resolved ingest or execution metadata from the hardcoded render flow.
- Main output artifact: `artifacts/<tenant>/export-summary.yml`.
- Affected flow steps:
  1. source rule render preparation
  2. deployment target resolution
  3. artifact summary shaping
  4. artifact persistence
  5. CLI and API return payloads
- Correct ownership:
  - `app/usecases`: distinguish internal deploy-ready payload from user-facing export summary
  - `app/services/rule_artifact_service.py`: build the summary artifact
  - `infrastructure/repositories/file_rule_repository.py`: persist and read the summary artifact format
- Validation plan: update targeted export tests and repository artifact tests, rerun the narrow pytest selection, then rerun `export-rules` for `lab`.
- Log file path: `docs/note/logs/code/2026-03-29-export-rules-summary-artifact.md`.

## Function Flow Summary

1. `interfaces.cli.run_cli()` dispatches `export-rules`.
2. `ExportRulesUseCase.prepare_export()` still resolves deploy-ready rule payloads internally for downstream deploy flows.
3. `RuleArtifactService.build_artifacts()` now builds a single `tenant_rule_export` summary document with counts, rule-type breakdown, deployed device or dataset coverage, deployed logsource scope, and a compact rule list.
4. `FileRuleRepository.save_rendered_for_tenant()` now writes the artifact to `artifacts/<tenant>/export-summary.yml`.
5. `ExportRulesUseCase.execute()` returns the summary artifact document to CLI or API callers.
6. `deploy-rules` still uses the internal mapped rule payload returned by `prepare_export()`.

## Files Changed

- `project-root/app/services/rule_artifact_service.py`
- `project-root/app/usecases/export_rules.py`
- `project-root/interfaces/cli.py`
- `project-root/interfaces/api.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/tests/test_export_rules.py`
- `project-root/tests/test_folder_architecture.py`

## Tests Run

- `python -m pytest tests/test_export_rules.py tests/test_folder_architecture.py -q` from `project-root/`
- Result: `4 passed, 1 warning`
- Warning: pytest could not write its cache under `.pytest_cache` due local filesystem permissions, but the tests themselves passed.

## Risks And Follow-ups

- `RuleRepository.list_for_tenant()` now reconstructs lightweight rules from the summary artifact for compatibility, but these reconstructed items intentionally do not carry full query payloads because the export artifact is summary-only.
- If a future workflow needs both summary and per-rule rendered documents, that should likely become a separate command or an explicit export mode instead of overloading `export-rules`.

## Assumptions

- The primary purpose of `export-rules` is export visibility and deployment scope reporting, not storing full per-rule SIEM execution documents in the artifact layer.
