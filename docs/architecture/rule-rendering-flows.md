# Các luồng Render Rule

> Tài liệu này giữ nguyên thiết kế kiến trúc hai luồng render hiện tại: một luồng mục tiêu dài hạn và một luồng hardcoded-query đang vận hành được.

## 1. Mục đích

Repository hiện cần mô tả đồng thời hai cách hiểu về render rule:

- luồng chuẩn dài hạn, hướng tới tách semantic rule khỏi query implementation
- luồng hardcoded query đang chạy được trong implementation hiện tại, đặc biệt với Splunk

Giữ cả hai cách mô tả giúp tài liệu phản ánh đúng hiện trạng mà không làm mất định hướng kiến trúc.

## 2. Luồng chuẩn không dùng hardcoded query

Đây là luồng mục tiêu ở mức kiến trúc. Nó ưu tiên separation giữa content, mapping, tenant context, execution, và converter.

Trình tự mục tiêu:

1. Nạp tenant config từ `tenants/<tenant>/`.
2. Xác định `tenant_id`, `siem_id`, device, và dataset.
3. Nạp semantic rules từ `rules/`.
4. Nạp detection mappings từ `mappings/detections/`.
5. Resolve ingest binding từ `tenants/.../bindings/ingest/`.
6. Resolve field binding từ `tenants/.../bindings/fields/`.
7. Áp tenant filter hoặc tenant override nếu có.
8. Dùng converter hoặc renderer để sinh query theo SIEM từ semantic rule.
9. Resolve execution policy từ `execution/<siem>/`.
10. Render output vào `artifacts/<tenant>/tenant-rules/`.

Luồng này giữ separation tốt nhất giữa:

- semantic rule
- field mapping
- execution policy
- tenant-specific tuning

## 3. Luồng thực tế dùng hardcoded query

Đây là luồng đang khả dụng trong implementation hiện tại của `project-root/`.

Trình tự thực tế:

1. Nạp source rule từ `rules/detections/` và `rules/analysts/`.
2. Chỉ chọn các rule có status phù hợp với current render flow, hiện chủ yếu là `stable`.
3. Đọc hardcoded query từ `x_query` hoặc execution payload đã có sẵn theo SIEM hiện tại.
4. Resolve ingest binding để bổ sung `index`, `sourcetype`, `device_id`, `dataset_id`.
5. Chỉ render các target có field binding hợp lệ.
6. Resolve execution config theo thứ tự:

```text
execution/<siem>/defaults.yaml
  <= execution/<siem>/rule-overrides.yaml
  <= tenants/<tenant>/overrides/execution/...
```

7. Sinh output vào `artifacts/<tenant>/tenant-rules/` theo envelope artifact hiện tại.
8. Refresh `deployments/rule-deployments.yaml`.
9. Đồng bộ trạng thái `enabled` từ deployment manifest ngược vào artifact.

## 4. Phân tách vai trò giữa các lớp

Trong current hardcoded-query flow:

- `rules/` giữ detection intent
- `rules/analysts/` giữ correlation hoặc analyst logic
- `mappings/` và `bindings/fields/` giữ contract field
- `bindings/ingest/` giữ ingest target thực tế
- `execution/` giữ metadata thực thi như schedule, severity, risk score
- `deployments/rule-deployments.yaml` giữ quyết định enablement cuối cùng
- `artifacts/` giữ output cuối cùng sau render

## 5. Ghi chú quan trọng

- Hardcoded query là execution artifact chuyển tiếp, không thay thế semantic rule.
- Việc giữ hai luồng không có nghĩa kiến trúc bị thay đổi; đây là cách tài liệu phản ánh đúng cả target design lẫn current operational state.
- Artifact hiện tại nên được hiểu theo `artifacts/default.yml`, không theo flattened legacy artifacts.

## 6. Kết luận

Ở thời điểm hiện tại, cả hai luồng đều cần được giữ trong tài liệu:

- luồng chuẩn là đích kiến trúc dài hạn
- luồng hardcoded query là luồng triển khai thực tế đang vận hành

Nhờ vậy, repository có thể giữ nguyên thiết kế kiến trúc trong khi tài liệu vẫn phản ánh đúng trạng thái implementation hiện tại.
