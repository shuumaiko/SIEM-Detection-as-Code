# Gen-Artifact SIEM Output Root

## Request Summary

Change `gen-artifact` so each tenant export writes under `artifacts/<tenant-id>/<siem-id>/...` instead of `artifacts/<tenant-id>/tenant-rules/...`, while still removing the previously generated tree for the current tenant/SIEM pair before re-rendering.

## Business Definition

- Business goal: separate generated artifact trees by tenant and SIEM instead of one shared `tenant-rules` root.
- Operator outcome: `gen-artifact --tenant-id <id>` rewrites only that tenant's active SIEM artifact tree and returns the new root in the CLI summary.
- Entry command: `python project-root/main.py gen-artifact --tenant-id demo`
- Main input and output: tenant config under `tenants/<tenant-id>/` and generated artifacts under `artifacts/<tenant-id>/<siem-id>/`.
- Affected flow steps: export use case summary, rule repository artifact save/read/sync path resolution, repository-facing save service signature, and regression tests.
- Correct ownership layer: `app/usecases`, `app/services`, `domain/repositories`, `infrastructure/repositories`, and targeted tests.
- Validation plan: run focused `pytest` coverage for export/repository flows and execute the CLI command for tenant `demo`.
- Log file path: `docs/note/logs/code/2026-03-30-gen-artifact-siem-output-root.md`

## Function Flow Summary

1. CLI still enters through `main.py` and dispatches `gen-artifact` into `ExportRulesUseCase`.
2. `ExportRulesUseCase.prepare_export()` still builds resolved rules and artifacts, but now reports `artifact_root` as `artifacts/<tenant>/<siem-id>`.
3. `RuleService.save_rendered_rules_for_tenant()` now passes the full `Tenant` context so persistence can scope writes by both tenant and SIEM.
4. `FileRuleRepository.save_rendered_for_tenant()` deletes and rewrites the current `artifacts/<tenant>/<siem-id>/` tree.
5. `FileRuleRepository.list_for_tenant()` and `sync_artifact_enabled_states()` now resolve the current tenant/SIEM artifact root first, while keeping read compatibility with older `tenant-rules` trees.
6. Regression tests verify the new output path and summary value.

## Files Changed

- `project-root/domain/repositories/rule_repository.py`
- `project-root/app/services/rule_service.py`
- `project-root/app/usecases/export_rules.py`
- `project-root/app/services/rule_artifact_service.py`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/tests/test_folder_architecture.py`
- `project-root/tests/test_export_rules.py`
- `docs/note/logs/code/2026-03-30-gen-artifact-siem-output-root.md`

## Tests Run

- `python -m pytest tests/test_folder_architecture.py tests/test_export_rules.py -q`
- `python main.py gen-artifact --tenant-id demo`

## Risks / Notes

- Read flows still support older `artifacts/<tenant-id>/tenant-rules/` trees for compatibility, but new writes only target `artifacts/<tenant-id>/<siem-id>/`.
- Existing older artifact directories are not rewritten automatically; they simply stop being the primary read target once the SIEM-specific tree exists.
