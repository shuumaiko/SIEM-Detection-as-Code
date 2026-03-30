# Code Log: Split Multi-Logsource Artifacts By Device

## Request Summary

When one source rule matches multiple tenant logsources, generate multiple rendered rules instead of one shared artifact. Each artifact should clearly show the device it uses, and the artifact filename should include that target device context.

## Business Definition

- Goal: avoid ambiguous multi-device artifacts by materializing one deployable rule per resolved ingest target.
- User outcome: antivirus rules that match both `eset-ra` and `mcafee-epo` render into separate artifacts and deployment entries, each with a device-specific display name and target context.
- Entry command: `python project-root/main.py gen-artifact --tenant-id <tenant>`.
- Main input: source rules under `rules/`, tenant logsource and ingest bindings under `tenants/`, and execution config under `legacy/execution/`.
- Main output artifact: one file per rendered target variant under `artifacts/<tenant>/tenant-rules/`, with filenames suffixed by `device_id` and `dataset_id` for split variants.
- Affected flow steps:
  1. CLI dispatch to `gen-artifact`
  2. export use case orchestration
  3. deployment builder expands one source rule into multiple target-specific rendered rules
  4. artifact service writes unique filenames and preserves source rule metadata
  5. tenant deployment manifest stores one entry per rendered variant
- Ownership layers:
  - `app/services/rule_deployment_builder.py`
  - `app/services/rule_artifact_service.py`
  - `tests/test_export_rules.py`
- Validation plan: targeted pytest for export flow, then rerun `gen-artifact` for tenant `lab`.
- Log file path: `docs/note/logs/code/2026-03-29-split-multi-logsource-artifacts-by-device.md`.

## Function Flow Summary

1. `RuleDeploymentBuilder.build()` still resolves ingest targets from tenant config, but now expands multi-target mappings into one rendered rule per target.
2. Each split variant gets:
   - a target-scoped rendered rule ID
   - a prefixed display name from its single `device_id`
   - direct `device_id` and `dataset_id` fields in the final target payload
3. `RuleArtifactService.build_artifacts()` now reads `source_rule_id` for lookup, writes the rendered rule ID into the artifact document, and appends a filename suffix such as `__eset-ra__eset-ra-alerts` for split variants.
4. The deployment manifest records one deployment entry per rendered variant, which keeps per-device deploy behavior visible and configurable.

## Files Changed

- `project-root/app/services/rule_deployment_builder.py`
- `project-root/app/services/rule_artifact_service.py`
- `project-root/tests/test_export_rules.py`

## Tests Run

- Pending after implementation in this log entry.

## Risks And Follow-Ups

- Existing deployment manifests will be regenerated with new variant-scoped rule IDs for any source rule that resolves to multiple tenant targets.
- If the team wants variant IDs to follow a stricter schema later, that can be normalized in a dedicated compatibility pass.
