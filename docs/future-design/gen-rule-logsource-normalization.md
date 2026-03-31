# Thiết kế tương lai cho chuẩn hóa logsource và tối ưu hóa luồng `gen-rule`

## 1. Mục tiêu

Tài liệu này đề xuất hướng thiết kế tương lai để chuẩn hóa cách repository hiểu `logsource` giữa:

- `rules/` là semantic layer
- `tenants/` là tenant reality layer
- luồng `gen-rule` hoặc `gen-artifact` là orchestration layer

Mục tiêu của thiết kế là:

- làm rõ một rule nên khớp với tenant dataset theo contract nào
- giảm phụ thuộc vào fallback heuristic giữa `dataset.category`, `log_type`, `dataset_id`, và `device_type`
- giữ khả năng tái sử dụng detection rule giữa nhiều tenant
- dùng `Detection-Catalog.csv` như reference dictionary thay vì biến nó thành taxonomy cưỡng bức cho toàn repo
- giữ ATT&CK là lớp coverage và metadata thay vì folder taxonomy chính

## 2. Vấn đề hiện tại

Trong trạng thái hiện tại, rule được deploy theo `rule.logsource.category/product/service`, còn tenant dataset lại được mô tả bằng:

- `device.device_type`
- `device.vendor`
- `device.product`
- `dataset.dataset_id`
- `dataset.category`
- `dataset.log_type`

Engine hiện match theo logic mềm:

- rule category có thể khớp `dataset.category` hoặc `device.device_type`
- rule service có thể khớp `dataset_id`, `service`, hoặc `log_type`

Điều này đang hoạt động được, nhưng tạo ra các vấn đề:

- contract match chưa rõ ràng
- `dataset.category` vừa mang nghĩa mô tả tenant data, vừa bị dùng như rule-facing scope
- `dataset.log_type` vừa mô tả kiểu log, vừa bị dùng như `rule.logsource.service`
- các nguồn như `Detection-Catalog.csv` hoặc ATT&CK tags chưa có vị trí kiến trúc rõ ràng

## 3. Kết luận thiết kế cốt lõi

Không nên cố ép một taxonomy duy nhất cho cả:

- `catalog_logsource`
- tenant `dataset.category` và `log_type`
- rule `logsource.category/product/service`
- ATT&CK technique hoặc sub-technique

Thay vào đó, nên tách thành 4 lớp riêng.

### 3.1. Lớp source-family reference

Lớp này trả lời câu hỏi: "nguồn log này thuộc họ nguồn nào theo reference catalog?"

Field đại diện:

- `catalog_logsource`

Ví dụ:

- `NSM:Flow`
- `WinEventLog:Sysmon`
- `WinEventLog:Security`
- `AWS:CloudTrail`
- `networkdevice:syslog`
- `custom`

Vai trò:

- dùng để suy luận gợi ý ban đầu
- dùng cho onboarding và skill support
- dùng cho reporting và thống kê source coverage

Nguồn dữ liệu:

- `Detection-Catalog.csv`
- file `logsource-catalog.seed.yaml` của skill

Lớp này không phải primary matching key ở runtime.

### 3.2. Lớp tenant dataset reality

Lớp này trả lời câu hỏi: "tenant hiện đang có dataset gì và ingest như thế nào?"

Field đại diện:

- `device_type`
- `vendor`
- `product`
- `dataset_id`
- `category`
- `log_type`
- `index`
- `sourcetype`

Vai trò:

- mô tả thực tế dữ liệu tenant
- phục vụ ingest binding và field binding
- giữ naming ổn định theo tenant

`dataset_id` vẫn là tenant-local stable key. Không nên ép `dataset_id` luôn bằng tên từ catalog.

### 3.3. Lớp rule-facing normalized scope

Đây là lớp mới cần chuẩn hóa rõ ràng cho tương lai.

Lớp này trả lời câu hỏi: "dataset này có thể phục vụ những rule nào?"

Field đại diện:

- `match.category`
- `match.product`
- `match.service`

Vai trò:

- là contract chính để khớp tenant dataset với `rule.logsource`
- tách khỏi lớp mô tả tenant reality
- giảm fallback heuristic trong engine
- được đặt ở level `dataset`, không phải ở root `logsource`, vì runtime thực tế đang resolve ingest, field binding, và deploy target theo `dataset_id`

Ví dụ:

```yaml
datasets:
  - dataset_id: traffic
    category: network
    log_type: traffic
    enabled: true
    match:
      category: firewall
      product: any
      service: traffic
    metadata:
      catalog_logsource: NSM:Flow
```

Ở ví dụ này:

- `category: network` mô tả dataset theo tenant
- `match.category: firewall` là semantic scope để rule firewall khớp được

Không nên đặt `match.*` dưới `metadata.*` vì đây là contract vận hành chính để resolve rule, không phải auxiliary metadata.

### 3.4. Lớp ATT&CK overlay

Lớp này trả lời câu hỏi: "rule hoặc tenant đang cover ATT&CK nào?"

Field đại diện:

- `tags: attack.txxxx`
- `tags: attack.txxxx.xxx`

Vai trò:

- coverage reporting
- search/filter
- analyst context
- governance

ATT&CK không nên là khóa đặt folder chính của `rules/`, vì:

- một rule có thể map nhiều technique
- nhiều rule không map ATT&CK đẹp
- ATT&CK phù hợp cho metadata hơn là deployment scope

## 4. Thiết kế chuẩn cho rule-side logsource

Rule nên tiếp tục giữ contract:

```yaml
logsource:
  category: <semantic-scope>
  product: <product-scope>
  service: <service-scope>
```

Trong đó:

- `category` là semantic domain dùng để chọn loại data phù hợp cho detection
- `product` là scope vendor hoặc platform khi cần
- `service` là stream hoặc dataset semantic cần thiết cho rule

Ví dụ:

- firewall traffic rule:
  - `category: firewall`
  - `product: any`
  - `service: traffic`
- antivirus rule:
  - `category: antivirus`
  - `product: any`
  - `service: any`
- web access rule:
  - `category: webserver`
  - `product: any`
  - `service: access`

Rule-side `logsource` là semantic deploy scope. Nó không nên bị thay bằng:

- raw vendor parser name
- Detection Catalog family
- ATT&CK technique

## 5. Thiết kế chuẩn cho tenant-side logsource

Tenant logsource tương lai nên có hai lớp field:

### 5.1. Lớp mô tả tenant reality

```yaml
datasets:
  - dataset_id: traffic
    description: Firewall traffic logs
    category: network
    log_type: traffic
    enabled: true
```

### 5.2. Lớp normalized match scope

```yaml
datasets:
  - dataset_id: traffic
    description: Firewall traffic logs
    category: network
    log_type: traffic
    enabled: true
    match:
      category: firewall
      product: any
      service: traffic
    metadata:
      catalog_logsource: NSM:Flow
```

Nguyên tắc:

- `dataset_id` vẫn là key ổn định của tenant
- `category` và `log_type` vẫn giữ vai trò mô tả dữ liệu tenant
- `match.*` là normalized contract để khớp rule
- `metadata.catalog_logsource` là reference layer
- `metadata` chỉ nên giữ auxiliary fields như source-family reference, evidence, notes, provenance

### 5.3. Tránh lặp dữ liệu giữa reality và match scope

Nếu persist đầy đủ `match.category/product/service` cho mọi dataset thì có thể phát sinh lặp nghĩa, ví dụ:

- `log_type: traffic`
- `match.service: traffic`

Thiết kế tương lai nên cho phép 2 mức biểu diễn:

#### a. Full explicit match

Phù hợp khi cần contract rõ ràng tuyệt đối:

```yaml
datasets:
  - dataset_id: traffic
    category: network
    log_type: traffic
    enabled: true
    match:
      category: firewall
      product: any
      service: traffic
    metadata:
      catalog_logsource: NSM:Flow
```

#### b. Derived match với override tối thiểu

Phù hợp khi muốn giảm duplication:

```yaml
datasets:
  - dataset_id: traffic
    category: network
    log_type: traffic
    enabled: true
    match_overrides:
      category: firewall
    metadata:
      catalog_logsource: NSM:Flow
```

Trong mô hình này, engine derive:

- `match.service` từ `log_type` khi phù hợp
- `match.product` từ default như `any` hoặc từ `vendor/product`
- `match.category` từ `catalog_logsource`, `device_type`, hoặc dictionary normalize

Rồi áp `match_overrides` như delta cuối cùng.

Vì vậy, về lâu dài nên hiểu:

- `match` là normalized runtime view
- `match_overrides` là persisted delta khi cần tối ưu dữ liệu và giảm drift

Repo có thể hỗ trợ cả hai dạng trong giai đoạn migration, nhưng hướng tối ưu hơn là:

- runtime luôn làm việc với normalized `match`
- tenant source file chỉ persist override khi giá trị suy ra đã đủ tốt

## 6. Taxonomy đề xuất cho normalized scope

Không nên lấy trực tiếp Detection Catalog làm taxonomy cho `match.category`.

Taxonomy `match.category` nên là rule-facing semantic vocabulary nhỏ, ổn định, ví dụ:

- `firewall`
- `webserver`
- `antivirus`
- `endpoint`
- `windows`
- `linux`
- `cloud`
- `identity`
- `saas`
- `network`
- `threat-intelligence`
- `siem`

Taxonomy `match.service` nên là stream vocabulary ngắn, ví dụ:

- `traffic`
- `access`
- `audit`
- `sysmon`
- `security`
- `alerts`
- `api`
- `app`
- `system`
- `internal`
- `authentication`

Các giá trị này nên được vận hành như repo contract, không phải vendor contract.

## 6.1. Vì sao không đưa `match` thành `category/product/service` top-level

Mặc dù `match.*` là contract chính để khớp rule, không nên đổi tên trực tiếp thành:

- `category`
- `product`
- `service`

ở top-level dataset, vì sẽ gây nhập nhằng giữa:

- field mô tả thực tế dữ liệu tenant
- field dùng để match semantic rule

Do đó, thiết kế tương lai nên tách rõ:

- `category`, `log_type` cho tenant reality
- `match.category/product/service` cho rule-facing scope

Tách namespace như vậy giúp:

- dễ đọc YAML hơn
- giảm nhầm lẫn trong validator và code
- hỗ trợ explainability khi cần trả lời vì sao một dataset khớp với một rule

## 7. Vai trò của Detection Catalog trong thiết kế tương lai

`Detection-Catalog.csv` nên được dùng như reference dictionary để hỗ trợ normalize source.

Vai trò phù hợp:

- gợi ý `catalog_logsource`
- gợi ý `match.category`
- gợi ý `match.service`
- gợi ý starter `dataset_id_pattern`

Ví dụ:

- `NSM:Flow` -> `match.category: firewall`, `match.service: traffic`
- `WinEventLog:Sysmon` -> `match.category: endpoint`, `match.service: sysmon`
- `AWS:CloudTrail` -> `match.category: cloud`, `match.service: audit`

### 7.1. Logsource ngoài scope Detection Catalog

Logsource ngoài scope Detection Catalog không được xem là invalid.

Thiết kế nên hỗ trợ rõ:

- `catalog_logsource: custom`
- hoặc `catalog_logsource: vendor-specific`

Fallback normalize nên dựa vào:

- `device_type`
- `vendor`
- `product`
- field hints trong log thật
- naming pattern đã tồn tại trong tenant hoặc repo

Ví dụ các nhóm cần fallback:

- WAF split như `api`, `app`, `system`
- threat intel feeds
- SIEM internal sources
- custom SaaS audit exports

## 7.2. Dataset reality dùng để làm gì trong tương lai

Dataset reality không phải lớp phụ chỉ để hỗ trợ matching. Nó có giá trị vận hành riêng và nên được giữ như first-class data model.

Các use case dài hạn gồm:

- ingest modeling:
  - map `dataset_id` sang `index`, `sourcetype`, parser, pipeline ingest
- field binding scope:
  - xác định binding nào áp cho dataset nào
- data inventory:
  - tenant thật sự đang có những loại dữ liệu nào
- parser and onboarding quality:
  - kiểm tra log thật có được phân loại đúng chưa
- data governance:
  - retention, cost, priority, ownership theo loại dữ liệu
- content gap analysis:
  - tenant có data nhưng chưa có rule phù hợp
  - tenant có rule nhưng thiếu data thực tế
- explainability:
  - phân biệt rõ "log này là gì trong thực tế" với "log này được xem là gì để match rule"
- future automation:
  - gợi ý parser, field binding, detection pack, hoặc tenant onboarding template từ real dataset profile

Nói ngắn gọn:

- dataset reality phục vụ data management
- normalized match scope phục vụ rule selection

Cả hai lớp đều cần tồn tại độc lập.

## 8. Vai trò của ATT&CK trong thiết kế tương lai

ATT&CK không nên dùng để đặt thư mục chính của `rules/`.

### 8.1. Vì sao không dùng ATT&CK làm folder taxonomy chính

- một rule có thể cover nhiều kỹ thuật
- một rule có thể cover cả parent technique và sub-technique
- nhiều rule không map rõ vào ATT&CK
- ATT&CK là adversary framework, không phải deployment scope
- nếu dùng ATT&CK làm folder chính thì một thay đổi mapping có thể kéo theo move file lớn

### 8.2. ATT&CK nên đứng ở đâu

ATT&CK nên đứng ở metadata và index layer:

- `tags` trong rule
- `rule-index`
- coverage report theo tenant
- search/filter view

Luồng đúng nên là:

`tenant source -> normalized match scope -> candidate rules -> ATT&CK coverage from matched rules`

Không nên là:

`tenant source -> ATT&CK -> folder rules`

## 9. Thiết kế cho `rule-index` và `tenant-scope`

Để tối ưu hóa `gen-rule`, nên có hai lớp materialized index.

### 9.1. `rule-index`

`rule-index` là index đã flatten từ `rules/`.

Field đề xuất:

- `rule_id`
- `source_path`
- `status`
- `rule_type`
- `supported_siems`
- `logsource.category`
- `logsource.product`
- `logsource.service`
- `vendor_hints` optional
- `device_type_hints` optional
- `attack_tags`

Vai trò:

- search candidate rules nhanh
- tránh phải scan toàn bộ `rules/` mỗi lần
- hỗ trợ reporting

### 9.2. `tenant-scope`

`tenant-scope` là normalized view của tenant datasets phục vụ `gen-rule` hoặc `gen-artifact`.

Field đề xuất:

- `tenant_id`
- `solution_id` hoặc `siem_id`
- `device_id`
- `device_type`
- `vendor`
- `product`
- `dataset_id`
- `catalog_logsource`
- `category`
- `log_type`
- `match.category`
- `match.product`
- `match.service`
- `match_overrides.category` optional
- `match_overrides.product` optional
- `match_overrides.service` optional
- `index`
- `sourcetype`
- `candidate_rule_ids`

Vai trò:

- tách bước normalize tenant data khỏi bước render rule
- tạo đầu vào ổn định cho pipeline
- hỗ trợ explainability vì có thể chỉ ra vì sao một dataset khớp rule nào

## 10. Luồng `gen-rule` tương lai

Luồng tương lai nên tách thành các bước rõ ràng.

### Bước 1. Load tenant reality

Đọc:

- `tenant.yaml`
- `devices/*.yaml`
- `logsources/*.yaml`
- `bindings/ingest/*.yaml`
- `bindings/fields/*.yml`

### Bước 2. Normalize tenant scope

Từ mỗi dataset, suy ra:

- `catalog_logsource`
- `match.category`
- `match.product`
- `match.service`

Nếu tenant source chỉ có `match_overrides`, engine phải:

1. derive `match.*` từ dictionary + heuristic
2. apply `match_overrides.*`
3. materialize normalized view vào `tenant-scope` hoặc log debug

### Bước 3. Build hoặc load `rule-index`

Flatten `rules/` thành index theo `logsource.category/product/service` và ATT&CK tags.

### Bước 4. Resolve candidate rules

Match:

- `tenant.match.category` <-> `rule.logsource.category`
- `tenant.match.product` <-> `rule.logsource.product`
- `tenant.match.service` <-> `rule.logsource.service`

Đây là contract chính. Các fallback cũ qua `dataset.category`, `log_type`, `dataset_id`, `device_type` chỉ nên còn là backward-compatibility layer.

### Bước 5. Resolve field compatibility

Sau khi có candidate rules, kiểm tra:

- detection mapping
- tenant field binding
- ingest binding

Nếu rule không đủ field contract thì loại khỏi deployable set.

### Bước 6. Generate artifacts hoặc deployment candidates

Output:

- artifact files
- deployment manifest
- coverage summary

### Bước 7. Generate ATT&CK coverage report

Sau khi rule đã được chọn, mới tính:

- tenant cover technique nào
- dataset nào đóng góp vào ATT&CK coverage nào

## 11. Lộ trình migration đề xuất

### Giai đoạn 1. Documentation-first

- thống nhất tài liệu thiết kế
- thêm `logsource-catalog.seed.yaml` và skill support
- chưa đổi runtime contract

### Giai đoạn 2. Tenant metadata support

- cho phép `metadata.catalog_logsource`
- cho phép `match.category/product/service` hoặc `match_overrides.category/product/service`
- validator chấp nhận fields mới

### Giai đoạn 3. Rule index support

- build `rule-index`
- build `tenant-scope`
- thêm CLI inspect/debug để explain match

### Giai đoạn 4. Runtime switch

- engine ưu tiên `match.*`
- fallback cũ vẫn còn để tương thích

### Giai đoạn 5. Cleanup heuristic

- giảm dần dependence vào match mềm qua `dataset.category`, `dataset_id`, `log_type`, `device_type`
- chuyển logic match về contract rõ ràng hơn

## 12. Quyết định kiến trúc nên chốt

Các quyết định nên được chốt rõ trong hướng tương lai:

1. `rule.logsource.category/product/service` tiếp tục là rule-side semantic contract.
2. `Detection-Catalog.csv` là reference dictionary, không phải primary taxonomy của repo.
3. ATT&CK là metadata và coverage layer, không phải folder taxonomy chính của `rules/`.
4. Tenant dataset cần có normalized match scope riêng với tenant reality fields.
5. `dataset_id` vẫn là stable tenant-local key, không bị ép bằng catalog naming.
6. `match.*` là contract chính để khớp rule; `metadata.*` chỉ giữ auxiliary fields.
7. `gen-rule` tương lai nên dùng `tenant-scope + rule-index` thay vì scan và match mềm hoàn toàn ở runtime.

## 13. Tóm tắt ngắn

Hướng thiết kế khả thi và phù hợp nhất là:

- giữ `rules/` theo semantic taxonomy hiện tại
- thêm normalized match contract cho tenant dataset
- dùng Detection Catalog để hỗ trợ normalize source family
- dùng ATT&CK để reporting và coverage
- materialize `rule-index` và `tenant-scope` để tối ưu hóa `gen-rule`

Nói ngắn gọn:

`catalog_logsource` trả lời "đây là họ nguồn log nào"`

`dataset_id/category/log_type` trả lời "tenant đang có data gì"`

`match.category/product/service` trả lời "data này phục vụ rule nào"`

`attack tags` trả lời "rule này cover kỹ thuật ATT&CK nào"`
