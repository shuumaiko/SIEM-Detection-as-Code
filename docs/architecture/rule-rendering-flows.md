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
10. Render output vào `artifacts/<tenant>/<siem-id>/`.

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
3. Đọc hardcoded query từ `x_query` hoặc payload SIEM-specific đã có sẵn trên rule.
4. Nếu có tenant filter override trong `tenants/<tenant>/overrides/filter/`, dùng `query_modifiers.<siem>.search_query` để override hardcoded query trước bước map field.
5. Resolve ingest binding để bổ sung `index`, `sourcetype`, `device_id`, `dataset_id`.
6. Chỉ render các target có field binding hợp lệ và rewrite field trong hardcoded query theo chuỗi:

```text
source rule field
  -> canonical field
  -> tenant SIEM field
```

7. Resolve execution config theo thứ tự:

```text
execution/<siem>/defaults.yaml
  <= execution/<siem>/rule-overrides.yaml
  <= tenants/<tenant>/overrides/execution/...
```

8. Sinh output vào `artifacts/<tenant>/<siem-id>/` theo envelope artifact hiện tại.
9. Refresh `deployments/rule-deployments.yaml`.
10. Đồng bộ trạng thái `enabled` từ deployment manifest ngược vào artifact.

## 4. Phân tách vai trò giữa các lớp

Trong current hardcoded-query flow:

- `rules/` giữ detection intent
- `rules/analysts/` giữ correlation hoặc analyst logic
- `mappings/` và `bindings/fields/` giữ contract field
- `bindings/ingest/` giữ ingest target thực tế
- `execution/` giữ metadata thực thi như schedule, severity, risk score
- `deployments/rule-deployments.yaml` giữ quyết định enablement cuối cùng
- `artifacts/` giữ output cuối cùng sau render, hiện theo root `artifacts/<tenant>/<siem-id>/`

## 5. Ghi chú quan trọng

- Hardcoded query là execution artifact chuyển tiếp, không thay thế semantic rule.
- Trong hardcoded-query flow hiện tại, `tenants/<tenant>/overrides/filter/` có thể override trực tiếp `search_query` trước bước field mapping.
- Engine hiện tại mới consume phần `query_modifiers.<siem>.search_query` của tenant filter override; các block như `detection_filters` và `append_condition` vẫn là contract dữ liệu, chưa được dựng thành semantic render flow tổng quát.
- Việc giữ hai luồng không có nghĩa kiến trúc bị thay đổi; đây là cách tài liệu phản ánh đúng cả target design lẫn current operational state.
- Artifact hiện tại nên được hiểu theo `artifacts/default.yml`, không theo flattened legacy artifacts.

## 6. Kết luận

Ở thời điểm hiện tại, cả hai luồng đều cần được giữ trong tài liệu:

- luồng chuẩn là đích kiến trúc dài hạn
- luồng hardcoded query là luồng triển khai thực tế đang vận hành

Nhờ vậy, repository có thể giữ nguyên thiết kế kiến trúc trong khi tài liệu vẫn phản ánh đúng trạng thái implementation hiện tại.
