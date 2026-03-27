# Kiến trúc thành phần Execution

> Tài liệu này mô tả lớp `execution/` trong trạng thái hiện tại của repository.

## 1. Mục đích

`execution/` là lớp cấu hình thực thi theo SIEM. Lớp này không định nghĩa detection intent, mà định nghĩa cách một semantic rule được chạy trên SIEM cụ thể.

## 2. Vai trò

`execution/` dùng để chứa:

- schedule như `cron`, `earliest`, `latest`
- notable metadata như `enabled`, `severity`, `risk_score`
- policy mặc định theo SIEM
- override execution theo từng rule

Trong giai đoạn hiện tại, `execution/` được dùng rõ nhất ở nhánh `execution/splunk/`.

## 3. Cấu trúc hiện tại

```text
execution/
  splunk/
    defaults.yaml
    rule-overrides.yaml
    legacy/
      ...
```

Ý nghĩa:

- `defaults.yaml`: policy mặc định của Splunk
- `rule-overrides.yaml`: các ngoại lệ execution theo `rule_id`
- `legacy/`: execution artifact hoặc file chuyển tiếp từ mô hình cũ

## 4. Quan hệ với rule và tenant

`execution/` là lớp chung theo SIEM, không phải cấu hình riêng của tenant.

Khi render một rule, execution config được resolve theo thứ tự:

1. `execution/<siem>/defaults.yaml`
2. `execution/<siem>/rule-overrides.yaml`
3. `tenants/<tenant>/overrides/execution/...`

Tức là:

```text
execution defaults
  <= rule-specific execution override
  <= tenant-specific execution override
```

## 5. Quan hệ với hardcoded query

Trong giai đoạn hiện tại, hardcoded query hoặc hardcoded SPL vẫn là execution artifact hợp lệ. Tuy nhiên:

- hardcoded query không thay thế semantic rule
- hardcoded query không thay thế execution metadata
- `execution/` vẫn là lớp riêng để chứa schedule, notable, severity, risk score

Nói ngắn gọn:

- query trả lời câu hỏi rule chạy logic gì trên SIEM
- execution trả lời câu hỏi rule được vận hành như thế nào trên SIEM

## 6. Quan hệ với tenant overrides

Tenant override là lớp tuning cuối cùng, được tách riêng trong:

```text
tenants/
  <tenant>/
    overrides/
      execution/
        <siem>/
          ...
```

Vai trò của tenant execution override:

- điều chỉnh cron riêng cho tenant
- điều chỉnh severity hoặc risk score theo ngữ cảnh vận hành
- điều chỉnh notable behavior mà không thay đổi execution config gốc của rule

## 7. Kết luận

Trong kiến trúc hiện tại:

- `execution/` là lớp cấu hình thực thi theo SIEM
- `execution/` không thay thế semantic rule
- `execution/` không thay thế tenant override
- `execution/` là input config, không phải output artifact

Tài liệu này là chuẩn tham chiếu cho mọi thay đổi liên quan đến default execution policy, rule-specific execution override, và tenant-specific execution tuning.
