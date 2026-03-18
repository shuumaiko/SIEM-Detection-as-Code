## Contributing

Repository này hiện được phát triển theo hướng cá nhân. Vì vậy, tài liệu này mô tả nguyên tắc đóng góp ở mức tối giản và phù hợp với mô hình một maintainer chính.

## Nguyên tắc chung

- Mọi thay đổi nên bám theo kiến trúc hiện tại của repository.
- `rules/`, `mappings/`, `tenants/`, và `artifacts/` cần được xem là các lớp dữ liệu có quan hệ chặt chẽ với nhau.
- Không chỉnh tay output trong `artifacts/` nếu thay đổi đó thực chất thuộc về `rules/`, `mappings/`, hoặc `tenants/`.
- Khi thay đổi tài liệu, ưu tiên giữ văn phong rõ ràng, chuẩn hóa, và nhất quán giữa bản tiếng Việt và tiếng Anh.

## Quy trình đề xuất thay đổi

1. Fork repository hoặc tạo branch riêng để làm việc.
2. Thực hiện thay đổi ở phạm vi nhỏ và có chủ đích.
3. Kiểm tra lại các file liên quan để tránh lệch giữa rule, mapping, tenant config, và documentation.
4. Gửi Pull Request hoặc patch kèm mô tả rõ mục tiêu thay đổi.

## Phạm vi thay đổi thường gặp

### Detection content

- thêm hoặc cập nhật rule trong `rules/`
- cập nhật metadata, references, tags, hoặc detection intent

### Mapping

- cập nhật `mappings/detections/`
- cập nhật `tenants/.../bindings/fields/`
- cập nhật `tenants/.../bindings/ingest/`

### Tenant configuration

- thêm tenant mới
- cập nhật `tenant.yaml`, `devices/`, `logsources/`, `filters/`, hoặc `deployments/`

### Documentation

- cập nhật `README`
- cập nhật tài liệu trong `docs/architecture/` và `docs/en/architecture/`
- đồng bộ lại nội dung giữa bản tiếng Việt và bản tiếng Anh khi cần

## Rule Template

Template dưới đây dùng làm khung tham chiếu cho detection rule. Cấu trúc này kế thừa từ Sigma và đã được điều chỉnh để phù hợp với repository hiện tại.

```yaml
id: <UUID v4, ví dụ: 722d5f75-2b02-426a-8f24-e2a6fe47388b>
title: <Tên rule, ví dụ: 7Zip Compressing Dump File>
status: <enable|disable>
tenant:
  - tenant_a
  - tenant_b
description: <Mô tả rule>
references:
  - <Link tham chiếu 1>
  - <Link tham chiếu 2>
author: <Tên tác giả hoặc nguồn tham chiếu>
date: <Ngày tạo lần đầu, ví dụ: 2022-09-27>
modified: <Ngày cập nhật gần nhất, ví dụ: 2023-09-27>
tags:
  - <MITRE tactic>
  - <MITRE technique>
logsource:
  product: <ví dụ: windows>
  service: <ví dụ: powershell>
  category: <ví dụ: process_creation>
detection:
  selection:
    FieldName|contains: value
  condition: selection
logic: <Logic triển khai cụ thể cho EDR hoặc SIEM nếu có>
falsepositives:
  - <False positive 1>
level: medium
version: <phiên bản rule, ví dụ: 1.0>
```

Lưu ý:

- Nếu rule là base rule chuẩn, chỉ khai báo những trường thực sự cần thiết cho detection content.
- Nếu rule có logic triển khai riêng cho SIEM, phần execution artifact cần được giữ tách bạch với detection intent.
- Nếu rule được render theo tenant, thay đổi nên được thực hiện từ lớp dữ liệu gốc thay vì chỉnh trực tiếp output.

## Tài liệu tham chiếu

- Sigma: <https://sigmahq.io/docs/guide/getting-started.html>
- Kiến trúc project: [docs/architecture/project-architecture.md](/d:/My%20Project/SIEM-Detection/docs/architecture/project-architecture.md)
- Kiến trúc tenant: [docs/architecture/tenants-relationship.md](/d:/My%20Project/SIEM-Detection/docs/architecture/tenants-relationship.md)
- Kiến trúc mapping: [docs/architecture/mappings-relationship.md](/d:/My%20Project/SIEM-Detection/docs/architecture/mappings-relationship.md)

## Maintainer

Repository hiện được duy trì theo mô hình cá nhân.

Maintainer mặc định:

- Phạm Tuấn Anh
