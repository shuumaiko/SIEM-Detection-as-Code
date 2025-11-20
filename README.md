# SIEM-Detection

> Kho lưu trữ các rules phát hiện tấn công cho hệ thống SIEM, hỗ trợ vận hành, giám sát và phản ứng sự cố hiệu quả cho SOC.

## 📌 Giới thiệu

**SIEM-Detection** là kho lưu trữ các detection rules được xây dựng và duy trì với mục tiêu hỗ trợ các nhóm vận hành an ninh (SOC). Dự án cung cấp:

- Bộ rule phát hiện theo hành vi độc hại, kỹ thuật tấn công.
- Kịch bản threat hunting dựa trên MITRE ATT&CK.
- Artifact phục vụ điều tra số (DFIR).
- Các công cụ hỗ trợ triển khai rules một cách tự động.

Dành cho SOC Analyst, Threat Hunter, Incident Responder, Detection Engineer. Đây là nền tảng để tăng cường khả năng phát hiện, phản ứng và săn tìm mối đe dọa trên nhiều lớp: endpoint, network, application, cloud,...

## 📁 Cấu trúc thư mục

| Thư mục | Mô tả |
|---|---|
|[.github](.github/)| Chứa các GitHub workflows để tự động hóa một số luồng công việc |
|[docs](docs/)| Chứa các tài liệu và hướng dẫn khác của dự án |
|[rules](rules/)| Chứa tất cả các rules cho các giải pháp SIEM |
|[rules-compliance](rules-compliance/)| Chứa các rules phục vụ kiểm tra tuân thủ |
|[rules-dfir](rules-dfir/)| Chứa các rules cho Forensics & Response |
|[rules-emerging-threats](rules-emerging-threats/)| Chứa các rules như CVE, Malware, Exploit |
|[rules-tenants](rules-tenants/)| Chứa các rule đang triển khai thực tế cho các khách hàng |
|[rules-threat-hunting](rules-threat-hunting/)| Chứa các rules phục vụ Hunting |
|[tests](tests/)| Chứa các kết quả testing rules, script test rules |
|[tools](tools/)| Chứa các công cụ tự động hóa: triên khai rules, quản lý rules cơ bản |

## 🧠 Phương pháp phát triển rule

Các detection rule được xây dựng theo các nguyên tắc:

- **Theo framework:** Ánh xạ MITRE ATT&CK.
- **Ít false positive:** Phát hiện theo hành vi có ngữ cảnh.
- **Đã kiểm nghiệm:** Kiểm thử qua hệ thống Lab, dùng các công cụ giả lập tấn công.

## ⚙️ Các hệ thống hỗ trợ

- Splunk
- IBM QRadar SIEM
- Graylog
- Elastic Security

## 📚 Tài liệu tham khảo

- [Splunk Security Content](https://github.com/splunk/security_content)
- [ATT&CK Matrix for Enterprise](https://attack.mitre.org/)

## 🤝 Đóng góp

- Xem thêm ở [CONTRIBUTING.md](CONTRIBUTING.md) trước khi gửi pull request.
