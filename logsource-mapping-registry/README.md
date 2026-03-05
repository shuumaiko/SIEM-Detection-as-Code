# LogSource Mapping Registry
<!-- Phục vụ chuẩn hóa log trên SIEM -->
Thư mục `logsource-mapping-registry/` là **source of truth** cho toàn bộ
việc ánh xạ (mapping) log gốc từ các vendor / product khác nhau
sang schema chuẩn **OCFS**.

Layer này chịu trách nhiệm **chuẩn hóa semantic của log** và
tách biệt hoàn toàn detection rule khỏi vendor, agent và SIEM.

---

## Mục tiêu

- Chuẩn hóa field log từ nhiều nguồn khác nhau về một schema thống nhất (OCSF)
- Cho phép viết detection rule **không phụ thuộc vendor**
- Hỗ trợ triển khai tự động (Detection as Code – DaC)

---

## Nguyên tắc thiết kế

- Mapping **chỉ chứa ánh xạ field**, không chứa logic detection
- Mapping **không phụ thuộc SIEM** (Splunk, Elastic, Sentinel, …)
- Mapping **không phụ thuộc rule**
- Mỗi mapping đại diện cho **một logsource có semantic nhất quán**

---

## Cấu trúc thư mục

logsource-mapping-registry/
├── README.md
├── _schema/ # Schema & definition cho mapping
│ ├── mapping.schema.yaml # Schema validate mapping
│ └── ocfs.fields.yaml # Danh sách field OCFS chuẩn
├── vendors/
│ ├── microsoft/
│ │ └── windows/
│ │ └── security/
│ │ └── mapping.yaml
│ ├── fortinet/
│ │ └── fortigate/
│ │ └── traffic/
│ │ └── mapping.yaml
│ └── paloalto/
│ └── pan-os/
│ └── traffic/
│ └── mapping.yaml

---

## Phân tầng logsource

Mỗi mapping được định danh theo ba lớp:

| Tầng | Ý nghĩa |
|----|----|
| `vendor` | Đơn vị định nghĩa schema log gốc |
| `product` | Sản phẩm cụ thể của vendor |
| `service` | Nhóm log có semantic nhất quán |

Ví dụ:

vendors/fortinet/fortigate/traffic/

- `vendor`: fortinet
- `product`: fortigate
- `service`: traffic

---

## Cấu trúc một file mapping

```yaml
logsource:
  vendor: fortinet
  product: fortigate
  service: traffic

mapping:
  srcip: ocfs.source.ip
  dstip: ocfs.destination.ip
  srcport: ocfs.source.port
  dstport: ocfs.destination.port
  action: ocfs.event.action

status: stable
version: 1.0

## Vòng đời sử dụng mapping
Log gốc (vendor)
  ↓
LogSource Mapping Registry
  ↓
OCFS (semantic layer)  <===> SIEM Fields
  ↓
Rule View (rule-view/)
  ↓
Detection Rule
  ↓
SIEM

# Ý tưởng và vấn đề về mapping ocsf

Viết schema map log <=> ocsf (excl phân tích log)
  => field k map đc vào ocsf 
    PA1: sử dụng ocsf custom field định dạng ocsf.
    => ocsf.custom field có nên đc sử dụng k? Nếu sử dụng thì dùng cơ chế nào để quản lý custom field này để tránh xung đột với rule gốc (maintain? version? xung đột với ocsf)
    PA2: Bỏ qua?
    PA3: Trong case của SIEM
    Rule ==> Rule Field ==(Data view)==> ocsf field ==(mapping - LogSource Mapping Registry)==> Log Field (Requirement)
      => field ocsf đủ hỗ trợ không? (đủ - cần confirm)
      => phát triển thêm rule -> log field req mở rộng -> quản lý và maintain thông qua version
Thông qua PA3 - Task:
  - Define tạm thời log field req, rule field req, ocsf mapping cho 2 phần trên (logsource mapping + data-view)
Define mapping trong code <=> field mapping (LogSource Mapping Registry)
# case CA tool cần viết parser:
Log ==(parser tool + LogSource Mapping Registry)==> log được xử lý
