# Tenants

Thư mục `tenants/` chứa cấu hình đầu vào theo tenant cho repository `SIEM-Detection-as-Code`.

Lớp dữ liệu này được sử dụng để:

- xác định tenant đang dùng SIEM nào
- mô tả các device và logsource thuộc tenant
- ánh xạ dataset logic vào ingest model thực tế trên SIEM
- ánh xạ canonical field sang field thực tế của tenant
- áp filter đặc thù theo tenant trong quá trình render
- xác định tập rule được bật hoặc tắt theo tenant và theo SIEM

## Cấu trúc chuẩn

```text
tenants/
  <tenant_name>/
    tenant.yaml
    devices/
      *.yaml
    logsources/
      *.yaml
    bindings/
      ingest/
        *.yaml
      fields/
        *.yml
    filters/
      detections/
        <category>/
          <product>/
            *.yaml
    deployments/
      rule-deployments.yaml
```

## Vai trò của từng nhóm file

`tenant.yaml`

- định danh tenant
- xác định `siem_id`
- lưu metadata và cấu hình mặc định ở mức tenant

`devices/`

- mô tả thiết bị hoặc platform phát sinh log
- định danh bằng `device_id`

`logsources/`

- mô tả dataset logic của từng device
- là lớp dữ liệu logic trước khi ánh xạ vào ingest model thực tế

`bindings/ingest/`

- ánh xạ `dataset_id` sang `index`, `sourcetype`, hoặc ingest target tương đương trên SIEM

`bindings/fields/`

- ánh xạ canonical field sang field thực tế của tenant trên SIEM

`filters/`

- lưu tenant-specific filter dùng trong quá trình render từ base rule

`deployments/rule-deployments.yaml`

- lưu quyết định bật hoặc tắt rule theo SIEM

## Ví dụ tenant hiện có

Hiện tại thư mục này đang có tenant:

- `lab/`

Tenant này là ví dụ tham chiếu cho mô hình tenant layer hiện tại của repository.

## Quan hệ với các lớp khác

- `rules/` cung cấp base detection rules
- `mappings/` cung cấp lớp chuẩn hóa field ở phía detection content
- `tenants/` cung cấp hiện trạng triển khai thực tế của từng tenant
- `artifacts/` lưu output đã được render cho tenant

## Tài liệu tham chiếu

Chi tiết chuẩn kiến trúc của tenant layer được mô tả tại:

- [docs/architecture/tenants-relationship.md](d:\My Project\SIEM-Detection\docs\architecture\tenants-relationship.md)
- [docs/en/architecture/tenants-relationship.md](d:\My Project\SIEM-Detection\docs\en\architecture\tenants-relationship.md)

