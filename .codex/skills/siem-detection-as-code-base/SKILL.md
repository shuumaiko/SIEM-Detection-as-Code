---
name: siem-detection-as-code-base
description: Work inside the SIEM-Detection-as-Code repository with the repository's layered model for rules, mappings, tenants, artifacts, and the Python engine under project-root. Use when Codex needs to create or update detection rules, tenant config, ingest or field bindings, deployment manifests, validation flows, or architecture-aligned documentation for this repo.
---

# SIEM Detection as Code Base

Use this skill to stay aligned with the repository's multi-tenant Detection-as-Code architecture.

## Start Here

Read only the files needed for the requested change.

- Read `README.en.md` for the high-level model when the task spans multiple layers.
- Read `docs/architecture/rules-relationship.md` when the task involves creating or updating rules, rule types, or the relationship between rules and other layers.
- Read `docs/architecture/tenants-relationship.md` when changing tenant structure, bindings, filters, or deployments.
- Read `docs/architecture/mappings-relationship.md` when changing canonical fields or detection mappings.
- Read `docs/architecture/rule-rendering-flows.md` when the task touches rendering, hardcoded queries, or execution layering.
- Read `project-root/interfaces/cli.py` and `project-root/tests/` when the task affects validation or runtime behavior.
- Read `references/repo-map.md` in this skill for a compact repo-specific checklist.

## Follow The Layer Boundaries

- Keep detection intent in `rules/`.
- Keep normalized field contracts in `mappings/`.
- Keep tenant-specific reality in `tenants/`.
- Treat `artifacts/` as rendered output, not the primary place for manual edits, unless the task is explicitly about generated artifacts or backward-compatibility fixtures.
- Keep engine and validation logic in `project-root/`.

## Choose The Correct Edit Target

- Edit `rules/detections/` when changing reusable detection content.
- Edit `tenants/<tenant>/devices/`, `logsources/`, `bindings/ingest/`, `bindings/fields/`, `filters/`, or `deployments/` when changing tenant-specific deployment context.
- Edit `schema/` and `project-root/app/services/` together when changing validation contracts.
- Edit tests in `project-root/tests/` whenever behavior, structure, or validation expectations change.

## Work With Rules Carefully

- Preserve the rule's semantic intent unless the user asks to redesign it.
- Keep `rule_type`, taxonomy, and folder placement consistent with the architecture docs.
- Prefer updating supporting mappings or tenant bindings instead of hardcoding tenant-specific assumptions into a reusable base rule.
- Treat `x_query` or other hardcoded SIEM query blocks as execution artifacts that may still be valid in the current transition state.

## Work With Tenant Data Carefully

- Keep `tenant_id`, `device_id`, `dataset_id`, and `siem_id` consistent across related files.
- Ensure `bindings/ingest/*.yaml` dataset entries match the datasets declared in the corresponding logsource.
- Ensure field bindings map canonical fields to the actual tenant SIEM fields instead of inventing new canonical names ad hoc.
- Update deployment manifests when a tenant should start or stop receiving a rule.

## Validate Before Finishing

Run the smallest useful verification after edits.

- Run `python project-root/main.py validate-tenant --tenant-id <tenant>` after tenant or binding changes.
- Run `python project-root/main.py validate-rules --all` after rule or schema changes when broad validation is reasonable.
- Run focused tests in `project-root/tests/` when changing engine behavior.
- Mention clearly if validation could not be run.

## Keep The Skill Lean

- Prefer referencing repo docs instead of copying long explanations into new files.
- Add new reference material to this skill only when it captures stable repo-specific conventions that Codex would otherwise need to rediscover repeatedly.
