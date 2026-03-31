# Tenant Config Logsource Catalog Reference

- Request summary: Add a small Detection Catalog reference schema for `tenant-config-from-siem-logs` and apply it to the skill workflow.
- Files changed:
  - `.codex/skills/tenant-config-from-siem-logs/SKILL.md`
  - `.codex/skills/tenant-config-from-siem-logs/logsource-catalog.schema.json`
  - `.codex/skills/tenant-config-from-siem-logs/logsource-catalog.seed.yaml`
- Change notes:
  - Added a compact catalog entry contract with required keys `catalog_logsource`, `suggested_category`, `suggested_service`, and `dataset_id_pattern`.
  - Seeded the reference dictionary with initial entries derived from high-signal Detection Catalog source families and current repo examples.
  - Updated the skill so the dictionary is consulted before choosing tenant dataset naming, while keeping final `dataset_id` decisions rule-driven and tenant-stable.
  - Explicitly documented that `catalog_logsource` and `dataset_id_pattern` are decision aids for the skill, not mandatory persisted tenant fields.
- Validation:
  - Manually re-read the updated skill and new reference files.
  - Confirmed key references in `SKILL.md` with `rg`.
- Assumptions:
  - The reference dictionary will remain skill-local for now and is not yet part of `project-root` runtime validation.
