# Detection Rules

Thư mục `rules/` chứa các detection rule độc lập với SIEM và vendor,
được thiết kế để triển khai tự động thông qua kiến trúc Detection as Code (DaC).

## Nguyên tắc thiết kế

- Rule **KHÔNG phụ thuộc** vào:
  - Vendor log (Fortinet, Palo Alto, Microsoft, …)
  - SIEM (Splunk, Elastic, Sentinel, …)
- Rule chỉ sử dụng các field trừu tượng được định nghĩa trong `rule-view/`
- Mọi ánh xạ tới log gốc được xử lý thông qua:
  - `rule-view/` (rule field → OCFS)
  - `logsource-mapping-registry/` (vendor field → OCFS)

## Cấu trúc thư mục

rules/
├── detection/ # Detection rules phục vụ alerting
├── hunting/ # Hunting rules phục vụ phân tích chủ động
├── dfir/ # Rules phục vụ điều tra & phản ứng sự cố
├── deprecated/ # Rules đã ngừng sử dụng

## Cấu trúc một rule

Mỗi rule được định nghĩa bằng một file YAML với các thành phần chính:

### 1. Metadata

- `id`: Định danh duy nhất của rule
- `name`: Tên rule
- `severity`: Mức độ nghiêm trọng
- `status`: experimental / stable / deprecated

### 2. Abstraction Layer

- `view`: Rule View được sử dụng (ví dụ: `firewall`, `endpoint`)
- `platform`: Domain logic của rule (network, endpoint, identity)
- `service`: Nhóm semantic log (traffic, process, authentication)

### 3. Detection Logic

Phần `detection` chỉ sử dụng các field được định nghĩa trong `rule-view/`.

Ví dụ:

```yaml
detection:
  selection:
    dst.port: 443
    action: accept
  condition: selection

Vòng đời của rule
Rule
  ↓
Rule View (rule-view/)
  ↓
OCFS
  ↓
Vendor Mapping (logsource-mapping-registry/)
  ↓
SIEM

Luồng test triển khai Phase 1:
load tenant config trong tenant-manager => define device,vendor,logsource -> map to ./rules
read ./rules
map ./rule-views => rule field -> oscf.field
map ./logsource-mapping-registry => oscf.field -> siem field
export to siem-rule.json
=> deploy to siem