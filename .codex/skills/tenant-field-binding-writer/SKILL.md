---
name: tenant-field-binding-writer
description: Create or update tenant field binding files under tenants/<tenant>/bindings/fields/ that map repository canonical fields to the tenant's actual SIEM fields. Use when Codex needs to identify the target device or dataset, determine the rule pack being deployed, resolve rule fields to canonical fields from mappings/, and write a minimal canonical-to-SIEM binding file from user-provided SIEM events without mapping every raw SIEM field.
---

# Tenant Field Binding Writer

Use this skill to write or revise `tenants/<tenant>/bindings/fields/*.yml` files for a specific tenant SIEM deployment.

## Start With Repo Truth

Read only the files needed for the task.

- Read `schema/tenants/field_binding.schema.json` before structural edits.
- Read `docs/architecture/tenants-relationship.md` and `docs/architecture/mappings-relationship.md` when the task spans `rules/`, `mappings/`, and `tenants/`.
- Read nearby tenant field binding files first, especially `tenants/lab/bindings/fields/checkpoint-fw.fields.yml`, to preserve the repo's live style.
- Read the target rule files and the matching mapping file under `mappings/detections/` before deciding which canonical fields must appear in the tenant binding.

## Required Inputs

Gather the minimum set of inputs before editing.

- Identify `tenant_id`.
- Identify `siem_id`.
- Identify `device_id`.
- Identify the target dataset if the binding is dataset-specific.
- Identify the rule or rule pack being deployed for that device or dataset.
- Collect the SIEM event or field sample provided by the user.

If one of these is missing, infer it from tenant files or nearby rules when safe. Otherwise ask only for the missing blocker.

## Binding Workflow

Follow this order.

1. Determine the target device, dataset, and deployment scope from the tenant structure and the rule pack that will be deployed.
2. Inspect the rule file or rule set to list only the source fields needed for detection, correlation, filtering, or useful output.
3. Locate the corresponding file under `mappings/detections/` and resolve each required rule field to its canonical field.
4. Reuse existing canonical names from repo mappings and nearby tenant bindings; do not invent new canonical fields inside tenant binding files.
5. From the user-provided SIEM event, identify the actual SIEM field names that carry those canonical meanings.
6. When multiple SIEM fields carry the same value or nearly the same meaning, choose the best physical field instead of binding all duplicates.
7. Prefer the SIEM field that appears consistently across more events of the same device or dataset, has the clearest semantic name, and is more likely to remain stable for the target content pack.
8. Write only the canonical fields that are actually needed for the target rules. Do not map the full SIEM event just because it is available.
9. Choose `default_field_mapping` when the mapping applies broadly to the device, and `datasets.<dataset>.field_mapping` when the mapping is dataset-specific.
10. Re-read the final file and verify every canonical field is justified by both the mapping layer and the SIEM event sample.

## File Shape Rules

Keep the file valid against `schema/tenants/field_binding.schema.json`.

- Keep `schema_version`, `tenant_id`, `siem_id`, and `device_id`.
- Add `description` with clear tenant, device, and scope context.
- Use `default_field_mapping` for shared bindings at the device level.
- Use `datasets.<dataset>.field_mapping` only when the field names differ for a specific dataset or when the scope is intentionally dataset-limited.
- Keep every mapping value as the exact SIEM field path or field name used by the tenant.
- Use canonical keys from the mapping layer, including repository `canonical.*` names or direct OCSF-style field references only when that is already the repository contract.

## Mapping Rules

- Treat `mappings/detections/` as the authority for canonical field selection.
- Treat the user-provided SIEM event as the authority for the tenant's physical SIEM field names.
- Prefer the smallest useful binding set for the target rule pack.
- Preserve an existing file's style and scope when extending it.
- If several SIEM fields expose the same value or overlapping meaning, bind the one that is most reusable across events, semantically closest to the canonical field, and least likely to be vendor-noise or a one-off alias.
- Do not bind duplicate SIEM fields to the same canonical field unless the repository task explicitly requires alternate field paths.
- If multiple rules share the same device-level mapping, keep the binding shared instead of creating rule-specific files.
- If a required canonical field cannot be located in the relevant mapping file, search nearby mappings before proposing a new canonical field upstream.

## Recheck Checklist

Before finishing, verify all of the following.

- The chosen file path under `tenants/<tenant>/bindings/fields/` matches the intended tenant and device.
- `tenant_id`, `siem_id`, and `device_id` are consistent with the tenant configuration.
- The file includes only canonical fields needed by the target rules or deployment pack.
- Every canonical field in the binding can be traced back to a rule requirement and a mapping file in `mappings/`.
- Every SIEM field value can be traced back to the user-provided event or explicit tenant knowledge.
- If there were duplicate candidate SIEM fields, the selected field is the one judged most stable and most broadly present across relevant events.
- Dataset-specific mappings are placed under `datasets`, not mixed into `default_field_mapping`.
- No tenant binding file is used to define new canonical semantics that belong in `mappings/`.

## Output Expectations

When you perform the task, report briefly:

- which rule or rule pack drove the binding set
- which mapping file under `mappings/` was used
- which SIEM event fields were bound
- whether automated validation was run
