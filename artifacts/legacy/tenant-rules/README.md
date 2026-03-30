# Legacy Tenant Artifacts

Thư mục này giữ các artifact lịch sử hoặc compatibility fixtures từ mô hình cũ.

## Cách hiểu đúng

- Đây không phải là source of truth của repository.
- Đây không phải là shape artifact chuẩn mới.
- Nội dung ở đây có thể vẫn dùng flattened rule shape thay vì artifact envelope trong `artifacts/default.yml`.

## Khi nào dùng

- tra cứu lịch sử
- so sánh drift giữa legacy artifact và flow render hiện tại
- giữ fixture tương thích khi cần review migration

## Khi nào không dùng

- không dùng làm mẫu để viết artifact mới
- không dùng để suy ra contract hiện tại của artifact
- không chỉnh tay ở đây nếu mục tiêu là thay đổi flow render chính

Artifact hiện tại của tenant nên được hiểu từ:

- `artifacts/default.yml`
- `artifacts/<tenant>/tenant-rules/`
- `schema/artifacts/artifact.schema.json`
