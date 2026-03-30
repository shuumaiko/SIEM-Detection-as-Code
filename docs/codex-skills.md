# Codex Skills

Tài liệu này mô tả ngắn gọn các repo-local Codex Skills hiện có trong `.codex/skills/`.

## Mục đích

Các skill này giúp Codex làm việc đúng với kiến trúc nhiều lớp của repository, thay vì xử lý ad hoc cho từng yêu cầu.

Nên hiểu skill như:

- workflow helper cho Codex
- bộ guardrail theo domain của repo
- tài liệu thao tác chuyên biệt cho từng loại tác vụ

Source kỹ thuật đầy đủ của từng skill nằm tại `.codex/skills/<skill-name>/SKILL.md`.

## Danh sách skill hiện có

### `siem-detection-as-code-base`

Mục đích:
- skill nền cho các tác vụ trải rộng nhiều layer trong repo

Dùng khi:
- cần thay đổi hoặc giải thích kiến trúc chung của repo
- cần sửa tài liệu bám theo `rules/`, `mappings/`, `tenants/`, `artifacts/`, `project-root/`
- cần đảm bảo không nhầm ranh giới giữa source data và generated output

### `project-root-code-maintainer`

Mục đích:
- bảo trì và mở rộng code trong `project-root/` theo hướng business-first, có flow map và code log

Dùng khi:
- sửa CLI, use case, service, repository, validator
- đổi behavior của render, export, deploy, validation
- cần log thay đổi dưới `docs/note/logs/code/`

### `schema-fix-from-source`

Mục đích:
- sửa hoặc thiết kế lại schema bằng cách suy contract từ dữ liệu thật trong repo

Dùng khi:
- cập nhật file trong `schema/`
- xử lý schema drift giữa schema và source files
- cần quyết định split schema hay unified schema

### `detection-mapping-ocsf`

Khuyến nghị:
- clone `ocsf-schema` vào `.tmp/ocsf-schema` khi muốn skill có local OCSF reference ổn định


Mục đích:
- viết hoặc cập nhật detection field mapping theo OCSF hoặc canonical field của repo

Dùng khi:
- sửa `mappings/detections/**/*.fields.yaml`
- chọn field contract cho detection rule
- bổ sung canonical hoặc OCSF path cho rule mapping

### `merge-rule-into-base`

Mục đích:
- đưa rule import từ nguồn ngoài vào lớp `rules/` chuẩn của repo

Dùng khi:
- merge rule từ `.tmp/` hoặc nguồn import khác
- phân loại rule thành detection content hay analyst content
- chuẩn hóa metadata và ghi merge log

### `tenant-config-from-siem-logs`

Mục đích:
- tạo hoặc cập nhật tenant config từ SIEM log thật hoặc event sample

Dùng khi:
- onboard device hoặc dataset mới cho tenant
- cập nhật `tenant.yaml`, `devices/`, `logsources/`, `bindings/ingest/`, `filters/`
- cần suy cấu trúc tenant từ log thực tế

### `tenant-field-binding-writer`

Mục đích:
- viết canonical-to-SIEM field binding cho tenant

Dùng khi:
- cập nhật `tenants/<tenant>/bindings/fields/*.yml`
- cần map canonical fields sang field thực tế của tenant
- cần giữ binding tối thiểu đủ để render rule pack

### `tenant-onboard-from-siem-log`

Mục đích:
- orchestration skill để onboard tenant từ một log input duy nhất

Dùng khi:
- một SIEM log hoặc event sample cần đồng thời sinh tenant config và field binding
- cần phối hợp `tenant-config-from-siem-logs`, `tenant-field-binding-writer`, và `detection-mapping-ocsf`

## Cách đọc skill

Khi cần hiểu hoặc cập nhật một skill:

1. Đọc file `.codex/skills/<skill-name>/SKILL.md`
2. Đọc thêm file `references/` nếu skill có chỉ dẫn sang đó
3. Chỉ xem đúng skill liên quan tới task đang làm

## Nguyên tắc sử dụng trong repo này

- Skill phải bám theo `docs/architecture/`, không tự tạo kiến trúc mới.
- Skill không thay thế source of truth của repo; nó chỉ hướng dẫn cách thao tác đúng với source of truth đó.
- Nếu current implementation đang ở giai đoạn chuyển tiếp, skill nên mô tả rõ current state thay vì che mất drift.

## Tham chiếu nhanh

- Repository skill root: `.codex/skills/`
- Architecture source of truth: `docs/architecture/`
- Current code-change audit trail: `docs/note/logs/code/`
