---
name: merge-rule-into-base
description: Merge imported SIEM rules into the repository's canonical `rules/` layer using the repo docs and JSON schemas. Use when Codex needs to inspect an imported rule from sources such as `.tmp/rules`, classify it as detection or analyst content, decide whether to create a new canonical rule or merge into an existing base rule, preserve detection or correlation semantics, normalize metadata to schema, and record all changed rules in a merge log without relying on validation functions under `./project-root`.
---

# Merge Rule Into Base

Use this skill to fold imported rules into the repo's core rule set while preserving the original semantic intent. Read docs and schemas first, classify the rule correctly, then either create a new canonical rule or merge into an existing one and log what changed.

## Start Here

Read only the minimum context required for the current merge.

- Read `docs/architecture/rules-relationship.md` to understand `detection`, `detection_base` or `base`, and `analyst`.
- Read `schema/rules/rule_file.schema.json`, `schema/rules/base_rule.schema.json`, and `schema/rules/correlation_rule.schema.json` before deciding the target file shape.
- Check `.tmp/rules/` first when the imported content is a Sigma clone or a staged upstream rule set.
- Read the closest existing canonical rule candidates under `rules/detections/` or `rules/analysts/`.
- Read nearby rules in the same taxonomy to mirror naming, folder placement, metadata style, and field ordering.
- Do not use validation functions under `./project-root` unless the user explicitly changes that instruction.

## Merge Workflow

Follow this order.

1. Inspect the imported rule and extract the semantic core: title, source references, logsource or correlation behavior, detection fields, tags, level, and any Sigma-style condition or aggregation logic.
   - When the import was cloned from Sigma, check the staged source under `.tmp/rules/` before editing canonical files.
2. Classify the imported rule by target semantic type:
   - `detection` when the logic is a standalone event rule with `logsource` and `detection`.
   - `detection_base` or `base` when the logic is a reusable building block that an analyst rule can call.
   - `analyst` when the rule expresses threshold, sequence, aggregation, or multi-rule correlation in `correlation`.
   - When creating or normalizing an `analyst` rule from referenced base rules, carry a concrete `logsource` block into the analyst rule from the shared base-rule scope. Do not leave analyst `logsource` implicit for runtime inference.
3. Search for the closest existing canonical rule by intent, not just by title.
4. Decide whether the imported rule should create a new canonical rule or merge into an existing one.
5. Set `status: test` on every rule that is created or modified by the merge.
6. Normalize the final YAML to the applicable schema while preserving the semantic logic.
7. Record every changed rule in a merge log.

## Classification Rules

Use the repo architecture, not the upstream source taxonomy, as the source of truth.

- Target `rules/detections/**` for `detection` and `detection_base` or `base`.
- Target `rules/analysts/**` for `analyst`.
- Treat Sigma event rules as candidates for `detection` unless they are clearly intended as reusable base logic.
- Treat imported threshold or aggregation logic as `analyst` unless the repository already models the same concept as a standalone detection.
- Preserve `detection` blocks for event rules and `correlation` blocks for analyst rules.

## Decision Tree

### TH1: Import Rule Cannot Merge Into A Base Rule

Create new canonical content.

- If the imported rule is a standalone event rule, create one new detection rule under `rules/detections/`.
- If the imported rule is analyst-facing or contains correlation logic, create the required reusable base rule under `rules/detections/` when needed and create the analyst rule under `rules/analysts/`.
- If you create an analyst rule from a base rule, copy the base rule `logsource` into the analyst rule so the analyst content keeps its own deploy scope.
- Base new files on Sigma-style structure first, then normalize the result to the repo schema.
- Set `status: test` on every newly created canonical rule.
- Keep the imported semantic logic intact while rewriting only the repository-facing structure and metadata.
- Generate a new UUID only when the rule becomes a new semantic object in this repository.

### TH2: Import Rule Can Merge Into An Existing Base Or Similar Canonical Rule

Pick one of these branches after comparing the imported rule with the canonical target.

If the canonical rule is not yet repo-standard:

- Merge the imported rule into the canonical rule.
- Normalize the canonical file to schema and local style.
- Set `status: test` on the canonical rule because it was changed by the merge.
- Do not change the underlying `detection` logic or `correlation` logic unless the user explicitly asks for semantic redesign.
- Clean up metadata, references, formatting, field lists, and other schema-facing issues around the preserved logic.

If the canonical rule is already repo-standard:

- Merge only the imported query or execution-facing expression into the canonical rule where that repository pattern is still used, such as `x_query`.
- Update metadata that should track the import, such as `references`, `modified`, `description`, `tags`, or explanatory notes.
- Set `status: test` on the canonical rule because it was changed by the merge.
- Do not silently change `logsource`, `mitre att&ck` tags, or `detection` or `correlation` semantics.
- When the imported rule suggests improvements to those semantic sections, add the suggestion as YAML comments near the relevant block or describe it in the merge log if inline comments would be too noisy.

## Normalization Rules

- Keep the rule valid against the relevant schema branch.
- Every created or modified rule must end with `status: test`.
- Required metadata for detection-style rules: `title`, `id`, `status`, `description`, `references`, `author`, `date`, `tags`, `logsource`, `detection`.
- Required metadata for analyst rules in this repository: `title`, `id`, `status`, `description`, `references`, `author`, `date`, `tags`, `logsource`, `correlation`, `fields`, `falsepositives`, `level`.
- Accept `rule_type: detection`, `rule_type: detection_base`, or `rule_type: base` for detection-style content based on nearby repo patterns.
- Keep `level: informational` when `rule_type: base` is used, matching the schema rule.
- Preserve nearby file conventions for extension, naming, and metadata ordering.
- Prefer Sigma-compatible `detection` structure and condition syntax unless the repo already uses a local adaptation for the same pattern.

## Merge Guardrails

- Do not overwrite an existing rule just because the title is similar; compare semantics, scope, and intended reuse.
- Do not remove original references from the canonical rule unless they are clearly wrong or duplicated.
- Do not demote an analyst rule into a detection rule or the reverse without a strong architectural reason.
- Do not treat `x_query` as the semantic source of truth.
- Prefer adding comments or log notes for proposed semantic improvements instead of changing semantic blocks when the user asked to preserve them.

## Merge Log

Always record the outcome of the merge in a log file.

- Create or update a markdown log under `log/YYYY-MM-DD/merge-rule-into-base/`.
- Use the current local date for `YYYY-MM-DD`.
- Use a short filename such as `<task-slug>.md`.
- Log every created or modified canonical rule.
- Include: imported source identifier, target file path, classification, action taken, whether logic was preserved, metadata changes, query changes, and deferred suggestions.
- Use `references/merge-log-template.md` as the default structure when creating a new log file.

## Completion Checklist

Before finishing, verify these points manually.

- The target file is placed in the correct taxonomy under `rules/detections/` or `rules/analysts/`.
- Every created or modified rule has `status: test`.
- The final YAML shape matches the applicable schema branch.
- The semantic logic that the user wanted preserved is unchanged.
- Any suggestions that were intentionally not applied to `logsource`, MITRE tags, or semantic logic are captured as comments or in the merge log.
- The merge log clearly states which rules were created or changed.
