# Request Summary

Update the current `gen-artifact` render flow so it no longer depends on
`legacy` execution inputs and so hardcoded query fields are rendered through
the repository's two-layer field contract:

`source rule field -> canonical field -> tenant SIEM field`

# Business Definition

- Business goal: render tenant artifacts from current repository contracts only,
  without runtime dependency on legacy execution paths or legacy field concepts.
- User or operator outcome: `gen-artifact` writes queries that use the tenant's
  actual SIEM field names and only renders targets whose field bindings truly
  satisfy the hardcoded query.
- Entry command or trigger: `python project-root/main.py gen-artifact --tenant-id <tenant>`
- Main input data and output artifact:
  - Inputs: `rules/`, `mappings/detections/`, `tenants/<tenant>/bindings/*`,
    `execution/<siem>/`, and tenant execution overrides.
  - Outputs: `artifacts/<tenant>/tenant-rules/` and
    `tenants/<tenant>/deployments/rule-deployments.yaml`
- Affected flow steps:
  1. build app dependencies
  2. flatten rule payloads
  3. resolve detection field mapping
  4. validate target field coverage
  5. rewrite hardcoded query fields
  6. load execution metadata from `execution/`
  7. write artifacts and deployment manifest
- Correct ownership layer:
  - `app/services`: export payload enrichment and query-target resolution
  - `infrastructure/file_loader`: detection field mapping and execution config loading
  - `interfaces` / `main`: dependency wiring
- Validation plan:
  - focused pytest on export and repository flow
  - live `gen-artifact` run on tenant `demo`
- Log file path:
  - `docs/note/logs/code/2026-03-30-gen-artifact-field-mapping-and-execution-path.md`

# Function Flow Summary

1. `main.build_app()` now wires `ExecutionConfigLoader` to `execution/` and
   injects a new detection field mapping loader rooted at
   `mappings/detections/`.
2. `ExportService.export_rules()` includes `fields` and `source_path` in the
   flat payload so downstream services can resolve the correct shared mapping.
3. `RuleDeploymentBuilder` selects the best matching detection mapping from
   `mappings/detections/`, resolves canonical-to-tenant field bindings for the
   candidate device/dataset, and rejects targets whose hardcoded query cannot be
   rendered through both mapping layers.
4. The same builder rewrites hardcoded query field tokens to tenant SIEM field
   names while preserving query aliases and derived fields such as `as Time` or
   aggregate `count`.
5. Artifact writing remains unchanged structurally, but saved queries now carry
   tenant field names and the output no longer leaks internal `_field_bindings`
   metadata.

# Files Changed

- `project-root/main.py`
- `project-root/app/services/export_service.py`
- `project-root/app/services/rule_deployment_builder.py`
- `project-root/infrastructure/file_loader/detection_field_mapping_loader.py`
- `project-root/tests/test_export_rules.py`
- `docs/note/logs/code/2026-03-30-gen-artifact-field-mapping-and-execution-path.md`

# Tests Run

- `python -m pytest tests/test_export_rules.py -q` from `project-root/`
- `python -m pytest tests/test_folder_architecture.py tests/test_export_rules.py -q` from `project-root/`
- `python project-root/main.py gen-artifact --tenant-id demo`

# Risks, Follow-Ups, And Assumptions

- The query token rewrite is intentionally narrow and tailored to the current
  hardcoded Splunk query style in the repository. If future rules introduce more
  complex SPL syntax, the token scanner may need to grow with new reserved words
  or parsing rules.
- Query field coverage is based on fields actually referenced in the hardcoded
  query, not every field listed under `rule.fields`, because some rules carry
  extra review/output fields that are not executed in the query path.
- Current execution input now comes from `execution/<siem>/...`; the old
  `legacy/execution` files remain on disk but are no longer used by this flow.
