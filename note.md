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

vai trò của decoder?


Mục đích: Map artifact field vào ocsf (Liệu có thể map hết tất cả các field không? khả năng là ko => vậy thì cần map những field nào, cần làm gì với những field chưa map? Bổ sung field mới)
1. Cần map những field nào?
Rule cần những field gì để viết detection + TI cần những field gì để điều tra = field req <==(map)==> ocsf
2. Làm gì với những field chưa?
No idea

Giả sử đã define đc 1 list field dựa trên 1 bộ rule/uc
=> Liệu đã đủ "field" chưa, sau cần dùng thêm field khác thì sẽ update ra sao? quản lý về version

Luồng "mapping field module" - ocsf-mapping-worker:

Plaso output ==(đẩy vào)==> ocsf-mapping-worker (Được call bởi OpenRelic) ==> log chuẩn
Kiến trúc thì mình sẽ define dần