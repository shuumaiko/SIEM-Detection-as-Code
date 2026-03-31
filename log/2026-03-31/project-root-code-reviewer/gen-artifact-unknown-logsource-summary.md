# Project-Root Review: Unknown Logsource Summary Still Generates Rule

## Request Summary

Review why `python project-root/main.py gen-artifact --tenant-id demo` reports one `deployed_logsources` entry with `category/product/service = unknown` while still generating an artifacted rule.

## Review Scope

- Goal: determine whether the rule should have been dropped or whether the summary is misleading
- Suspected risk: summary implies unresolved logsource, but render pipeline may still deploy the rule
- Entry workflow: `gen-artifact`
- Main files inspected:
  - `project-root/app/usecases/export_rules.py`
  - `project-root/app/services/rule_deployment_builder.py`
  - `project-root/infrastructure/repositories/file_rule_repository.py`
  - `project-root/tests/test_export_rules.py`
- Log path: `log/2026-03-31/project-root-code-reviewer/gen-artifact-unknown-logsource-summary.md`

## Commands Run

- `python project-root/main.py gen-artifact --tenant-id demo`
- `python -m pytest tests/test_export_rules.py -q` from `project-root/`

## Findings

1. Summary labeling is sourced from rule metadata, not resolved target metadata.
   - `project-root/app/usecases/export_rules.py` uses `item.get("category"|"product"|"service")` for the `deployed_logsources` rollup key and defaults each missing value to `unknown`.
   - Because the summary key ignores the resolved tenant dataset metadata, a rendered rule can be counted under `unknown` even after target resolution succeeds.

2. Missing logsource metadata is intentionally treated as wildcard-like during target resolution.
   - `project-root/infrastructure/repositories/file_rule_repository.py` defaults missing category to `unknown` when loading render candidates.
   - `project-root/app/services/rule_deployment_builder.py` allows `unknown` product to match any device and bypasses category/service checks when those values are `unknown`.
   - Net effect: a stable rule with `x_query` but no `logsource` block can still deploy if field bindings and ingest bindings are available.

3. The concrete rule behind the `unknown` summary bucket is `77f0e02f-ee74-45ab-8e02-921246687a12`.
   - Source file: `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`
   - Rendered artifact: `artifacts/demo/splunk/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`
   - Resolved target in artifact: `device_id: checkpoint-fw`, `dataset_id: traffic`, `index: checkpoint`, `sourcetype: cp_log`

## Evidence Notes

- The source analyst rule has `x_query.splunk` and required fields, but no `logsource` block.
- Tenant data for `checkpoint-fw` exposes dataset `traffic` with ingest binding `checkpoint/cp_log`.
- Focused tests pass and currently do not assert that missing rule logsource metadata should block rendering.

## Generated Output Touched

- `gen-artifact` rewrote current tenant artifacts and deployment manifest as part of the observed workflow.

## Assumptions

- Repository intent remains: rules without deployable targets should be dropped, but rules with missing source logsource metadata are not currently considered targetless if wildcard matching still finds a tenant dataset.

## Conclusion

This is a behavior/contract mismatch in `project-root`, not stale artifact state. The pipeline currently permits rendering for rules whose source logsource metadata is missing and only surfaces that gap in the summary as `unknown`.

## Note

This review did not modify source files.
