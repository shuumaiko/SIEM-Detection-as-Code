---
name: detection-mapping-ocsf
description: Create or update detection field mapping files under mappings/detections by preferring direct OCSF field paths where they map cleanly, and using repository canonical fields only when a direct OCSF path is not a good fit. Use when Codex needs to write or revise *.fields.yaml mapping files, choose field contracts from a relevant OCSF event or object, or build source_fields from rule field requirements explicitly provided by the user.
---

# Detection Mapping OCSF

Use this skill to write or revise `mappings/detections/**/*.fields.yaml` files from user-defined required rule fields.

## Inputs To Gather

Collect the minimum information needed before editing.

- Collect the rule's required source fields from the user or from the rule file.
- Identify the target logsource tuple: `category`, `product`, `service`.
- Locate the mapping file that should be edited; create one only when a shared dictionary for that taxonomy does not already exist.
- Treat `.tmp/ocsf-schema` as the preferred local OCSF reference if present.
- If `.tmp/ocsf-schema/version.json` exists, read it and capture the exact OCSF version string used for the mapping decision.

## Mapping Workflow

Follow this order.

1. List only the source fields the rule actually requires for detection, correlation, or useful output.
2. Inspect the most relevant OCSF event class and supporting object files under `.tmp/ocsf-schema`, and note the exact files, version, and field paths that justify each mapped field group.
3. Prefer the direct OCSF field path when the rule field meaning maps cleanly and stably to an OCSF attribute.
4. Search existing repo mappings and tenant field bindings to reuse an established field contract when the repo already settled on the same OCSF path or when a repo-specific `canonical.*` field is required.
5. Use a repo-specific `canonical.*` field only when a direct OCSF path would be lossy, ambiguous, vendor-specific, or would break an intentional internal contract.
6. Append or update `source_fields` aliases using the user-defined required fields as the primary input set.
7. Write the mapping `description` so it records the detailed field-reference sources that informed the mapping, not just a generic mention of OCSF.
8. Keep the mapping file shared and detection-driven; do not turn it into a rule-specific dump of every possible raw field.

## Canonical Field Rules

- Prefer `canonical_field` entries for canonical mappings.
- Preserve an existing file's style if the file already mixes legacy `target_field` patterns, unless the task explicitly includes cleanup.
- Prefer a direct OCSF field path in `canonical_field` when the semantics are exact enough to stand on their own.
- Reuse an existing OCSF field path already present in nearby mappings when the meaning matches.
- Reuse an existing repo-specific `canonical.*` field when the repo already depends on that internal contract for the same meaning.
- Use OCSF as the primary semantic reference and default output shape unless there is a clear reason not to.
- Create or keep a repo-specific `canonical.*` field only when the repo does not express that meaning cleanly with a direct OCSF path.
- When falling back to `canonical.*`, capture the reason in the mapping description if it is not obvious from the field name.
- Avoid tenant-specific or SIEM-specific names in `canonical_field`.

## OCSF Lookup Rules

- Prefer non-deprecated OCSF event classes when multiple candidates exist.
- Read the event class first, then read referenced objects that carry the field semantics.
- For web access and WAF-style detections, start with `events/application/web_resources_activity.json`, then inspect `objects/http_request.json`, `objects/url.json`, and related endpoint objects.
- Read `.tmp/ocsf-schema/version.json` when available and carry that version into the mapping description.
- If `.tmp/ocsf-schema` is unavailable, fall back to the repo's existing mappings and architecture docs, and say that the local OCSF clone was missing.
- Read `references/ocsf-lookup.md` for fast lookup paths and naming guidance.

## File Shape Rules

Keep the file valid against `schema/mappings/detection_fields.schema.json`.

- Keep `mapping_type: detection_fields`.
- Keep `logsource.category`, `logsource.product`, and `logsource.service` aligned with the target rules.
- Keep every `source_fields` list unique and non-empty.
- Update the `description` so it states the mapping scope and cites the detailed field-reference sources that informed the design.
- In the `description`, include the OCSF version referenced, preferably from `.tmp/ocsf-schema/version.json`.
- In the `description`, name the exact OCSF event and object files used, and when practical mention the field paths or field groups they informed.
- When nearby repo mappings or architecture docs materially influenced field reuse, mention that reference briefly after the OCSF sources.
- Avoid vague descriptions such as only `Defined using OCSF`; prefer descriptions such as `Defined using local OCSF 1.9.0-dev from version.json plus Detection Finding, Malware.name, File.name/path/hashes, Device.hostname/ip, and User.name semantics.`

## Editing Guardrails

- Avoid adding fields that the user did not request and the rule does not require.
- Avoid renaming an established canonical field unless the change is intentional and the impact has been checked.
- Avoid baking tenant bindings into `mappings/detections/`; tenant-specific physical fields belong in `tenants/.../bindings/fields/`.
- Prefer a compact, maintainable shared dictionary over exhaustive vendor normalization.

## Validation

- Re-read `schema/mappings/detection_fields.schema.json` after structural edits.
- Compare with nearby mappings in the same taxonomy to keep naming and scope consistent.
- Re-read the final `description` and verify it still names the actual OCSF version and OCSF or repo references used for the mapped fields.
- Mention clearly when no dedicated automated validator was run for mappings.
