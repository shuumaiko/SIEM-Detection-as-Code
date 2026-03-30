# SIEM-Detection-as-Code

Repository này quản lý `Detection as Code` cho môi trường SOC đa tenant, theo hướng tách biệt giữa detection intent, field contract, tenant deployment context, execution metadata, và artifact đầu ra theo từng SIEM.

## Repository này là gì

`SIEM-Detection-as-Code` nên được hiểu là một repository kiến trúc nhiều lớp, không chỉ là nơi lưu rule YAML.

Các lớp chính hiện nay là:

- `rules/`: semantic detection content
- `mappings/`: contract chuẩn hóa field
- `execution/`: execution policy và metadata theo từng SIEM
- `tenants/`: cấu hình triển khai thực tế theo tenant
- `artifacts/`: output đã render cho tenant
- `schema/`: contract validation cho rule, tenant, mapping, artifact
- `project-root/`: engine để load, validate, render, export, và deploy

Mục tiêu của mô hình này là giữ detection logic có thể tái sử dụng giữa nhiều tenant, nhiều loại device, và nhiều cách triển khai SIEM khác nhau mà không phải fork toàn bộ rule.

## Mục tiêu

Repository được tổ chức để:

- tách detection logic khỏi vendor log cụ thể
- tách detection logic khỏi SIEM implementation cụ thể
- quản lý detection rule như code
- hỗ trợ validate, render, export, và deploy theo tenant
- tái sử dụng detection content qua nhiều tenant

## Source of truth

Ở trạng thái hiện tại, nên hiểu repo theo thứ tự ưu tiên sau:

1. `docs/architecture/` là nguồn tham chiếu kiến trúc chính.
2. `rules/`, `mappings/`, `execution/`, `tenants/`, `schema/` là các lớp dữ liệu chính.
3. `artifacts/` là output render, không phải nơi chỉnh tay dài hạn.
4. `project-root/` là implementation đang được kéo dần về đúng kiến trúc.

Thiết kế kiến trúc hiện tại vẫn được giữ nguyên:

- semantic rule tách khỏi execution
- tenant context tách khỏi detection content
- deployment decision tách khỏi rule gốc
- artifact là output cuối cùng sau khi render

## Trạng thái vận hành hiện tại

Implementation hiện tại trong `project-root/` đã có các flow chạy được cho nhánh hardcoded query, đặc biệt với Splunk:

- load tenant từ `tenants/<tenant>/`
- đọc source rule từ `rules/detections/` và `rules/analysts/`
- resolve ingest target từ `bindings/ingest/`
- yêu cầu field binding trước khi render artifact
- resolve execution config từ `execution/<siem>/` và tenant override nếu có
- render artifact vào `artifacts/<tenant>/tenant-rules/`
- sinh hoặc refresh `deployments/rule-deployments.yaml`
- đồng bộ trạng thái `enabled` từ deployment manifest ngược vào artifact

Artifact render mới hiện dùng envelope theo `artifacts/default.yml`, thay vì chỉ giữ nguyên source-rule shape như các artifact cũ.

## CLI hiện có

Các lệnh chính đang có trong `project-root/`:

- `python project-root/main.py load-tenant --tenant-id <tenant>`
- `python project-root/main.py gen-artifact --tenant-id <tenant>`
- `python project-root/main.py export-rules --tenant-id <tenant>`
- `python project-root/main.py deploy-rules --tenant-id <tenant>`
- `python project-root/main.py validate-tenant --tenant-id <tenant>`
- `python project-root/main.py validate-rules --all`

`export-rules` hiện là alias legacy của `gen-artifact`.

## Cấu trúc thư mục

```text
.
|-- artifacts/
|   |-- default.yml
|   |-- <tenant>/
|   |   `-- tenant-rules/
|   `-- legacy/
|-- docs/
|   |-- architecture/
|   `-- note/
|-- execution/
|   `-- <siem>/
|       |-- defaults.yaml
|       |-- rule-overrides.yaml
|       `-- legacy/
|-- mappings/
|   |-- detections/
|   `-- legacy/
|-- project-root/
|   |-- app/
|   |-- domain/
|   |-- infrastructure/
|   |-- interfaces/
|   `-- main.py
|-- rules/
|   |-- detections/
|   |-- analysts/
|   `-- legacy/
|-- schema/
|   |-- artifacts/
|   |-- mappings/
|   |-- rules/
|   `-- tenants/
|-- tenants/
|   `-- <tenant>/
|       |-- tenant.yaml
|       |-- devices/
|       |-- logsources/
|       |-- bindings/
|       |-- overrides/
|       `-- deployments/
`-- tests/
```

## Tài liệu nên đọc trước

Nếu muốn hiểu repo nhanh và đúng, nên đọc theo thứ tự:

1. `docs/architecture/project-architecture.md`
2. `docs/architecture/rule-rendering-flows.md`
3. `docs/architecture/tenants-relationship.md`
4. `docs/architecture/mappings-relationship.md`
5. `docs/architecture/execution-relationship.md`
6. `README.en.md` nếu cần bản tiếng Anh

## Codex Skills

Repo hiện có một số repo-local Codex Skills trong `.codex/skills/` để hỗ trợ làm việc đúng layer và đúng workflow của dự án.

- README này chỉ mô tả ngắn để người đọc biết chúng tồn tại.
- Tài liệu chi tiết nằm tại `docs/codex-skills.md`.
- Khi làm việc với OCSF-driven mapping qua skill `detection-mapping-ocsf`, nên clone `ocsf-schema` vào `.tmp/ocsf-schema` để skill dùng local reference ổn định.
- Khi cập nhật skill, nên giữ chúng bám sát `docs/architecture/` và current repository contracts.

## Ghi chú cho contributor

- Không xem `artifacts/` là source of truth.
- Không xem `rules/legacy/` hay `artifacts/legacy/` là mô hình chính của repo.
- Khi sửa README hoặc document, giữ nguyên định hướng kiến trúc trong `docs/architecture/`.
- Khi mô tả current state, phân biệt rõ:
  - `target architecture`
  - `current operational flow`
  - `legacy or transitional content`

## Tóm tắt

Repo hiện đã có runtime flow thực dụng cho render và export theo tenant, nhưng vẫn đang trong giai đoạn chuyển tiếp lên kiến trúc đầy đủ. Kiến trúc nền không đổi; tài liệu nên phản ánh đúng hai điều cùng lúc:

- thiết kế dài hạn của repository
- trạng thái implementation đang vận hành được hôm nay
