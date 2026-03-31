# Request Summary

- Restrict tenant rule export so only rules with `status: stable` are rendered into artifacts.

# Business Definition

- Business goal: prevent non-production rule states from being exported into tenant-ready artifacts.
- User or operator outcome: `export-rules` ignores rules marked `test`, `experimental`, `deprecated`, or `unsupported`.
- Entry command or trigger: `python project-root/main.py export-rules --tenant-id <tenant>`
- Main input data and output artifact: source rule YAML under `rules/detections/` and rendered tenant artifacts plus deployment manifest.
- Affected flow steps: source rule scan, render candidate selection, export test fixtures.
- Correct ownership layer: `infrastructure/repositories` for source-rule selection.
- Validation plan: run focused export pipeline test under `project-root/tests/test_export_rules.py`.
- Log file path: `log/2026-03-29/project-root-code-maintainer/export-only-stable-rules.md`

# Function Flow Summary

- Entry point: `project-root/app/usecases/export_rules.py::execute`
- Orchestration: `RuleService.load_render_candidates()` delegates to `FileRuleRepository.list_render_candidates()`
- Business logic: source rules are filtered to `status == stable` before SIEM query extraction and render target mapping
- Side effects: tenant artifacts and deployment manifests contain only stable rules
- Failure points: repositories with no stable source rules will export nothing until at least one rule is promoted

# Files Changed

- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/tests/test_export_rules.py`
- `log/2026-03-29/project-root-code-maintainer/export-only-stable-rules.md`

# Tests Run

- `..\ .venv\Scripts\python.exe -m pytest tests/test_export_rules.py -q` from `project-root/`

# Risks And Follow-ups

- The current repository data shown during implementation contains only `status: test` rules in `rules/detections/`, so real exports may now be empty until stable rules are introduced.

