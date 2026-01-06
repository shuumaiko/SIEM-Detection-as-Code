SIEM-DaC

Kho lưu trữ triển khai Detection as Code (DaC), chuẩn hóa detection rule và log schema phục vụ vận hành SOC đa SIEM.

📌 Giới thiệu

SIEM-DaC là kho lưu trữ các detection rule và thành phần liên quan, được xây dựng theo mô hình Detection as Code (DaC) nhằm hỗ trợ các đội SOC xây dựng, quản lý và triển khai detection một cách có hệ thống.

Dự án tập trung vào việc chuẩn hóa và tách bạch:

Logic phát hiện (detection logic)

Chuẩn dữ liệu và schema log (OCSF / OCFS)

Triển khai kỹ thuật theo từng nền tảng SIEM

Qua đó giúp giảm phụ thuộc vào vendor, tăng khả năng tái sử dụng, kiểm soát chất lượng và mở rộng detection trong môi trường thực tế.

Dự án phù hợp cho:

SOC Analyst

Detection Engineer

Threat Hunter

SIEM Engineer

DFIR / Purple Team

🎯 Mục tiêu

Xây dựng detection rule độc lập SIEM

Chuẩn hóa log source và field mapping

Quản lý detection theo tư duy code (Git, review, test)

Hỗ trợ toàn bộ vòng đời detection trong SOC

📁 Cấu trúc thư mục
Thư mục	Mô tả
.github/	Chứa GitHub workflows phục vụ tự động hóa
docs/	Tài liệu kiến trúc, chuẩn schema, hướng dẫn sử dụng
logsource-mapping-registry/	Field mapping cho các logsource theo chuẩn OCSF / OCFS
rule-view/	Lớp trung gian ánh xạ field giữa rule và log thực tế
rules/	Các detection rules độc lập SIEM (base rules)
rules-tenants/	Rule đang triển khai thực tế theo từng tenant/khách hàng
tests/	Test case, kết quả kiểm thử và script test rule
tools/	Công cụ hỗ trợ validate, build và deploy rules
🧠 Phương pháp phát triển Detection

Các detection rule trong dự án được xây dựng theo các nguyên tắc:

Phát hiện theo hành vi (behavior-based), hạn chế IOC tĩnh

Ánh xạ theo MITRE ATT&CK

Không phụ thuộc trực tiếp vào field SIEM hoặc log vendor

Có kiểm thử và điều chỉnh dựa trên dữ liệu thực tế

Detection được quản lý theo vòng đời:

Thiết kế

Viết rule

Review

Test

Deploy

Monitor và tuning

📐 Chuẩn log & mapping

Ưu tiên sử dụng chuẩn OCSF / OCFS

Log không theo chuẩn được xử lý thông qua logsource mapping

Field chưa có trong chuẩn được mở rộng có kiểm soát

Mapping tách biệt hoàn toàn khỏi logic detection

⚙️ Các nền tảng SIEM hỗ trợ

Splunk

Elastic Security

IBM QRadar

Graylog

(Có thể mở rộng sang XDR, SOAR hoặc Data Lake)

🧪 Testing & Validation

Kiểm thử logic detection bằng dữ liệu giả lập

Validate logsource mapping

Đánh giá false positive / false negative

Đảm bảo rule hoạt động nhất quán giữa các SIEM

📚 Tài liệu tham khảo

MITRE ATT&CK

Splunk Security Content

Sigma Project

OCSF Schema

Detection Engineering Handbook

🤝 Đóng góp

Vui lòng đọc CONTRIBUTING.md
 trước khi gửi pull request

Hoan nghênh đóng góp rule, mapping và tài liệu

Ưu tiên các PR có mô tả mục tiêu detection và test kèm theo