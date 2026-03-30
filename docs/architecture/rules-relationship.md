# Kiến trúc thành phần Rules

> Tài liệu này mô tả lớp `rules/` trong trạng thái hiện tại của repository.

## 1. Mục đích và phạm vi

Tài liệu này xác định vai trò, cấu trúc, và nguyên tắc tổ chức của thư mục `rules/` trong repository `SIEM-Detection-as-Code`.

Phạm vi của tài liệu bao gồm:

- cấu trúc thư mục của lớp `rules/`
- ý nghĩa của từng nhóm rule
- cách dùng `rule_type`
- ranh giới giữa semantic rule và execution artifact
- quan hệ giữa `rules/`, `mappings/`, `execution/`, và `tenants/`

## 2. Vai trò của `rules/`

`rules/` là lớp semantic content của hệ thống.

Vai trò chính:

- lưu detection knowledge gốc
- giữ detection intent ở mức tương đối độc lập với SIEM
- cung cấp semantic rule để các lớp `mappings/`, `execution/`, và `tenants/` dùng trong quá trình render

Nguyên tắc cốt lõi:

- `rules/` không phải là nơi chứa execution metadata
- `rules/` không phải là nơi chứa tenant-specific tuning
- `rules/` là nguồn chuẩn của semantic rule, còn `artifacts/` chỉ là output đã render

## 3. Cấu trúc hiện tại

Hiện trạng thư mục:

```text
rules/
  detections/
    <domain or category>/
      ...
  analysts/
    <domain>/
      ...
  legacy/
    ...
```

Ý nghĩa:

- `rules/detections/`: detection rule và detection base đang dùng
- `rules/analysts/`: analyst rule chứa correlation hoặc logic tổng hợp
- `rules/legacy/`: content cũ, dùng làm tham chiếu hoặc chuyển đổi

## 4. Phân loại rule hiện tại

Trong trạng thái hiện tại, semantic rule được phân biệt bằng `rule_type`.

Các giá trị đang phù hợp với kiến trúc:

- `detection`
- `detection_base`
- `analyst`

## 5. `detection`

`rule_type: detection` là detection rule hoàn chỉnh, có thể đứng độc lập như một detection intent hoàn chỉnh.

Đặc điểm:

- có `logsource`
- có `detection`
- có `level`
- có thể có `x_query` như execution artifact chuyển tiếp

Ví dụ hiện tại:

- `rules/detections/network/firewall/base/fw_connection_port_23.yaml`
- `rules/detections/category/antivirus/av_hacktool.yaml`

## 6. `detection_base`

`rule_type: detection_base` là building block cho analyst rule.

Mục tiêu:

- giữ logic detection nền
- cho phép analyst rule tái sử dụng mà không cần lặp lại điều kiện
- không nhất thiết được triển khai như một alert độc lập

Nguyên tắc:

- `detection_base` là semantic object hợp lệ
- `detection_base` không nên bị dùng `level` như một cách phân loại thay cho `rule_type`
- việc có deploy trực tiếp hay không là quyết định của pipeline hoặc policy, không phải lý do để bỏ semantic layer này

## 7. `analyst`

`rule_type: analyst` là rule tổng hợp ở mức analyst-facing.

Đặc điểm:

- chứa correlation hoặc logic tổng hợp
- có thể tham chiếu tới detection rule hoặc detection base khác
- thể hiện detection intent ở mức aggregation, threshold, sequence, grouping

Ví dụ hiện tại:

- `rules/analysts/network/firewall/base/net_fw_request_reached_over_threshold.yaml`

Trong rule loại này, block `correlation:` là semantic logic thực thụ, không phải execution metadata.

## 8. Quan hệ giữa `detection` và `analyst`

Quan hệ logic hiện tại có thể được hiểu như sau:

```text
detection rule
  -> có thể đứng độc lập

detection base
  -> thường được analyst rule tái sử dụng

analyst rule
  -> gọi đến detection base hoặc detection rule khác
  -> bổ sung logic correlation / threshold / aggregation
```

Nói ngắn gọn:

- `detection` trả lời câu hỏi phát hiện hành vi gì
- `analyst` trả lời câu hỏi analyst cần nhìn thấy tín hiệu tổng hợp nào

## 9. Metadata chung của rule

Một semantic rule thường có các thành phần sau:

- `title`
- `id`
- `rule_type`
- `status`
- `description`
- `references`
- `author`
- `date`
- `modified`
- `tags`
- `logsource` hoặc `correlation`
- `fields`
- `level`

Không phải mọi rule đều cần đủ mọi block, nhưng đây là bộ metadata điển hình đang được dùng.

## 10. Vai trò của `id`

`id` là identity chính của rule.

Nguyên tắc:

- `id` nên ổn định hơn filename
- filename ưu tiên readability
- `id` dùng để map với execution override, deployment manifest, hoặc các lớp quản lý khác

Với rule từ upstream như Sigma, ELK, YARA:

- giữ `id` gốc nếu detection intent vẫn là cùng một rule
- tạo `id` mới nếu rule đã trở thành object semantic mới

## 11. Vai trò của `x_query`

Trong hiện trạng hiện tại, `x_query` hoặc hardcoded query trong rule là execution artifact chuyển tiếp.

Điều đó có nghĩa:

- semantic rule vẫn nằm ở `detection` hoặc `correlation`
- query hardcode là cách vận hành tạm thời trên SIEM
- `x_query` không thay thế vai trò của `execution/`

Nói ngắn gọn:

- `rules/` giữ meaning
- `x_query` giữ execution logic chuyển tiếp
- `execution/` giữ execution metadata như schedule, severity, risk score

## 12. Quan hệ với `mappings/`

`rules/` và `mappings/` đi cùng nhau theo mô hình:

```text
source rule field
  -> canonical field
  -> tenant SIEM field
```

Trong đó:

- `rules/` khai báo field nào được dùng trong semantic logic
- `mappings/` định nghĩa field đó mang nghĩa gì trong vocabulary chuẩn

## 13. Quan hệ với `execution/`

`rules/` không nên chứa execution metadata như:

- schedule
- earliest/latest
- notable severity
- risk score

Các phần này thuộc `execution/`.

Tuy nhiên, trong giai đoạn hiện tại, `rules/` vẫn có thể chứa `x_query` như execution artifact tạm thời do converter tổng quát chưa hoàn thiện.

## 14. Quan hệ với tenant filter và tenant overrides

`rules/` là semantic rule gốc.

Khi render thực tế:

- tenant filter hoặc `overrides/filter/` có thể tinh chỉnh logic theo ngữ cảnh tenant
- trong hardcoded-query flow hiện tại, `overrides/filter/` có thể thay trực tiếp `search_query` trước bước map field `source rule field -> canonical field -> tenant SIEM field`
- tenant execution override có thể tinh chỉnh metadata thực thi

Nhưng các lớp đó không thay thế semantic ownership của `rules/`.

## 15. Quan hệ với `legacy/`

`rules/legacy/` là nhánh lịch sử.

Vai trò:

- giữ nội dung cũ để tham chiếu
- hỗ trợ quá trình migrate sang taxonomy mới
- cung cấp bối cảnh thiết kế hoặc logic cũ cho việc chuẩn hóa

Nguyên tắc:

- `legacy/` không nên là nguồn chuẩn chính cho rule mới
- semantic rule mới nên đi vào `rules/detections/` hoặc `rules/analysts/`

## 16. Quy tắc tổ chức thư mục

Nguyên tắc tổ chức nên giữ:

- taxonomy của `rules/` phải đủ ổn định để `mappings/`, `execution/`, và `tenants/overrides/` có thể mirror hoặc tham chiếu
- detection rule và analyst rule nên tách thư mục riêng
- folder structure nên ưu tiên readability hơn là encode quá nhiều kỹ thuật vào filename

## 17. Kết luận

Trong kiến trúc hiện tại:

- `rules/` là semantic layer của repository
- `rules/detections/` giữ detection rule và detection base
- `rules/analysts/` giữ analyst rule với correlation logic
- `rules/legacy/` giữ content lịch sử để tham chiếu hoặc chuyển đổi
- `x_query` là execution artifact chuyển tiếp, không thay thế semantic rule

Tài liệu này là chuẩn tham chiếu cho mọi thay đổi liên quan đến taxonomy của rule, `rule_type`, semantic ownership của detection logic, và ranh giới giữa rule content với execution metadata.
