# Kiến trúc thành phần Mapping

> English mirror: [mappings-relationship.md](../en/architecture/mappings-relationship.md)

## 1. Mục đích và phạm vi

Tài liệu này xác định vai trò, phạm vi trách nhiệm, và nguyên tắc tổ chức của thư mục `mappings/` trong repository `SIEM-Detection-as-Code`.

Tài liệu tập trung vào lớp mapping phục vụ detection content và tenant-specific rendering. Tài liệu không mô tả toàn bộ bài toán từ raw log đến parser implementation của từng SIEM.

## 2. Vai trò của mapping layer

Trong kiến trúc hiện tại, `mappings/` là lớp contract phục vụ chuẩn hóa field và ngữ nghĩa detection content.

Lớp này có các mục tiêu chính sau:

- cung cấp vocabulary field chung để viết và duy trì detection rule
- giảm phụ thuộc của rule vào naming riêng của từng nguồn content
- nối source rule field với canonical field của project
- tạo nền cho việc nối canonical field với field thực tế của tenant trên SIEM
- hỗ trợ render rule theo tenant trong khi converter tổng quát chưa hoàn thiện đầy đủ

Theo mô hình này:

- `rules/` định nghĩa hành vi cần phát hiện
- `mappings/` định nghĩa field được hiểu như thế nào trong ngữ cảnh chuẩn
- `tenants/` định nghĩa tenant đang có field nào và deploy vào đâu

## 3. Mô hình folder chuẩn

Trong giai đoạn hiện tại, lớp mapping được tổ chức theo 2 nhánh chính:

```text
mappings/
  detections/
    <domain>/
      <product>/
        *.fields.yml
tenants/
  <tenant>/
    bindings/
      ingest/
        *.yaml
      fields/
        *.fields.yml
```

Nguyên tắc tổ chức:

- `mappings/detections/` lưu mapping chuẩn từ `source rule field` sang `canonical field`
- `tenants/.../bindings/fields/` lưu mapping từ `canonical field` sang `tenant SIEM field`
- taxonomy của `mappings/detections/` phải bám sát taxonomy của `rules/`
- tránh nhân bản file mapping theo từng rule nếu nhiều rule cùng dùng một field vocabulary

## 4. `mappings/detections/`

`mappings/detections/` là lớp mapping chuẩn ở phía detection content.

Vai trò:

- chuẩn hóa field của rule nguồn về canonical field
- hỗ trợ ingest rule từ nhiều nguồn field vocabulary khác nhau
- tạo shared field dictionary theo domain hoặc product

Ví dụ:

```text
rules/
  detections/
    network/
      firewall/
        base/
          net_fw_rpc-to-the-internet.yml

mappings/
  detections/
    network/
      firewall/
        firewall.fields.yml
```

Trong mô hình này, `firewall.fields.yml` là shared field dictionary cho nhóm rule firewall; file này không phải là mapping riêng cho một rule đơn lẻ.

## 5. Shared field dictionary theo domain

Một file như `firewall.fields.yml` phải được hiểu như một dictionary chuẩn theo domain.

Vai trò của file dạng này:

- gom nhiều source field alias về cùng một canonical field
- chuẩn hóa vocabulary chung cho một nhóm rule
- giảm duplication trong quá trình maintain mapping

Ví dụ:

- `src_ip`
- `src`
- `source.ip`

có thể cùng ánh xạ về:

- `canonical.source.ip`

File dictionary này chỉ mô tả quan hệ ánh xạ field; file này không thay thế cho field requirement riêng của từng rule.

## 6. Metadata dùng để resolve mapping

Metadata trong file mapping phải dùng cùng ngôn ngữ với metadata của rule, thay vì tạo một vocabulary riêng cho mapping.

Các field được sử dụng để resolve mapping bao gồm:

- `category`
- `product`
- `service`

Ví dụ:

```yaml
logsource:
  category: firewall
  product: any
  service: traffic
```

Nguyên tắc áp dụng:

- metadata dùng để match phải bám theo `rule.logsource.*`
- taxonomy thư mục vẫn có giá trị tổ chức file, nhưng không thay thế metadata dùng để resolve
- trong giai đoạn hiện tại, không sử dụng `domain` như key chính để resolve mapping

## 7. Mô hình canonical field

Trong ngữ cảnh của project này, `canonical field` là bộ field chuẩn nội bộ của repository.

Đặc tính mong muốn của canonical field:

- ổn định hơn field đang tồn tại trên từng tenant
- không phụ thuộc trực tiếp vào raw log của vendor
- không phụ thuộc trực tiếp vào parser implementation hiện tại của từng SIEM
- đủ nhỏ để có thể duy trì trong thực tế, nhưng đủ rõ để giữ semantic contract chung

`canonical field` có thể tham chiếu semantic từ OCSF, nhưng không bắt buộc phải là bản triển khai đầy đủ của OCSF trong giai đoạn hiện tại.

## 8. Phạm vi canonical hóa dữ liệu

Không phải mọi field của logsource đều cần được canonical hóa ngay từ đầu.

Trong giai đoạn hiện tại, canonical field được tạo theo nguyên tắc `detection-driven`, tức là ưu tiên theo nhu cầu thực tế của rule. Các nhóm field nên được ưu tiên gồm:

- field bắt buộc để rule hoạt động
- field dùng cho correlation
- field dùng cho output, notable, hoặc review vận hành

Mô hình xử lý tương ứng là:

```text
source rule field
  -> canonical field
  -> tenant SIEM field
```

Cách tiếp cận này giúp:

- giảm effort ban đầu
- giảm chi phí canonical hóa toàn bộ logsource upfront
- ưu tiên giá trị detection trước khi mở rộng data model

Trong luồng hardcoded query hiện tại, mapping vẫn giữ vai trò bắt buộc để resolve field logic theo tenant, kiểm tra field coverage, và bổ sung ingest target như `index`, `sourcetype`. Chi tiết luồng này được mô tả riêng tại [rule-rendering-flows.md](./rule-rendering-flows.md).

## 9. Quy tắc vận hành canonical field

Để tránh phát sinh canonical field trùng nghĩa hoặc thiếu kiểm soát, quy trình vận hành tối thiểu nên gồm:

1. Liệt kê các `source rule field` mà rule thực sự sử dụng.
2. Kiểm tra xem các field đó đã có canonical tương ứng hay chưa.
3. Nếu đã có, sử dụng lại canonical field hiện hữu.
4. Nếu chưa có, bổ sung canonical field mới vào dictionary hoặc registry phù hợp.
5. Chỉ sau đó mới ánh xạ canonical field sang `tenant SIEM field`.

## 10. `tenants/.../bindings/fields/`

`tenants/.../bindings/fields/` là lớp triển khai mapping theo tenant.

Vai trò:

- là nguồn chuẩn cho field thực tế trên SIEM của tenant
- phản ánh khác biệt theo `tenant_id`, `siem_id`, `device_id`, và khi cần là `dataset_id`
- cung cấp lớp nối cuối cùng giữa canonical field và field thực thi thực tế

Ví dụ:

```text
tenants/
  lab/
    bindings/
      fields/
        checkpoint-fw.fields.yml
```

Trong file này có thể mô tả:

- canonical field nào map sang field nào trên SIEM của tenant
- mapping đó áp dụng cho device hoặc dataset nào

## 11. Quan hệ giữa source rule field, canonical field, OCSF, và tenant field

Các lớp field trong kiến trúc hiện tại được phân tách như sau:

- `source rule field`: field xuất hiện trong rule nguồn hoặc content legacy
- `canonical field`: field chuẩn nội bộ của project
- `OCSF`: semantic reference để thiết kế canonical field
- `tenant SIEM field`: field vật lý thực tế đang tồn tại trên SIEM của tenant

Pipeline mục tiêu ở giai đoạn hiện tại là:

```text
source rule field <=> canonical field <=> tenant SIEM field
```

Mô hình này phù hợp hơn với hiện trạng của project so với việc giả định một pipeline đầy đủ từ raw log đến parser, OCSF, rồi render end-to-end.

## 12. Vai trò của hardcoded SPL

Trong hiện trạng của project, hardcoded SPL hoặc query đặc thù theo SIEM vẫn là execution artifact hợp lệ.

Việc này phản ánh một quyết định kiến trúc có kiểm soát, dựa trên các lý do sau:

- converter tổng quát từ detection rule chuẩn sang SIEM rule chưa ổn định
- pipeline vẫn cần output có thể review, export, hoặc deploy
- detection intent và field contract vẫn cần được giữ ở lớp chuẩn

Vì vậy:

- detection rule chuẩn giữ semantic intent và field requirement
- hardcoded SPL giữ vai trò execution artifact tạm thời
- canonical field tiếp tục giữ vai trò contract lâu dài của detection content

Chi tiết vai trò của hardcoded query và quan hệ với execution layer được mô tả thêm trong [execution-relationship.md](./execution-relationship.md) và [rule-rendering-flows.md](./rule-rendering-flows.md).

## 13. Phạm vi hỗ trợ thực tế trong v1.0

Trong giai đoạn `0.x` hoặc `1.0`, lớp `mappings/` nên hỗ trợ các khả năng sau:

- ánh xạ `source rule field` sang `canonical field`
- rename field và xử lý alias field
- ánh xạ ingest target như `index`, `sourcetype`
- validate tenant có đủ field cần thiết để render hoặc sử dụng rule hay không

Các khả năng sau chưa được xem là mục tiêu bắt buộc trong cùng giai đoạn:

- enum normalization ở mức sâu
- type casting tự động
- combine hoặc split field phức tạp
- derived field nhiều bước
- transform logic tổng quát cho mọi loại field

## 14. Giới hạn hiện tại

Tại thời điểm hiện tại, các giới hạn sau phải được ghi nhận rõ:

- mapping end-to-end từ raw log đến field cuối cùng trên SIEM không nằm hoàn toàn trong phạm vi của lớp `mappings/`
- hardcoded SPL vẫn là thành phần quan trọng của pipeline
- converter tổng quát vẫn chưa đạt độ ổn định cần thiết
- một số tri thức legacy về vendor hoặc raw log không còn nằm trong lớp folder chuẩn chính của pipeline

Việc ghi nhận rõ các giới hạn này là cần thiết để tài liệu phản ánh đúng hiện trạng vận hành.

## 15. Hướng phát triển tiếp theo

Sau khi canonical field và tenant bindings đạt mức ổn định cao hơn, lớp `mappings/` có thể được mở rộng theo các hướng sau:

- mở rộng field dictionary theo từng domain
- bổ sung field coverage report cho từng rule và tenant
- hỗ trợ transform đơn giản như enum alias hoặc type cast
- chuẩn hóa dần naming của field trên tenant SIEM
- đánh giá lại khả năng sử dụng hoặc xây dựng converter tổng quát

## 16. Kết luận

Trong kiến trúc hiện tại của `SIEM-Detection-as-Code`:

- `mappings/` là lớp contract field ở phía detection content
- `mappings/detections/` là lớp mapping chuẩn từ `source rule field` sang `canonical field`
- `tenants/.../bindings/fields/` là lớp mapping từ `canonical field` sang `tenant SIEM field`
- `canonical field` là lớp chuẩn nội bộ để detection content dựa vào
- hardcoded SPL là execution artifact hợp lệ trong giai đoạn chuyển tiếp

Tài liệu này là chuẩn tham chiếu cho mọi thay đổi liên quan đến vocabulary field, canonical model, cơ chế resolve mapping, và tenant field binding trong repository.
