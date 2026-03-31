# Gen-Artifact Unknown Logsource Summary Review

## Request Summary

Review `gen-artifact` output in `gen-artifact-output.txt` for tenant `demo` where one `deployed_logsources` entry shows `category/product/service: unknown` but a rule is still generated.

## Review Scenario

- Tenant: `demo`
- SIEM: `splunk`
- Entry command: `python project-root/main.py gen-artifact --tenant-id demo`
- Expected behavior under review: determine whether rules with `unknown` logsource metadata should have been dropped from artifact output
- Relevant layers: `rules/`, `tenants/demo/`, `project-root/app/usecases/export_rules.py`, `project-root/app/services/rule_deployment_builder.py`, generated artifacts under `artifacts/demo/splunk/`
- Log path: `log/2026-03-31/deployment-flow-reviewer/gen-artifact-unknown-logsource-summary.md`

## Commands Run

- `python project-root/main.py gen-artifact --tenant-id demo`
- `python -m pytest tests/test_export_rules.py -q` from `project-root/`

## Source Files Inspected

- `gen-artifact-output.txt`
- `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`
- `tenants/demo/logsources/logsource_checkpoint_fw.yaml`
- `tenants/demo/bindings/ingest/binding_checkpoint_fw.yaml`
- `tenants/demo/deployments/rule-deployments.yaml`
- `project-root/infrastructure/repositories/file_rule_repository.py`
- `project-root/app/services/rule_deployment_builder.py`
- `project-root/app/usecases/export_rules.py`

## Findings

1. The `unknown/unknown/unknown` summary entry is produced by a real rendered rule, not by a rule with no target.
   - Evidence: `gen-artifact` rerun still returns `generated_artifact_count: 7` and includes one `deployed_logsources` rollup with `unknown` labels and `device_ids: ["checkpoint-fw"]`, `dataset_ids: ["traffic"]`.
   - Evidence: generated artifact `artifacts/demo/splunk/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml` exists for rule `77f0e02f-ee74-45ab-8e02-921246687a12`.

2. The source analyst rule has a Splunk query but does not declare `logsource.category`, `logsource.product`, or `logsource.service`.
   - Evidence: `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml` contains `x_query.splunk` but no `logsource` block.

3. The render pipeline defaults missing source logsource metadata to `unknown`, then still allows that rule to match tenant devices and datasets as wildcards.
   - Evidence: `project-root/infrastructure/repositories/file_rule_repository.py` sets `category=logsource.get("category", data.get("category", "unknown"))`.
   - Evidence: `project-root/app/services/rule_deployment_builder.py` treats `rule_product in {"", "any", "generic", "unknown"}` as match-all for devices and skips category/service filtering when the rule value is `unknown`.
   - Result: the analyst rule resolves to `checkpoint-fw` / `traffic` and is rendered into artifact output.

4. The CLI summary groups rendered rules by raw rule metadata, not by resolved tenant dataset metadata.
   - Evidence: `project-root/app/usecases/export_rules.py` builds the `deployed_logsources` key from `item.get("category")`, `item.get("product")`, and `item.get("service")`, defaulting each missing value to `unknown`.
   - Impact: the summary can show `unknown/unknown/unknown` even when the final target is a concrete tenant dataset with known `device_id`, `dataset_id`, `index`, and `sourcetype`.

## Root-Cause Classification

`project-root` code-path issue, specifically a summary/reporting mismatch combined with permissive wildcard matching for missing logsource metadata.

## Verification Summary

- Confirmed by rerunning `gen-artifact` for `demo`.
- Confirmed the rendered artifact exists for the `unknown` summary bucket.
- Confirmed current focused tests pass from `project-root/`.
- This review did not modify source files.

## Project-Root Code Review

`project-root-code-reviewer` was used for the code-path inspection. See:

- `log/2026-03-31/project-root-code-reviewer/gen-artifact-unknown-logsource-summary.md`
