## Hướng dẫn contribute cho dự án

- Bước 1: Fork repo của dự án về Github cá nhân.
- Bước 2: Thực hiện các thay đổi trên dự án đã fork của GitHub cá nhân.
- Bước 3: Commit và push code lên dự án đã fork của GitHub cá nhân.
- Bước 4: Tạo Pull Request tới repo gốc của dự án, sau đó chờ được merge.

## Rule template

- Sử dụng template sau cho việc phát triển các detection rules. Cấu trúc này dựa trên sigma rules và có tùy biến lại để phù hợp với nhu cầu sử dụng.

```yaml
id: <UUID v4 sinh ngẫu nhiên, ví dụ: 722d5f75-2b02-426a-8f24-e2a6fe47388b>
title: <Tên Rule, ví dụ: 7Zip Compressing Dump File>
status: <enable|disable>
# Đối với các rule nằm trong trong thư mục 'converted-rules' cần phải bổ sung thêm field 'tenant' để biết đã triển khai cho khách hàng nào
# Các rule nằm trong thư mục riêng của mỗi tenant thì không cần field này
tenant:
  - tenant_a
  - tenant_b
  - tenant_c
description: <Mô tả về rules, ví dụ: Detects execution of 7z in order to compress a file with a ".dmp"/".dump" extension.>
references:
  - <Link tham chiếu 1, ví dụ: https://example1.com/post1>
  - <Link tham chiếu 2, ví dụ: https://example2.com/post2>
author: <Tác giả 1, ví dụ: Nasreddine Bencherchali (Nextron Systems)>, <Tác giả 2, ví dụ: FIS Purple Team>
date: <Thời gian tạo rule lần đầu, ví dụ: 2022-09-27>
modified: <Thời gian cập nhật rule, ví dụ: 2023-09-27>
tags:
  - <mitre tactic 1, ví dụ: attack.collection>
  - <mitre technique 1, ví dụ: attack.t1560.001>
  - <mitre tactic 2, ví dụ: attack.execution>
  - <mitre technique 2, ví dụ: attack.t1106>
logsource:
    # Tham khảo: https://sigmahq.io/docs/basics/log-sources.html
    product: <ví dụ: windows>
    service: <ví dụ: powershell>
    category: <ví dụ: process_creation>
detection:
  # Logic phát hiện của sigma -> Giữ nguyên để sau còn đối chiếu
  # Khi phát triển rules EDR/SIEM mới mà sigma chưa có thì có thể bỏ qua phần này
  selection_img:
    - Description|contains: '7-Zip'
    - Image|endswith:
        - '\7z.exe'
        - '\7zr.exe'
        - '\7za.exe'
    - OriginalFileName:
        - '7z.exe'
        - '7za.exe'
  selection_extension:
    CommandLine|contains:
      - '.dmp'
      - '.dump'
      - '.hdmp'
  condition: all of selection_*

# Logic phát hiện của một giải pháp EDR hoặc SIEM cụ thể
logic: <ví dụ: (cmdline:Compress-Archive AND cmdline:-Path AND cmdline:-DestinationPath AND cmdline:$env AND cmdline:TEMP)>
falsepositives:
  - Legitimate use of 7z with a command line in which ".dmp" or ".dump" appears accidentally
  - Legitimate use of 7z to compress WER ".dmp" files for troubleshooting
level: medium
version: <phiên bản rules, bắt đầu từ 1.0, ví dụ: 1.1>

```

## Tham khảo

- Sigma docs: <https://sigmahq.io/docs/guide/getting-started.html>
