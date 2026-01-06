# SIEM-DaC

Kho lưu trữ triển khai **Detection as Code (DaC)** phục vụ xây dựng, quản lý và triển khai detection cho SOC đa SIEM.

## 📌 Giới thiệu

SIEM-DaC là dự án áp dụng mô hình **Detection as Code** nhằm chuẩn hóa detection rule, log schema và quy trình triển khai detection trong SOC.

Dự án tập trung vào việc tách bạch rõ ràng giữa:
- 🧠 Logic phát hiện
- 📐 Chuẩn dữ liệu và schema log
- ⚙️ Triển khai kỹ thuật theo từng nền tảng SIEM

Mục tiêu là giảm phụ thuộc vendor, tăng khả năng tái sử dụng và kiểm soát chất lượng detection.

Đối tượng sử dụng:
- SOC Analyst
- Detection Engineer
- Threat Hunter
- SIEM Engineer
- DFIR / Purple Team

## 🧩 Kiến trúc Detection as Code (DaC)

Dự án áp dụng mô hình Detection as Code nhằm tách biệt rõ ràng giữa logic phát hiện, chuẩn dữ liệu và triển khai kỹ thuật.

Kiến trúc tổng thể được chia thành các lớp sau:

**Log source**  
Dữ liệu log gốc từ các hệ thống như endpoint, network, application, cloud, security device.  
Mỗi log source có format và field khác nhau tùy vendor.

**Logsource mapping**  
Chuẩn hóa log source về schema chung (OCSF / OCFS).  
Lớp này xử lý sự khác biệt về tên field, kiểu dữ liệu và cấu trúc log giữa các vendor.

**Rule view**  
Lớp trung gian ánh xạ giữa field logic trong detection rule và field đã được chuẩn hóa.  
Giúp detection rule không phụ thuộc trực tiếp vào log vendor hoặc SIEM.

**Detection rule (SIEM-agnostic)**  
Logic phát hiện được định nghĩa độc lập với nền tảng SIEM.  
Rule tập trung vào hành vi, ngữ cảnh và kỹ thuật tấn công.

**SIEM-specific implementation**  
Triển khai detection rule sang ngôn ngữ và cơ chế của từng SIEM (Splunk, Elastic, QRadar, ...).  
Đây là lớp cuối, chỉ chịu trách nhiệm thực thi.

Nguyên tắc thiết kế chính:
- Detection rule không phụ thuộc vendor
- Mapping và triển khai được tách rời
- Thay đổi log source không làm thay đổi logic detection
- Detection được quản lý và kiểm soát như code

## 🎯 Mục tiêu

- Xây dựng detection rule độc lập SIEM
- Chuẩn hóa log source và field mapping
- Quản lý detection theo tư duy code (Git, review, test)
- Hỗ trợ toàn bộ vòng đời detection trong SOC

## 📁 Cấu trúc thư mục

**.github/**  
Workflow và automation cho GitHub

**docs/**  
Tài liệu kiến trúc, chuẩn schema, hướng dẫn sử dụng

**logsource-mapping-registry/**  
Field mapping cho các logsource theo chuẩn OCSF / OCFS

**rule-view/**  
Lớp trung gian ánh xạ field giữa rule logic và log thực tế

**rules/**  
Detection rules độc lập SIEM (base rules)

**rules-tenants/**  
Rule triển khai thực tế theo từng tenant hoặc khách hàng

**tests/**  
Test case, kết quả kiểm thử và script test rule

**tools/**  
Công cụ hỗ trợ validate, build và deploy rules

## 🧠 Phương pháp phát triển Detection

Các detection rule được xây dựng theo các nguyên tắc:
- Phát hiện theo hành vi, hạn chế IOC tĩnh
- Ánh xạ theo MITRE ATT&CK
- Không phụ thuộc trực tiếp vào field của SIEM
- Có kiểm thử và điều chỉnh dựa trên dữ liệu thực tế

Vòng đời detection:
- Thiết kế
- Viết rule
- Review
- Test
- Deploy
- Monitor và tuning

## 📐 Chuẩn log và mapping

- Ưu tiên sử dụng chuẩn OCSF / OCFS
- Log không theo chuẩn được xử lý bằng logsource mapping
- Field chưa có trong chuẩn được mở rộng có kiểm soát
- Mapping tách biệt khỏi logic detection

## ⚙️ Nền tảng SIEM hỗ trợ

- Splunk
- Elastic Security
- IBM QRadar
- Graylog

## 🧪 Testing và Validation

- Kiểm thử logic detection bằng dữ liệu giả lập
- Validate logsource mapping
- Đánh giá false positive và false negative
- Đảm bảo rule hoạt động nhất quán giữa các SIEM

## 📚 Tài liệu tham khảo

- MITRE ATT&CK
- Splunk Security Content
- Sigma Project
- OCSF Schema
- Detection Engineering Handbook

## 🤝 Đóng góp

Vui lòng đọc **CONTRIBUTING.md** trước khi gửi pull request.

Hoan nghênh đóng góp rule, mapping và tài liệu cho dự án.
