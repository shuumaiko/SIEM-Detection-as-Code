# Request Summary

- Add `<device_id> - ` as a prefix for generated tenant rules.

# Business Definition

- Business goal: make rendered tenant rules easier to identify by their source device context.
- User or operator outcome: exported artifacts and deployment display names clearly show the resolved tenant `device_id`.
- Entry command or trigger: `python project-root/main.py export-rules --tenant-id lab`
- Main input data and output artifact: source rules, tenant device/logsource/binding metadata, and rendered rule artifacts plus deployment manifest.
- Affected flow steps: target resolution in deployment builder and final title rendering in artifact builder.
- Correct ownership layer: `app/services`
- Validation plan: run focused export pipeline tests.
- Log file path: `docs/note/logs/code/2026-03-29-device-id-prefix-generated-rules.md`

# Function Flow Summary

- Entry point: `project-root/app/usecases/export_rules.py::execute`
- Orchestration: export service prepares flat payload, deployment builder resolves targets, artifact service writes final document title.
- Business logic: derive one unambiguous `device_id` from `targets` or `ingest_targets`, then prefix the title and deployment display name.
- Side effects: generated artifact `title` and deployment `display_name` now include `<device_id> - `.
- Failure points: rules that map to multiple devices remain unprefixed to avoid misleading output.

# Files Changed

- `project-root/app/services/rule_artifact_service.py`
- `project-root/app/services/rule_deployment_builder.py`
- `project-root/tests/test_export_rules.py`
- `docs/note/logs/code/2026-03-29-device-id-prefix-generated-rules.md`

# Tests Run

- Planned: `.\.venv\Scripts\python.exe -m pytest project-root/tests/test_export_rules.py -q`

# Risks And Follow-ups

- Multi-device rules are intentionally left without a prefix because a single prefix would hide ambiguity.
