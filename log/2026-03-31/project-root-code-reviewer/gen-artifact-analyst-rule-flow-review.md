# Project-Root Review: Gen-Artifact Analyst Rule Flow

## Request Summary

Review whether `gen-artifact` currently handles analyst rules according to this intended flow:

1. Open analyst rule and check analyst status.
2. Check the base rule(s) referenced by the analyst rule.
3. Check referenced base rule status and only allow analyst deployment when the base rule is `stable`.
4. Reuse the base rule logsource for the analyst rule.
5. Treat the hardcoded-query flow as query override only.

If the code does not follow that principle, review whether the principle is suitable for implementation in this repository.

## Review Scope

- Goal: inspect the real `gen-artifact` path for analyst rules and compare it to the intended dependency flow above
- Suspected risk: analyst rules may deploy independently from referenced base rules, creating artifacts with mismatched or missing semantic context
- Entry workflow: `python project-root/main.py gen-artifact --tenant-id demo`
- Main files inspected:
  - `project-root/interfaces/cli.py`
  - `project-root/app/usecases/export_rules.py`
  - `project-root/app/services/export_service.py`
  - `project-root/infrastructure/repositories/file_rule_repository.py`
  - `project-root/app/services/rule_deployment_builder.py`
  - `project-root/tests/test_export_rules.py`
  - `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`
  - `rules/detections/network/firewall/base/fw_connection_port_21.yml`
- Log path: `log/2026-03-31/project-root-code-reviewer/gen-artifact-analyst-rule-flow-review.md`

## Commands Run

- `python project-root/main.py gen-artifact --tenant-id demo`
- `python -m pytest tests/test_export_rules.py -q` from `project-root/`

## Findings

1. The current code does not enforce base-rule status as a deployment prerequisite for analyst rules.
   - `project-root/infrastructure/repositories/file_rule_repository.py:101-117` filters render candidates purely by each rule document's own `status == stable`.
   - `project-root/app/services/export_service.py:23-49` exports any non-`base` rule that survived candidate loading.
   - There is no check that the analyst's referenced base rule exists in the candidate set, is `stable`, or is even renderable.
   - Concrete evidence: analyst rule `77f0e02f-ee74-45ab-8e02-921246687a12` is `stable` in `rules/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml`, while its referenced base rule `fw_connection_port_21` is `status: test` in `rules/detections/network/firewall/base/fw_connection_port_21.yml`. Despite that, `gen-artifact --tenant-id demo` still generates one analyst artifact and reports `rule_count_by_type.analyst = 1`.

2. The current code only derives analyst logsource opportunistically from referenced rules that are already present in the loaded candidate set.
   - `project-root/app/services/export_service.py:53-105` builds `rules_by_name` from the already loaded `rules` list, then `_derive_analyst_logsource()` looks up correlation references by `name`.
   - Because candidate loading excludes non-`stable` rules, a referenced base rule with `status: test` is absent from `rules_by_name`.
   - Result: analyst logsource inheritance silently fails when the base rule is not loaded, rather than explicitly blocking deployment.

3. When analyst logsource inheritance fails, the pipeline can still deploy the analyst rule through wildcard target resolution, which violates the intended "base logsource drives analyst deployment" principle.
   - The stable analyst FTP rule has no explicit `logsource` block, and its base rule is not loadable into `rules_by_name` because the base status is `test`.
   - Downstream, `rule_deployment_builder.py` treats missing or `unknown` product/category/service as permissive matching, so the analyst rule still resolves to tenant target `checkpoint-fw` / `traffic`.
   - Evidence: `gen-artifact --tenant-id demo` produces a rendered artifact under `artifacts/demo/splunk/analysts/network/firewall/base/net_fw_possible_scan_ftp_port_21_external_allowed.yaml` and a summary bucket with `category/product/service = unknown`.

4. Existing tests cover that analyst rules can render, but they do not cover the dependency contract you described.
   - `project-root/tests/test_export_rules.py` asserts that an analyst artifact is generated in the happy path.
   - There is no focused test asserting:
     - analyst rule must be blocked when a referenced base rule is not `stable`
     - analyst rule must inherit logsource from referenced base rule(s)
     - analyst rule must fail closed when that inheritance cannot be resolved

## Open Questions Or Assumptions

- This review assumes `correlation.rules` is intended to reference semantic base or detection rule names that are authoritative for logsource scope.
- This review also assumes the repository wants analyst rules to remain semantically attached to those referenced rules, not behave as independently scoped hardcoded search rules.

## Verification Summary

- Re-ran `gen-artifact` for tenant `demo` and confirmed one analyst rule is currently deployed.
- Verified the referenced base rule for that analyst example is `status: test`, not `stable`.
- Ran `python -m pytest tests/test_export_rules.py -q` from `project-root/`; result: `5 passed`.
- This review did not modify source files.

## Suitability Review Of The Proposed Principle

The proposed principle is suitable for this repository and is more consistent with the architecture than the current implementation, with two practical notes:

1. It fits the repository's semantic layering.
   - Analyst rules in `rules/analysts/` are described as correlation or higher-level content.
   - Base and detection rules in `rules/detections/` hold the semantic detection scope and logsource contract.
   - Requiring analyst deployment to depend on referenced stable rules preserves that separation instead of letting analyst rules become free-standing hardcoded searches.

2. It matches the current file design better than the current runtime behavior.
   - Analyst rules already reference upstream rules by semantic name in `correlation.rules`.
   - Reusing the referenced rule logsource as the analyst logsource follows the authoring model already present in the YAML content.

3. It should be implemented as "fail closed" when dependencies cannot be resolved.
   - If an analyst references one or more rules and the referenced rules are missing, non-stable, or have conflicting logsource scopes, the analyst should not be deployed.
   - This is safer than today's fallback path, which can still map to tenant targets with `unknown` scope.

4. The only caveat is multi-reference analysts.
   - When an analyst references multiple rules, the implementation should define whether all referenced rules must be `stable`, and whether their logsource must be identical or reducible to one shared scope.
   - If no single shared scope exists, deployment should be blocked or require an explicit analyst `logsource`.

## Conclusion

The current code does not follow the intended analyst-rule flow. It partially attempts logsource inheritance, but it does not enforce referenced base-rule stability, and it can still deploy analyst rules when inheritance fails. The principle you proposed is appropriate for this repository and would produce behavior that is safer and more architecture-aligned than the current hardcoded-query fallback.
