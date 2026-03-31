# Gen-Artifact Drop Rules Without Targets

## Request Summary

Fix lỗi hardcoded-query flow vẫn emit rule vào artifact/deployment manifest dù
không resolve được ingest target nào.

## Business Definition

- Business goal: chỉ giữ lại rule thật sự deployable trong output của
  `gen-artifact`.
- Operator outcome: khi tenant không match được dataset hoặc field contract cho
  một rule, rule đó bị drop khỏi `mapped_rules`, artifact output, và deployment
  manifest thay vì để lại entry rỗng.
- Entry command:
  - `python project-root/main.py gen-artifact --tenant-id <tenant>`
- Main input and output:
  - Inputs: source render candidates từ `rules/` và tenant context từ
    `tenants/<tenant>/`
  - Outputs: `artifacts/<tenant>/<siem>/...` và
    `tenants/<tenant>/deployments/rule-deployments.yaml`
- Affected flow steps:
  1. target resolution trong `RuleDeploymentBuilder.build()`
  2. mapping expansion
  3. export regression tests
- Correct ownership layer:
  - `app/services`: bỏ emit rule khi không có mapping deployable
  - `tests`: regression test end-to-end cho prepare_export
- Validation plan:
  - chạy `pytest` riêng cho `tests/test_export_rules.py`
- Log file path:
  - `log/2026-03-31/project-root-code-maintainer/gen-artifact-drop-rules-without-targets.md`

## Function Flow Summary

1. `ExportRulesUseCase.prepare_export()` vẫn load tenant, render candidates, và
   flat export payload như cũ.
2. `RuleDeploymentBuilder.build()` giờ chặn sớm các rule có `mapping = {}`
   trước khi expand mapping hay append vào `mapped_rules`.
3. `_expand_mappings()` cũng được siết lại để trả `[]` cho mapping rỗng, tránh
   coi empty mapping như một variant hợp lệ.
4. Regression test mới verify một source rule `stable` có hardcoded query nhưng
   không match được ingest target sẽ:
   - không xuất hiện trong `rendered_rules`
   - không sinh artifact
   - không để lại deployment entry

## Files Changed

- `project-root/app/services/rule_deployment_builder.py`
- `project-root/tests/test_export_rules.py`
- `log/2026-03-31/project-root-code-maintainer/gen-artifact-drop-rules-without-targets.md`

## Tests Run

- `python -m pytest tests/test_export_rules.py -q` from `project-root/`

## Risks / Notes

- Fix này chỉ xử lý đúng phạm vi bug “emit rule khi không có target”.
- Chưa đụng tới registry fallback, split-state migration của `enabled`, hay
  Windows-safe artifact persistence.
