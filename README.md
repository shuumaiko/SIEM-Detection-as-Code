# SIEM-Detection-as-Code

Repository này quản lý `Detection as Code` cho môi trường SOC đa tenant, theo hướng tách biệt giữa detection logic, lớp chuẩn hóa field, cấu hình tenant, và artifact triển khai theo từng SIEM.

## Repository Này Là Gì

`SIEM-Detection-as-Code` nên được hiểu như một mô hình kiến trúc và tổ chức repository để xây dựng `Detection as Code` trong môi trường multi-tenant.

Ý tưởng chính là detection engineering không nên bị ép vào một lớp rule phẳng duy nhất. Trong vận hành SOC thực tế, cùng một detection intent thường cần được tái sử dụng qua:

- nhiều tenant
- nhiều tổ hợp device và logsource
- nhiều cách đặt tên field khác nhau trên SIEM
- nhiều đích triển khai hoặc định dạng thực thi khác nhau

Vì vậy, repository này xem detection engineering như một hệ thống nhiều lớp:

- `rules/` biểu diễn detection intent
- `mappings/` biểu diễn canonical field contract
- `tenants/` biểu diễn ngữ cảnh triển khai riêng của từng tenant
- `artifacts/` biểu diễn output đã render cho tenant
- `project-root/` cung cấp engine để đọc, validate, render, export, và deploy theo mô hình đó

Nói cách khác, đây không chỉ là một kho rule. Đây là một reference architecture để tách phần detection knowledge có thể tái sử dụng khỏi phần chi tiết vận hành theo từng tenant.

## Mục Tiêu

`SIEM-Detection-as-Code` được xây dựng để:

- tách detection logic khỏi vendor log cụ thể
- tách detection logic khỏi SIEM implementation cụ thể
- quản lý detection rule như code
- hỗ trợ validate, render, export, và deploy theo tenant
- tăng khả năng tái sử dụng detection content giữa nhiều tenant

Về mặt kiến trúc, repository này không chỉ là nơi chứa rule YAML. Đây là một mô hình tổ chức detection content theo nhiều lớp, trong đó:

- `rules/` giữ detection knowledge gốc
- `mappings/` giữ lớp chuẩn hóa field
- `tenants/` giữ cấu hình thực tế của từng tenant
- `artifacts/` giữ output đã render cho tenant
- `project-root/` là application engine để đọc, validate, render, và deploy

## Vì Sao Cần Multi-Tenant Detection-as-Code

Trong môi trường single-tenant, vẫn có thể quản lý detection theo hướng khá trực tiếp từ rule logic sang SIEM query. Nhưng trong môi trường multi-tenant, cách tiếp cận đó khó mở rộng hơn vì:

- một detection có thể cần field binding khác nhau cho từng tenant
- mỗi tenant có thể có tập device, dataset, hoặc parser behavior khác nhau
- cùng một logical rule có thể cần enablement, filter, hoặc deployment decision khác nhau theo tenant
- định dạng thực thi có thể khác với mô hình nội dung dùng để giữ nguyên detection meaning

Repository này được thiết kế xoay quanh đúng bài toán tách biệt đó.

Kiến trúc ở đây cố gắng trả lời một câu hỏi thực tế:

Làm thế nào để một định nghĩa detection vẫn có thể tái sử dụng, nhưng đồng thời được render thành output riêng cho từng tenant dựa trên khác biệt về ingest, field, filter, và cách triển khai lên SIEM?

Cấu trúc repository là câu trả lời mà project này đề xuất.

## Trạng Thái Hiện Tại

Tài liệu kiến trúc đã được cập nhật theo mô hình mới trong `docs/architecture/`, nhưng implementation trong `project-root/` hiện vẫn đang trong giai đoạn chuyển tiếp và chưa phản ánh đầy đủ kiến trúc mới.

Điều này có nghĩa là:

- cấu trúc repo và quan hệ dữ liệu trong tài liệu là nguồn tham chiếu chính hiện tại
- một số luồng code cũ có thể chưa chạy đúng sau khi đổi kiến trúc
- hardcoded SIEM query, đặc biệt ở nhánh Splunk, vẫn đang được dùng như execution artifact tạm thời
- README này ưu tiên mô tả kiến trúc, mô hình dữ liệu, và cách hiểu repository hơn là làm hướng dẫn runtime end-to-end hoàn chỉnh

Nếu cần đi sâu hơn vào từng phần, xem thêm:

- `docs/architecture/project-architecture.md`
- `docs/architecture/tenants-relationship.md`
- `docs/architecture/mappings-relationship.md`

## Góc Nhìn Kiến Trúc

Có thể nhìn hệ thống theo 3 trục chính.

### 1. Trục Nội Dung Detection

Đây là phần quản lý tri thức detection:

- `rules/`: base detection rules theo category và product
- `mappings/detections/`: ánh xạ từ source rule field sang canonical field
- `tenants/.../bindings/fields/`: ánh xạ từ canonical field sang field thực tế trên SIEM của tenant

Mục tiêu của trục này là giữ detection logic đủ ổn định để tái sử dụng, thay vì gắn cứng vào parser hoặc naming riêng của từng tenant.

### 2. Trục Cấu Hình Tenant

Đây là phần mô tả môi trường thực tế của từng tenant:

- `tenant.yaml`: định danh tenant, `siem_id`, metadata vận hành
- `devices/`: thiết bị hoặc platform phát sinh log
- `logsources/`: dataset logic của từng device
- `bindings/ingest/`: map `dataset_id` sang ingest target thực tế như `index` và `sourcetype`
- `bindings/fields/`: map canonical field sang field thực tế trên SIEM
- `filters/`: tenant-specific filter dùng trong lúc render
- `deployments/rule-deployments.yaml`: manifest enable hoặc disable rule theo SIEM

Trục này trả lời các câu hỏi vận hành:

- tenant có nguồn log nào
- dataset nào đang active
- dataset đó đi vào SIEM bằng cấu hình ingest nào
- rule nào được bật cho tenant
- filter nào cần áp khi render từ base rule

### 3. Trục Vận Hành Và Đầu Ra

Đây là phần phục vụ validate, build, export, deploy:

- `project-root/`: CLI, use cases, services, repositories, adapters
- `schema/`: contract để validate rule và tenant config
- `tests/`: quality gate ở mức smoke test, validator, và kiểm tra cấu trúc
- `artifacts/`: kết quả render hoặc export dành riêng cho từng tenant

## Mô Hình Dữ Liệu Cốt Lõi

Kiến trúc hiện tại xoay quanh 4 khóa liên kết chính:

| Key | Ý nghĩa |
| --- | --- |
| `tenant_id` | định danh tenant |
| `device_id` | định danh thiết bị hoặc platform phát sinh log |
| `dataset_id` | định danh dataset logic của device |
| `siem_id` | định danh SIEM đích |

Quan hệ chính trong tenant layer:

- `tenant` sở hữu `devices`
- mỗi `device` có `logsource`
- `logsource` khai báo các `dataset_id`
- `bindings/ingest` nối `dataset_id` với ingest target thực tế trên SIEM
- `bindings/fields` nối canonical field với field thật của tenant trên SIEM
- `filters` tinh chỉnh base rule khi render
- `deployments` quyết định rule nào được đi tiếp vào pipeline

## Vai Trò Của `mappings/`

Trong kiến trúc hiện tại, `mappings/` không được hiểu là lớp phải giải trọn bài toán từ raw log đến field cuối cùng trên SIEM. Đây là lớp contract để team content chuẩn hóa field vocabulary cho detection và nối detection logic với field thực tế của từng tenant.

Pipeline field ở mức thực dụng hiện tại là:

```text
source rule field <=> canonical field <=> tenant SIEM field
```

Trong đó:

- `source rule field` là field của rule nguồn hoặc content legacy
- `canonical field` là vocabulary chuẩn nội bộ của project
- `tenant SIEM field` là field thực tế đang tồn tại trên SIEM của tenant

Hướng tiếp cận này giúp:

- ingest rule từ nhiều nguồn field vocabulary khác nhau
- giảm phụ thuộc vào naming riêng của từng người viết rule
- cho phép render theo tenant ngay cả khi converter tổng quát chưa hoàn thiện
- giữ một semantic contract đủ ổn định để content team và deploy team cùng làm việc

## Vai Trò Của Hardcoded SIEM Query

Ở trạng thái hiện tại, hardcoded query như SPL vẫn là execution artifact hợp lệ trong pipeline.

Điều này là một trade-off có chủ đích:

- converter tổng quát từ detection rule chuẩn sang SIEM rule chưa ổn định
- pipeline vẫn cần output có thể dùng để review, export, hoặc deploy
- detection intent và canonical field vẫn được giữ ở lớp nội dung, trong khi query hardcode đảm nhiệm vai trò thực thi tạm thời

Nói ngắn gọn:

- canonical giữ `meaning`
- hardcoded query giữ `execution`

## Luồng Xử Lý Tổng Quát

Ở mức kiến trúc, pipeline của project hiện được hiểu như sau:

1. Nạp tenant config từ `tenants/<tenant>/`.
2. Xác định `tenant_id`, `siem_id`, danh sách device và dataset.
3. Nạp base rules từ `rules/`.
4. Nạp detection mappings từ `mappings/detections/`.
5. Resolve ingest binding từ `tenants/.../bindings/ingest/`.
6. Resolve field binding từ `tenants/.../bindings/fields/`.
7. Áp tenant filters từ `tenants/.../filters/`.
8. Đọc `deployments/rule-deployments.yaml` để chọn tập rule bật cho tenant.
9. Render output vào `artifacts/<tenant>/tenant-rules/`.
10. Nếu cần, dùng adapter trong `project-root/` để export hoặc deploy sang SIEM đích.

## Cấu Trúc Thư Mục

```text
.
|-- artifacts/
|   `-- <tenant>/
|       `-- tenant-rules/
|           `-- detections/
|-- docs/
|   `-- architecture/
|-- mappings/
|   `-- detections/
|-- project-root/
|   |-- app/
|   |-- domain/
|   |-- infrastructure/
|   |-- interfaces/
|   `-- main.py
|-- rules/
|   `-- detections/
|-- schema/
|-- tenants/
|   `-- <tenant>/
|       |-- tenant.yaml
|       |-- devices/
|       |-- logsources/
|       |-- bindings/
|       |   |-- ingest/
|       |   `-- fields/
|       |-- filters/
|       `-- deployments/
`-- tests/
```

Ý nghĩa ngắn gọn:

- `rules/` là source of truth cho detection content gốc
- `mappings/` là source of truth cho shared field mapping ở lớp content
- `tenants/` là source of truth cho cấu hình triển khai theo tenant
- `artifacts/` là output đã materialize, không phải nơi chỉnh tay dài hạn

## Nguồn Tham Chiếu Chính

Khi làm việc với repo ở thời điểm hiện tại, nên ưu tiên đọc theo thứ tự sau:

1. `docs/architecture/project-architecture.md`
2. `docs/architecture/tenants-relationship.md`
3. `docs/architecture/mappings-relationship.md`
4. `rules/`, `mappings/`, `tenants/`, `artifacts/`
5. `project-root/` như implementation đang được điều chỉnh dần theo kiến trúc mới

## Ghi Chú Cho Contributor

- Ưu tiên xem `rules/`, `mappings/`, và `tenants/` là các lớp dữ liệu chính của repo.
- Không xem `artifacts/` là nơi chỉnh tay lâu dài; đây là output render theo tenant.
- Khi thêm rule mới, nên xác định rõ:
  - detection intent
  - source rule fields đang dùng
  - canonical fields cần có
  - tenant bindings cần để render được cho tenant mục tiêu
- Khi cập nhật tài liệu hoặc cấu trúc, cần giữ nhất quán với bộ tài liệu trong `docs/architecture/`.

## Tóm Tắt

`SIEM-Detection-as-Code` hiện được tổ chức theo mô hình:

- `rules/` giữ detection knowledge
- `mappings/` giữ field contract
- `tenants/` giữ hiện trạng triển khai của từng tenant
- `artifacts/` giữ output đã render
- `project-root/` là engine đang được hoàn thiện dần để bám theo kiến trúc này

Trong giai đoạn hiện tại, kiến trúc tài liệu là phần ổn định hơn implementation. Vì vậy README này được cập nhật để phản ánh đúng mô hình dữ liệu và cách hiểu repository theo version kiến trúc mới.
