---
name: schema-fix-from-source
description: Repair or redesign repository schema files by inspecting the real source files first and deriving contracts from current content. Use when Codex needs to update files under `schema/`, compare schema drift against `rules/`, `mappings/`, or `tenants/`, decide between per-file-type schemas and one unified schema, or document schema changes without modifying `project-root` runtime code.
---

# Schema Fix From Source

Use this skill to fix schema drift from the data layer outward.

## Start From Real Files

Read the smallest useful set of real files before editing any schema.

1. Read representative source files from the target family.
2. Read the matching schema files under `schema/`.
3. Read nearby docs or notes only when they affect the decision.

For this repo, start with `references/repo-schema-map.md`.

## Workflow

Follow this order.

1. Identify the source-of-truth file family: `rules/`, `mappings/`, or `tenants/`.
2. Compare actual file shape against the active schema, not against assumptions.
3. List the fields that are consistently present, optional, transitional, or type-specific.
4. Decide whether the family should use:
   - one schema per file type, or
   - one unified schema with a discriminator such as `rule_type`.
5. Edit only the schema layer, notes, or tests outside `project-root`.
6. Re-read sample files against the edited schema and call out any unresolved drift.

## Schema Strategy Decision

Prefer separate schemas when:

- file families have different top-level blocks such as `detection` vs `correlation`
- required fields differ materially across file types
- a unified schema would become mostly conditional exceptions

Prefer one unified schema when:

- files share the same envelope and differ mainly by a stable discriminator
- the common required fields are large enough to justify one contract
- `oneOf`, `allOf`, or `$defs` can keep the schema readable

For rule files in this repo, treat the split-vs-unified choice as a design decision that must be justified from the current YAML files. Do not assume the existing split is correct just because it already exists.

## Editing Rules

- Preserve what the repository actually stores today, including transitional fields such as `x_query`, unless the user explicitly asks for cleanup.
- Prefer modeling inconsistent fields as optional first, then tighten only where the samples support it.
- Keep schema names, `$id`, and `$ref` relationships coherent after structural changes.
- If the user asks for "schema tong", prefer a thin entry schema plus shared `$defs` instead of duplicating field definitions.
- If the user asks for schema per file type, keep each schema narrowly scoped to one real file family.

## Guardrails

- Do not modify `project-root/`.
- Do not patch runtime validators, loaders, or CLI commands under `project-root/`.
- If a schema-only fix would require runtime code changes to become active, stop at the schema/docs layer and state that dependency clearly.
- Avoid inventing fields that do not exist in the source files.
- Avoid tightening enums or required lists from one sample only.

## Validation

- Re-open the edited schema files and representative source files after the patch.
- Check that every `$ref` still resolves logically.
- If no non-`project-root` validation command exists, do a manual sample-to-schema sanity pass and say so.
- Mention clearly that runtime validation in `project-root` was intentionally left untouched.
