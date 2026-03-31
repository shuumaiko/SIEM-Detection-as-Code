# Gen-Artifact Hardcoded Query Current Errors

## Request Summary

Log lại chi tiết các lỗi hiện tại của luồng `gen-artifact` đang chạy trên
hardcoded-query pipeline vào `./log` để làm backlog xử lý tiếp.

## Business Definition

- Business goal: ghi nhận rõ các lỗi và rủi ro hiện tại của flow
  `gen-artifact` đang chạy thực tế để ưu tiên sửa có kiểm soát.
- Operator outcome: có một task log tập trung, chỉ ra lỗi nào là bug thực sự,
  lỗi nào là risk, nằm ở layer nào, và nên xử lý theo thứ tự nào.
- Entry command or trigger:
  - `python project-root/main.py gen-artifact --tenant-id <tenant>`
- Main input and output:
  - Inputs: `rules/`, `mappings/detections/`, `tenants/<tenant>/bindings/*`,
    `tenants/<tenant>/overrides/filter/`, `execution/<siem>/`, và
    `tenants/<tenant>/deployments/rule-deployments.yaml`
  - Outputs: `artifacts/<tenant>/<siem>/...` và deployment manifest dưới
    `tenants/<tenant>/deployments/rule-deployments.yaml`
- Affected flow steps:
  1. CLI wiring trong `main.build_app()`
  2. load render candidates
  3. flatten hardcoded-query payload
  4. tenant filter override
  5. resolve ingest target
  6. source rule field -> canonical field -> tenant field
  7. artifact write + manifest sync
- Correct ownership layer:
  - `interfaces`: CLI entry
  - `app/usecases`: export orchestration
  - `app/services`: target resolution, query rewrite, artifact shaping
  - `infrastructure`: loader, repository, filesystem side effects
- Validation plan:
  - giữ log làm backlog review
  - sau này khi fix sẽ cần targeted regression tests cho từng finding
- Log file path:
  - `log/2026-03-31/project-root-code-maintainer/gen-artifact-hardcoded-query-current-errors.md`

## Hardcoded Query Flow Summary

1. `main.build_app()` wire `FileTenantRepository`, `FileRuleRepository`,
   `RuleDeploymentBuilder`, `RuleArtifactService`, `ExecutionConfigLoader`, và
   `TenantFilterOverrideLoader`.
2. `ExportRulesUseCase.prepare_export()` load tenant, load render candidates,
   flatten rule payload, build mapped rules, build artifacts, save artifacts,
   save deployment manifest, rồi sync lại `enabled`.
3. `FileRuleRepository.list_render_candidates()` chỉ chọn source rule `stable`
   có hardcoded query cho SIEM hiện tại.
4. `ExportService.export_rules()` flatten source rule thành payload gồm
   `category/product/service`, `fields`, `search_query`, `targets`,
   `source_path`.
5. `RuleDeploymentBuilder.build()` áp tenant filter override trước, rồi resolve
   target theo tenant, validate query field coverage qua hai lớp mapping, và
   rewrite hardcoded query sang field tenant.
6. `RuleArtifactService.build_artifacts()` merge execution metadata từ
   `execution/<siem>/` và tenant execution overrides vào artifact envelope.
7. `FileRuleRepository.save_rendered_for_tenant()` xóa tree output cũ của
   tenant/SIEM rồi ghi lại artifact mới; sau đó
   `sync_artifact_enabled_states()` override `targets.enabled` theo deployment
   manifest vừa lưu.

## Findings

### 1. High - Rule vẫn bị emit khi không resolve được ingest target nào

- Location:
  - `project-root/app/services/rule_deployment_builder.py`
- Evidence:
  - `build()` vẫn append `rendered_rule` sau khi `mapping = {}`
  - `_expand_mappings({})` trả `[mapping]`
  - `_apply_mapping()` gặp `if not mapping: return item`, nên rule đi tiếp với
    `targets={}` và query placeholder chưa được thay
- Relevant lines:
  - `project-root/app/services/rule_deployment_builder.py:98`
  - `project-root/app/services/rule_deployment_builder.py:167`
  - `project-root/app/services/rule_deployment_builder.py:190-191`
  - `project-root/app/services/rule_deployment_builder.py:217-218`
  - `project-root/app/usecases/export_rules.py:45-48`
- Impact:
  - có thể sinh artifact/deployment entry rỗng cho rule không deploy được
  - summary CLI có thể báo `generated_artifact_count` sai với thực tế deployable
  - nếu artifact builder vẫn giữ được source rule, output có thể chứa query còn
    `$index$` / `$sourcetype$`
- Reproduction evidence:
  - chạy một smoke script nhỏ qua `RuleDeploymentBuilder.build()` với rule có
    `category=nonexistent-category` cho kết quả:

```text
mapped_rules_len= 1
mapped_rule_targets= {}
mapped_rule_query= index=$index$ sourcetype=$sourcetype$ src_ip=*
deployment_payload= {'schema_version': 1.0, 'tenant_id': 'lab', 'rule_deployments_by_siem': {'splunk': [{'rule_id': 'review-no-target', 'enabled': True, 'display_name': 'Review no target'}]}}
```

- Suggested handling order:
  - sửa đầu tiên
  - expectation mong muốn của hardcoded-query flow là rule không có target hợp lệ
    phải bị drop trước khi build artifact và manifest

### 2. High - Registry fallback cho `index/sourcetype` đang wire vào path không tồn tại

- Location:
  - `project-root/main.py`
  - `project-root/infrastructure/file_loader/registry_loader.py`
  - `project-root/app/services/rule_deployment_builder.py`
- Evidence:
  - app wire `RegistryLoader(root=workspace_root / "mappings" / "logsources")`
  - repo hiện không có `mappings/logsources`
  - repo chỉ còn `mappings/legacy/logsources`, nhưng hardcoded-query flow hiện
    đã được định hướng là không dùng `legacy` làm runtime truth
- Relevant lines:
  - `project-root/main.py:72`
  - `project-root/app/services/rule_deployment_builder.py:418-427`
  - `project-root/infrastructure/file_loader/registry_loader.py:19-43`
- Impact:
  - fallback `index/sourcetype` thực tế là dead code
  - rule sẽ bị loại nếu tenant ingest binding không có `index/sourcetype`, kể
    cả khi operator nghĩ rằng registry fallback vẫn còn hoạt động
- Reproduction evidence:

```text
mappings/logsources exists: False
mappings/legacy/logsources exists: True
current checkpoint/splunk: {}
legacy checkpoint/splunk: {'index': 'checkpoint', 'sourcetype': None}
```

- Suggested handling order:
  - sửa ngay sau finding 1
  - cần quyết định rõ: hoặc bỏ hẳn fallback registry khỏi flow hiện tại, hoặc
    tạo root runtime mới không dựa trên `legacy`

### 3. Medium - `enabled` có thể bị reset khi một rule chuyển từ unsplit sang split

- Location:
  - `project-root/app/services/rule_deployment_builder.py`
- Evidence:
  - state cũ được load vào `existing_enabled_by_rule_id`
  - rule split thì ID mới là `source_rule_id::device::dataset`
  - lookup `enabled` chỉ dùng `rendered_rule_id`, không fallback từ
    `source_rule_id`
- Relevant lines:
  - `project-root/app/services/rule_deployment_builder.py:83-85`
  - `project-root/app/services/rule_deployment_builder.py:104-115`
- Impact:
  - deployment manifest có thể bật lại rule variant mới dù source rule cũ đã bị
    operator tắt
  - đây là risk state migration của manifest, không phải lỗi syntax
- Suggested handling order:
  - xử lý sau khi flow drop-target và registry fallback đã ổn

### 4. Medium - Tokenizer rewrite của hardcoded SPL còn mong manh với syntax mới

- Location:
  - `project-root/app/services/rule_deployment_builder.py`
- Evidence:
  - query validation và rewrite dùng tokenizer tự viết
  - reserved token set là hardcoded list
  - parser hiện chỉ né quoted strings, alias sau `as`, function token khi gặp
    `(`
- Relevant lines:
  - `project-root/app/services/rule_deployment_builder.py:683-725`
  - `project-root/app/services/rule_deployment_builder.py:727-775`
- Impact:
  - query mới dùng macro phức tạp, subsearch, command lạ, hoặc field/function
    tên đụng reserved set có thể bị reject hoặc rewrite sai
  - risk này đặc biệt nằm ngay lõi của hardcoded-query flow hiện tại
- Assumption:
  - với SPL đang có trong repo hiện tại, parser vẫn đủ dùng cho phần lớn case
- Suggested handling order:
  - thêm regression tests trước khi mở rộng parser

### 5. Medium - Artifact persistence vẫn xóa cả cây output trước khi ghi lại

- Location:
  - `project-root/infrastructure/repositories/file_rule_repository.py`
- Relevant lines:
  - `project-root/infrastructure/repositories/file_rule_repository.py:151`
- Impact:
  - dễ fail trên Windows khi file bị lock
  - nếu process dừng sau `rmtree()` nhưng trước khi ghi xong, tenant sẽ bị mất
    toàn bộ artifact tree của SIEM đó
- Notes:
  - đây là lỗi vận hành của flow đang chạy, không phải khác biệt kiến trúc
- Suggested handling order:
  - xử lý sau khi correctness của target resolution đã được fix

### 6. Low - Lỗi parse ở execution config và filter override bị nuốt hoàn toàn

- Location:
  - `project-root/infrastructure/file_loader/execution_config_loader.py`
  - `project-root/infrastructure/file_loader/tenant_filter_override_loader.py`
- Relevant lines:
  - `project-root/infrastructure/file_loader/execution_config_loader.py:103-110`
  - `project-root/infrastructure/file_loader/tenant_filter_override_loader.py:73-80`
- Impact:
  - `gen-artifact` có thể chạy “thành công” nhưng quietly bỏ qua execution
    metadata hoặc filter override
  - operator không có signal để phân biệt “không có override” với “override bị
    parse lỗi”
- Suggested handling order:
  - có thể xử lý sau cùng bằng warning/logging, không nhất thiết block correctness fix

## Current Test Signals

- Command run from workspace root:

```text
python -m pytest project-root\tests\test_export_rules.py project-root\tests\test_folder_architecture.py -q
```

- Result:
  - fail do import path không đúng khi chạy từ workspace root

- Command run from `project-root/`:

```text
python -m pytest tests\test_export_rules.py tests\test_folder_architecture.py -q
```

- Result:
  - `1 failed, 6 passed`
- Current known failing test:
  - `tests/test_folder_architecture.py::test_rule_repository_reads_render_candidates_from_current_rules`
- Evidence:
  - test còn expect analyst rule
    `faee897b-2394-45cf-ae5d-0379476fbf3e` nằm trong render candidates
  - nhưng repo hiện chỉ render source rule `stable`, và rule đó hiện không còn
    satisfy expectation cũ
- Relevant lines:
  - `project-root/tests/test_folder_architecture.py:39`
  - `project-root/infrastructure/repositories/file_rule_repository.py:116-121`

## Missing Coverage

- chưa có test cho case “không resolve được target nào nhưng rule vẫn bị emit”
- chưa có test cho path registry fallback đang wire sai
- chưa có test migration `enabled` khi rule đổi từ unsplit sang split
- chưa có test negative cho parser query rewrite khi gặp syntax SPL phức tạp hơn

## Suggested Fix Order

1. Chặn hẳn việc emit mapped rule / deployment entry khi `mapping` rỗng.
2. Quyết định số phận của registry fallback trong hardcoded-query flow:
   - hoặc bỏ hoàn toàn
   - hoặc tạo runtime source mới không phụ thuộc `legacy`
3. Bổ sung logic carry-forward `enabled` khi rule split.
4. Tăng test coverage cho target resolution và split-state migration.
5. Cải thiện artifact persistence theo hướng an toàn hơn trên Windows.
6. Thêm warning/logging cho parse failure ở execution/filter override.

## Assumptions

- Review này chỉ áp cho hardcoded-query flow đang chạy thực tế của `gen-artifact`.
- Không đánh giá theo semantic converter tương lai.
- Không xem việc chỉ render `stable` là bug, vì đó là contract hiện tại của flow.
