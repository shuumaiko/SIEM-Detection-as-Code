SIEM-DaC (Detection as Code)

Kho lưu trữ triển khai Detection as Code (DaC) cho SOC, chuẩn hóa detection rule, log schema và quy trình triển khai đa SIEM.

📌 Giới thiệu

SIEM-DaC là một dự án áp dụng mô hình Detection as Code nhằm quản lý toàn bộ vòng đời detection theo tư duy code-first, giúp SOC xây dựng, vận hành và mở rộng hệ thống phát hiện một cách bền vững.

Dự án tập trung vào việc tách bạch rõ ràng giữa:

Logic phát hiện (Detection Logic)

Chuẩn dữ liệu & schema (OCSF / OCFS)

Triển khai kỹ thuật theo từng SIEM

Qua đó giảm phụ thuộc vào vendor, tăng khả năng tái sử dụng và chuẩn hóa detection trong môi trường đa nền tảng.

🎯 Mục tiêu

Xây dựng detection độc lập SIEM

Chuẩn hóa log và field mapping

Áp dụng version control, review, test cho detection

Hỗ trợ SOC từ Detection Engineering → Threat Hunting → Incident Response

👥 Đối tượng sử dụng

SOC Analyst

Detection Engineer

Threat Hunter

SIEM Engineer

DFIR / Purple Team

🧠 Kiến trúc Detection as Code

Luồng tổng quát của dự án:

Log source (vendor-specific)
        ↓
Logsource Mapping (OCSF / OCFS)
        ↓
Rule View (rule field ↔ log field)
        ↓
Detection Rule (SIEM-agnostic)
        ↓
SIEM-specific Implementation

Triết lý thiết kế

Detection rule không phụ thuộc log vendor

Mapping xử lý khác biệt dữ liệu

SIEM chỉ là lớp triển khai cuối

Detection được quản lý như code (Git, PR, CI/CD)

📁 Cấu trúc thư mục
Thư mục	Mô tả
.github/	GitHub Actions & workflow tự động hóa
docs/	Tài liệu kiến trúc, chuẩn schema, hướng dẫn
logsource-mapping-registry/	Mapping log source theo chuẩn OCSF / OCFS
rule-view/	Lớp trung gian ánh xạ field giữa rule và log
rules/	Detection rules độc lập SIEM (base rules)
rules-tenants/	Rule triển khai thực tế theo từng tenant
tests/	Test case, validation, simulation
tools/	Tool & script hỗ trợ build, validate, deploy

Các domain như compliance, DFIR, threat hunting sẽ được mở rộng khi cần.

📐 Chuẩn & nguyên tắc thiết kế
1️⃣ Detection Rule

Phát hiện theo hành vi (behavior-based)

Ánh xạ MITRE ATT&CK

Không hard-code field SIEM

Có metadata đầy đủ: severity, confidence, coverage

2️⃣ Log & Schema

Ưu tiên chuẩn OCSF / OCFS

Log vendor không chuẩn → xử lý bằng mapping

Field chưa có trong chuẩn → mở rộng có kiểm soát

3️⃣ Vòng đời Detection
Design → Write → Review → Test → Deploy → Monitor → Tune


Detection được quản lý như code:

Git versioning

Pull Request

CI/CD

Test & validation

⚙️ Nền tảng SIEM hỗ trợ

Splunk

Elastic Security

IBM QRadar

Graylog

Có thể mở rộng sang XDR / SOAR / Data Lake

🧪 Testing & Validation

Test logic detection bằng dữ liệu giả lập

Validate logsource mapping

Đánh giá false positive / false negative

Đảm bảo rule hoạt động nhất quán giữa các SIEM

📚 Tham khảo & cảm hứng

MITRE ATT&CK

Splunk Security Content

Sigma Project

OCSF Schema

Detection Engineering Handbook

🤝 Đóng góp

Vui lòng đọc CONTRIBUTING.md
 trước khi gửi PR

Hoan nghênh đóng góp rule, mapping, tài liệu

PR nên có mô tả mục tiêu detection và test đi kèm

🧭 Ghi chú

Dự án này không nhằm thay thế SIEM, mà nhằm:

Chuẩn hóa và nâng cấp cách SOC xây dựng, quản lý và mở rộng detection theo hướng bền vững và chuyên nghiệp.