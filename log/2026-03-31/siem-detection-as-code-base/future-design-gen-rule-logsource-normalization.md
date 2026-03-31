# Future Design - Gen Rule Logsource Normalization

- Request summary: Summarize a detailed design direction for standardizing rule logsource matching and optimizing the future `gen-rule` flow under `docs/future-design/`.
- File created:
  - `docs/future-design/gen-rule-logsource-normalization.md`
- Main decisions recorded:
  - Keep `rule.logsource.category/product/service` as the rule-side semantic contract.
  - Treat Detection Catalog as a source-family reference dictionary, not as the repository's primary rule taxonomy.
  - Separate tenant reality fields from normalized rule-matching fields.
  - Keep ATT&CK as metadata and coverage overlay, not as the primary folder taxonomy for `rules/`.
  - Introduce future concepts of `tenant-scope` and `rule-index` to reduce runtime heuristic matching.
- Validation:
  - Read current architecture docs and matching code paths before drafting.
  - Re-read the final document after creation.
