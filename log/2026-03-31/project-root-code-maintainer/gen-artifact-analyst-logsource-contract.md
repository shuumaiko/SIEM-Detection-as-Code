# Gen-Artifact Analyst Logsource Contract

## Request Summary

Implement the chosen analyst-rule flow:

- add `logsource` to current analyst rules based on their referenced base rule
- update the `merge-rule-into-base` skill so new analyst rules also carry inherited `logsource`
- change `project-root` so the hardcoded-query flow treats analyst `logsource` as explicit contract instead of deriving it at runtime

## Business Definition

- Business goal: make analyst rules carry their own deploy scope so the hardcoded-query flow can remain an execution adapter and later be replaced by the standard render flow without changing target resolution contracts
- User or operator outcome: analyst rules render only when they declare explicit `logsource`, and generated summaries use that real scope instead of falling back to `unknown`
- Entry command or trigger:
  - `python main.py gen-artifact --tenant-id <tenant>`
  - `python main.py validate-rules --all`
- Main input data and output artifact:
  - Inputs: `rules/analysts/**`, `rules/detections/**`, schema validation rules, and tenant context
  - Outputs: renderable analyst payloads in `project-root`, validation results, updated tenant artifacts, and updated skill guidance
- Affected flow steps:
  1. analyst rule authoring contract
  2. hardcoded-query export payload construction
  3. rule-format validation
  4. regression coverage for analyst rules without explicit `logsource`
- Correct ownership layer:
  - `app/services`: enforce analyst logsource contract during export
  - `app/services`: validate repository-specific analyst contract in `validate-rules`
  - `tests`: regression coverage near export and validation flows
- Validation plan:
  - run focused pytest for `test_export_rules.py` and `test_rule_format_validator.py`
  - run `python main.py validate-rules --all`
  - rerun `python main.py gen-artifact --tenant-id demo`
- Log file path:
  - `log/2026-03-31/project-root-code-maintainer/gen-artifact-analyst-logsource-contract.md`

## Function Flow Summary

1. `interfaces/cli.py` still dispatches `gen-artifact` and `validate-rules` without behavior changes.
2. `ExportRulesUseCase.prepare_export()` still coordinates source rule loading, flattening, target resolution, artifact build, and deployment manifest refresh.
3. `ExportService.export_rules()` now requires analyst rules to provide complete `logsource` metadata and no longer derives analyst scope from referenced base rules at runtime.
4. `RuleDeploymentBuilder.build()` stays responsible for target resolution and query rewrite, but now receives explicit analyst scope from the source rule contract.
5. `RuleFormatValidator.validate()` now enforces the repository contract that analyst rules must declare `logsource.category`, `logsource.product`, and `logsource.service`.
6. Regression tests verify that missing analyst `logsource` fails closed in both export and validation flows.

## Files Changed

- `project-root/app/services/export_service.py`
- `project-root/app/services/rule_format_validator.py`
- `project-root/tests/test_export_rules.py`
- `project-root/tests/test_rule_format_validator.py`
- `rules/analysts/application/splunk/base/siem_no_log_from_host_over_24h.yaml`
- `rules/analysts/application/splunk/base/siem_no_log_from_source_over_1h.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_blocked_per_host.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_to_multiple_hosts.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_rdp_port_3389_blocked_per_host.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_rdp_port_3389_external_allowed.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_rdp_port_3389_to_multiple_hosts.yaml`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_ssh_port_22_external_allowed.yaml`
- `rules/analysts/network/firewall/base/net_fw_request_reached_over_threshold.yaml`
- `.codex/skills/merge-rule-into-base/SKILL.md`

## Tests Run

- `python -m pytest tests/test_export_rules.py tests/test_rule_format_validator.py -q` from `project-root/`
- `python main.py validate-rules --all` from `project-root/`
- `python main.py gen-artifact --tenant-id demo` from `project-root/`

## Risks / Follow-Ups / Assumptions

- This change intentionally makes analyst logsource explicit and fail-closed. Future analyst rules without `logsource` will now be rejected by validation and skipped by export.
- The current repository only needed single-base inheritance to populate existing analyst rules. If future analyst rules reference multiple base rules with different scopes, authoring guidance should require an explicit analyst `logsource` chosen by the rule author rather than runtime merging.
- The `gen-artifact` rerun updated tracked artifacts for tenant `demo`; those generated diffs are expected review evidence for this task.
