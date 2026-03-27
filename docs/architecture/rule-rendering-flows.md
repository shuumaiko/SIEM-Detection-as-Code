# Các luồng Render Rule

> Tài liệu này mô tả 2 luồng render rule đang tồn tại trong định hướng kiến trúc hiện nay.

## 1. Mục đích

Hiện tại repository có 2 cách hiểu về render rule:

- một luồng chuẩn không dùng hardcoded query, đang ở mức ý tưởng
- một luồng thực tế đang dùng hardcoded query, đặc biệt với Splunk

Tài liệu này tách riêng phần đó để tránh làm phình các tài liệu kiến trúc nền.

## 2. Luồng chuẩn không dùng hardcoded query

Đây là luồng mục tiêu ở mức kiến trúc, nhưng hiện chưa hoàn thiện end-to-end.

Trình tự dự kiến:
<!-- Đề xuất chuyển phase mapping xuống ngay trước phase convert, như vậy sẽ thì luồng thực tế sẽ là luồng gốc nhưng skip phần convert -->
1. Nạp tenant config từ `tenants/<tenant>/`.
2. Xác định `tenant_id`, `siem_id`, danh sách device, và danh sách dataset.
3. Nạp semantic rules từ `rules/`.
4. Nạp detection mappings từ `mappings/detections/`.
5. Resolve ingest binding từ `tenants/.../bindings/ingest/`.
6. Resolve field binding từ `tenants/.../bindings/fields/`.
7. Áp tenant filter hoặc tenant logic override nếu có.
8. Dùng converter hoặc renderer để sinh query theo SIEM từ semantic rule.
9. Resolve execution policy từ `execution/<siem>/`.
10. Render output vào `artifacts/<tenant>/tenant-rules/`.

Luồng này giữ separation tốt nhất giữa:

- semantic rule
- field mapping
- execution policy
- tenant-specific tuning

## 3. Luồng thực tế dùng hardcoded query

Đây là luồng đang khả thi hơn trong giai đoạn hiện tại, đặc biệt với Splunk.

Trình tự thực tế:

1. Nạp base detection rule từ `rules/detections/`.
2. Nếu rule có analyst layer liên quan, resolve analyst rule từ `rules/analysts/`.
3. Xác định hardcoded query theo thứ tự override:

```text
rule
  <= analyst rule nếu có
  <= tenant filter nếu có
```

4. Sau khi có query cuối cùng, áp mapping cần thiết để resolve field và logic ràng buộc theo tenant.
5. Resolve ingest binding để bổ sung `index` và `sourcetype`.
6. Resolve execution config theo thứ tự:

```text
execution/<siem>/defaults.yaml
  <= execution/<siem>/rule-overrides.yaml
  <= tenants/<tenant>/overrides/execution/...
```

7. Sinh output cuối vào `artifacts/<tenant>/tenant-rules/`.

## 4. Phân tách vai trò giữa các lớp

Trong luồng hardcoded query hiện tại:

- `rules/` quyết định detection intent
- `rules/analysts/` có thể override hoặc mở rộng logic ở mức semantic
- `tenants/.../overrides/filter/` có thể tinh chỉnh query cuối theo tenant
- `mappings/` và `bindings/` dùng để resolve field và ingest target
- `execution/` quyết định metadata thực thi như schedule, severity, risk score

## 5. Ghi chú quan trọng

- hardcoded query là execution artifact được chấp nhận có chủ đích trong giai đoạn hiện tại
- hardcoded query không thay thế semantic rule
- `execution/` không quyết định detection logic
- tenant override là lớp tuning cuối cùng theo ngữ cảnh vận hành

## 6. Kết luận

Ở thời điểm hiện tại, cả hai luồng đều cần được ghi nhận:

- luồng chuẩn là mục tiêu kiến trúc dài hạn
- luồng hardcoded query là luồng vận hành thực tế đang dùng

Việc mô tả rõ cả hai giúp repository phản ánh đúng hiện trạng mà không đánh mất định hướng chuẩn hóa về sau.
