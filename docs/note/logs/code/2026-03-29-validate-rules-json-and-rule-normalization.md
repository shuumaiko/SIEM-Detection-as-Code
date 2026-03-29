# Request Summary

- Normalize rule files that started failing after tightening the detection schema.
- Make `validate-rules` output easier to read and redirect into files.

# Business Definition

- Business goal: restore a usable validation gate for current detection rules and make validator output operator-friendly.
- User or operator outcome: running `validate-rules` produces readable JSON output, and the repository's current detection rules align better with the tightened schema contract.
- Entry command or trigger: `python project-root/main.py validate-rules --all`
- Main input data and output artifact: rule YAML files under `rules/detections/` and JSON-formatted validation results on stdout.
- Affected flow steps: CLI command dispatch, validator result presentation, schema-driven rule validation.
- Correct ownership layer: `interfaces` for output formatting, `rules/` for normalized detection content.
- Validation plan: run focused CLI/output tests and rerun `validate-rules --all`.
- Log file path: `docs/note/logs/code/2026-03-29-validate-rules-json-and-rule-normalization.md`

# Function Flow Summary

- Entry point: `project-root/interfaces/cli.py::run_cli`
- Orchestration: `ValidateRuleFormatUseCase.execute()`
- Business logic: `RuleFormatValidator.validate()`
- Side effects: formatted stdout that can be redirected to `.txt` or `.json`
- Failure points: malformed rule YAML, schema mismatch, missing required detection metadata

# Files Changed

- `rules/detections/network/firewall/net_firewall_cleartext_protocols.yml`
- `rules/detections/network/firewall/base/fw_connection_port_23.yaml`
- `rules/detections/category/antivirus/av_relevant_files.yml`
- `project-root/interfaces/cli.py`
- `project-root/tests/test_cli.py`

# Tests Run

- `.\.venv\Scripts\python.exe -m pytest tests/test_rule_schema_contract.py -q`
- `.\.venv\Scripts\python.exe -m pytest project-root/tests/test_cli.py -q`
- `.\.venv\Scripts\python.exe project-root/main.py validate-rules --all`

# Risks And Follow-ups

- The added `x_query` blocks keep the current transition model alive, but they are still hand-maintained query artifacts rather than generated output.
- Some legacy or non-normalized rules under `rules/legacy/` and `rules/deprecated/` remain outside the current validator scope.
