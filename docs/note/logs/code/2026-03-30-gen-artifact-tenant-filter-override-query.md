# Gen-Artifact Tenant Filter Override Query

## Request Summary

Update the hardcoded-query render flow so it reads tenant filter overrides from `tenants/<tenant>/overrides/filter/` and replaces the source hardcoded query before tenant field mapping runs.

## Business Definition

- Business goal: let tenant-specific filter overrides tune the hardcoded query without forking the source semantic rule.
- Operator outcome: when a tenant filter override provides `query_modifiers.<siem>.search_query`, `gen-artifact` uses that query and still rewrites its fields through the normal source-to-canonical-to-tenant mapping flow.
- Entry command: `python project-root/main.py gen-artifact --tenant-id demo`
- Main input and output: source rules in `rules/`, tenant overrides in `tenants/<tenant>/overrides/filter/`, and rendered artifacts in `artifacts/<tenant>/<siem>/`.
- Affected flow steps: main app wiring, rule deployment builder query preparation, tenant filter override loading, and export regression tests.
- Correct ownership layer: query override file parsing belongs in `infrastructure/file_loader`, while pre-field-mapping query substitution belongs in `app/services/rule_deployment_builder.py`.
- Validation plan: run targeted export tests and execute the CLI once for `demo`.
- Log file path: `docs/note/logs/code/2026-03-30-gen-artifact-tenant-filter-override-query.md`

## Function Flow Summary

1. `main.build_app()` now wires a tenant filter override loader from `tenants/`.
2. `ExportRulesUseCase.prepare_export()` still flattens source rules into hardcoded-query payloads.
3. `RuleDeploymentBuilder.build()` now checks `tenants/<tenant>/overrides/filter/**/*.filter.yaml|yml` for a matching rule before resolving ingest targets.
4. If a matching override contains `query_modifiers.<siem>.search_query`, the builder replaces `search_query` in the flat payload.
5. The existing query field rewrite logic then maps the overridden query through source fields, canonical fields, and tenant SIEM fields.
6. Tests verify that an overridden query using source-rule fields is transformed into tenant field names in the final artifact.

## Files Changed

- `project-root/infrastructure/file_loader/tenant_filter_override_loader.py`
- `project-root/app/services/rule_deployment_builder.py`
- `project-root/main.py`
- `project-root/tests/test_export_rules.py`
- `docs/note/logs/code/2026-03-30-gen-artifact-tenant-filter-override-query.md`

## Tests Run

- `python -m pytest tests/test_export_rules.py tests/test_rule_deployment_builder.py -q`
- `python main.py gen-artifact --tenant-id demo`
- `python main.py gen-artifact --tenant-id lab`

## Risks / Notes

- The current implementation intentionally uses only `query_modifiers.<siem>.search_query` from tenant filter overrides for the hardcoded-query flow.
- Richer semantic processing of `detection_filters` and `append_condition` remains out of scope for this fix.
