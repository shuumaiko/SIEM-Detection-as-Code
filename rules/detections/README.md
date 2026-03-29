# Detection Rules

Thư mục `rules/detections/` chứa detection content chuẩn của repository.

## Vai trò

- lưu detection intent có thể tái sử dụng
- tách detection logic khỏi tenant-specific deployment detail
- làm đầu vào cho flow render sang artifact theo tenant

## Kiểu rule hiện có

- `rule_type: detection`: detection deployable
- `rule_type: base`: detection building block dùng để tái sử dụng hoặc tham chiếu

Ngoài `rules/detections/`, repo còn có `rules/analysts/` cho analyst correlation content.

## Cấu trúc dữ liệu hiện tại

Các rule hiện tại là file YAML một document, thường chứa:

- metadata như `title`, `name`, `id`, `status`, `author`, `date`, `modified`
- `rule_type`
- `logsource`
- `detection`
- `fields`
- `falsepositives`
- `level`
- `x_query` như execution artifact chuyển tiếp

## Nguyên tắc

- Không nhúng assumption riêng của tenant vào rule tái sử dụng.
- Không coi hardcoded query là semantic source of truth; đây là execution artifact chuyển tiếp nhưng hợp lệ trong current flow.
- Giữ taxonomy và folder placement nhất quán với `docs/architecture/`.

## Liên hệ với các lớp khác

- `mappings/detections/` nối source rule fields với canonical fields
- `tenants/.../bindings/fields/` nối canonical fields với field thực tế trên SIEM
- `project-root/` dùng detection rule để render artifact cho tenant

## Tham chiếu

- `docs/architecture/rules-relationship.md`
- `docs/architecture/rule-rendering-flows.md`
