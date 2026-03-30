# Tenants

Thư mục `tenants/` chứa cấu hình đầu vào theo tenant cho repository `SIEM-Detection-as-Code`.

## Vai trò

Lớp dữ liệu này được dùng để:

- xác định tenant đang dùng SIEM nào
- mô tả device và logsource thuộc tenant
- ánh xạ dataset logic vào ingest model thực tế trên SIEM
- ánh xạ canonical field sang field thực tế của tenant
- áp filter và override theo tenant trong quá trình render
- xác định tập rule bật hoặc tắt theo tenant và theo SIEM

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
    overrides/
      execution/
        <siem>/
          ...
      filter/
        detections/
          ...
        analysts/
          ...
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

- là đường dẫn kiến trúc gốc cho tenant-specific filter

`overrides/filter/`

- là đường dẫn tuning filter đang được dùng nhiều hơn trong dữ liệu và flow chuyển tiếp hiện tại

`overrides/execution/`

- lưu delta execution metadata như schedule, severity, risk score, enabled

`deployments/rule-deployments.yaml`

- lưu quyết định bật hoặc tắt rule theo SIEM
- là nguồn quyết định enablement cuối cùng cho artifact sau render

## Tenant hiện có

Hiện tại repo có tenant ví dụ:

- `lab/`
- `demo/`

Trong đó:

- `lab/` là tenant tham chiếu chính cho nhiều test và flow kỹ thuật
- `demo/` là tenant output mẫu để review artifact và deployment state

## Quan hệ với các lớp khác

- `rules/` cung cấp source detection content
- `mappings/` cung cấp lớp chuẩn hóa field ở phía content
- `tenants/` cung cấp hiện trạng triển khai thực tế của từng tenant
- `artifacts/` lưu output đã được render cho tenant

## Tài liệu tham chiếu

- `docs/architecture/tenants-relationship.md`
- `docs/en/architecture/tenants-relationship.md`

## Ghi chú current state

- Kiến trúc tenant layer vẫn giữ `filters/`, `overrides/`, và `deployments/` là các lớp riêng.
- Implementation hiện tại trong `project-root/` đọc `deployments/rule-deployments.yaml` như deployment manifest chính.
- Sau khi render artifact, trạng thái `enabled` trong artifact được sync lại từ deployment manifest.
