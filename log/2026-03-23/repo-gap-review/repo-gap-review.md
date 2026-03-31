# Repository Gap Review Notes

Date: 2026-03-23

This note records the main gaps identified during a repository review that excluded `./project-root/`.

Review scope:

- `docs/`
- `rules/`
- `mappings/`
- `execution/`
- `tenants/`
- `schema/`
- `tests/`
- `artifacts/`

Out of scope:

- `project-root/`

## 1. General reading

Based on the current architecture documents:

- `rules/` is intended to be the source of truth for semantic detection content.
- `mappings/` is intended to provide source-field to canonical-field contracts.
- `tenants/` is intended to provide tenant-specific ingest, field binding, tuning, and deployment input.
- `execution/` is intended to provide SIEM-specific execution metadata.
- `artifacts/` is intended to be rendered output, not long-term editable source content.
- `schema/` and `tests/` are intended to act as quality gates for these layers.

The review found that the target architecture is documented reasonably clearly in `docs/architecture/`, but several repository layers are still drifting apart in practice.

## 2. Main gaps identified

### 2.1. Rule schema is no longer aligned with the actual rule model

Severity: Critical

Observed mismatch:

- `schema/rules/rule_file.schema.json` defines a rule file as a two-item array with `base_rule` and `correlation_rule`.
- current rule files in `rules/` are stored as single YAML documents.
- current rule files use `rule_type`, `fields`, `level`, `falsepositives`, and `x_query`.
- current schemas do not consistently model these fields.

Concrete examples:

- `schema/rules/rule_file.schema.json` expects a multi-document array.
- `rules/detections/network/firewall/base/fw_connection_port_23.yaml` is a single document.
- `rules/analysts/network/firewall/base/net_fw_request_reached_over_threshold.yaml` is also a single document.

Additional drift:

- `schema/rules/base_rule.schema.json` requires `name`, but not every current detection rule has `name`.
- `schema/rules/base_rule.schema.json` does not model `rule_type`, `fields`, `level`, `falsepositives`, or `x_query` as first-class properties.
- `schema/rules/correlation_rule.schema.json` requires `x_splunk_es`, but current analyst rule files use `x_query`.

Impact:

- schema validation cannot be trusted as a real quality gate for current rule content.
- contributors may believe rules are structurally validated when they are not.
- future automation around validation or CI will either fail incorrectly or be bypassed.

Recommended follow-up:

- redesign rule schemas around the current single-document model.
- decide whether to have one unified rule schema with `rule_type`, or separate schemas for `detection`, `detection_base`, and `analyst`.
- explicitly model transitional `x_query` support while the generalized converter is still incomplete.

## 2.2. Deployment manifest is disconnected from the current `rules/` source of truth

Severity: High

Observed mismatch:

- `tenants/lab/deployments/rule-deployments.yaml` contains rule identifiers that do not match the current rule IDs under `rules/`.
- a cross-check against the current `rules/` layer showed that all listed deployment `rule_id` values are missing from the current non-legacy rule set used in this review.

Concrete examples:

- `tenants/lab/deployments/rule-deployments.yaml` contains many entries that do not map to any current rule object.
- several IDs also appear malformed as UUIDs, for example values containing non-hex characters.

At the same time:

- `execution/splunk/rule-overrides.yaml` references current rule IDs that do exist in `rules/`.
- `tenants/lab/overrides/execution/splunk/detection/category/antivirus/av_hacktool.execution.yaml` references a current rule ID that exists.
- `tenants/lab/overrides/filter/detections/fw_connection_port_23.filter.yaml` also references a current rule ID that exists.

Interpretation:

- execution and tenant override layers are partially aligned with the current architecture.
- deployment selection is still aligned to legacy content or legacy rendered artifacts.
- repository identity is currently split between the old and new content models.

Impact:

- render and deploy workflows cannot safely rely on `deployments/rule-deployments.yaml` as the enablement source for the current architecture.
- rule enablement, override resolution, and output generation can diverge silently.

Recommended follow-up:

- decide whether deployment manifests should target legacy artifacts or the new `rules/` layer.
- if the new `rules/` layer is the intended source of truth, rebuild deployment manifests against current rule IDs.
- add integrity checks that verify every deployment `rule_id` resolves to exactly one rule.

## 2.3. Tenant filter ownership is still ambiguous

Severity: High

Observed mismatch:

- architecture documents still describe `filters/` as a tenant input layer.
- tenant documentation also introduces `overrides/filter/` as an active path.
- the actual tenant data currently uses `overrides/filter/` rather than `filters/`.

Concrete examples:

- `docs/architecture/project-architecture.md` lists `filters/` and `overrides/` as distinct concepts.
- `docs/architecture/tenants-relationship.md` defines both `filters/` and `overrides/filter/`.
- current lab tenant filter data exists under `tenants/lab/overrides/filter/detections/fw_connection_port_23.filter.yaml`.

Impact:

- filter lookup rules are not fully deterministic from documentation alone.
- future render logic may apply the wrong search path or precedence.
- contributors do not have a single clear place to add tenant-specific detection filters.

Recommended follow-up:

- choose one primary ownership model:
  - `filters/` as the canonical tenant filter layer, or
  - `overrides/filter/` as the canonical tenant filter layer.
- document the precedence and lookup path explicitly.
- deprecate the losing path in docs and validation rules.

## 2.4. Quality gates are declared in architecture, but not implemented in practice

Severity: Medium

Observed state:

- architecture docs describe `tests/` as a quality gate for validation, smoke flow, and structure checks.
- the actual `tests/` directory currently contains only `.gitkeep`.

Impact:

- there is no practical automated protection against drift between:
  - `rules/` and schemas
  - `tenants/` and schemas
  - `deployments/` and rule identities
  - `mappings/` and field bindings
- architecture evolution can continue without any feedback loop until much later in implementation.

Recommended follow-up:

- add lightweight repository integrity tests first.
- suggested first checks:
  - every `rule_id` in deployments resolves to a rule
  - every override `rule_id` resolves to a rule
  - every binding `dataset_id` resolves to a declared logsource dataset
  - every rule file matches the active rule schema

## 2.5. Documentation quality is uneven and can mislead onboarding

Severity: Medium

Observed issues:

- `README.md` shows encoding corruption and is difficult to read in its current state.
- `tenants/README.md` contains absolute file links pointing to an external local path instead of repository-relative references.
- some documents reflect the new architecture, while some repository-level notes and readmes still expose older structure ideas.

Concrete examples:

- `README.md` contains mojibake in Vietnamese content.
- `tenants/README.md` links to `d:\My Project\SIEM-Detection\...`, which is not portable.
- `rules/legacy/README.md` still reflects older concepts such as `rule-view/` and `logsource-mapping-registry/`.

Impact:

- contributor onboarding becomes slower and less reliable.
- reviewers may follow outdated guidance and add content into the wrong layer.
- architecture drift is reinforced by inconsistent documentation.

Recommended follow-up:

- normalize file encoding for top-level docs.
- replace absolute links with repository-relative links.
- mark outdated readmes clearly as legacy, transitional, or deprecated.

## 3. Architectural interpretation

The most important pattern behind these findings is not just incomplete implementation. The repository currently has a split-brain state across data layers:

- `docs/architecture/` describes the new target model.
- `rules/`, `execution/`, and some tenant overrides partially follow the new model.
- `deployments/` and `artifacts/legacy/` still reflect older identity and content assumptions.
- `schema/` does not yet validate the current model.
- `tests/` does not yet enforce integrity across layers.

This means the project is not blocked by one missing component only. It is blocked by missing alignment between the declared source of truth layers.

## 4. Priority order for later handling

Suggested handling order:

1. Align rule schemas with the current rule file model.
2. Reconcile deployment manifests with the active `rules/` identity model.
3. Decide and document the canonical tenant filter path and precedence.
4. Add minimal integrity tests for repository-level cross references.
5. Clean up high-traffic documentation and legacy readme references.

## 5. Short conclusion

The repository already has a usable target architecture narrative, but the operational repository contracts are not yet synchronized with it.

The biggest gaps are:

- invalid or outdated schema contracts for current rule files
- deployment manifests that do not resolve against current rule identities
- unclear ownership between `filters/` and `overrides/filter/`
- missing automated integrity checks
- uneven documentation quality during the transition period
