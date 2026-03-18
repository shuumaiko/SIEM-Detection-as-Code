# Tài liệu SIEM-Detection-as-Code

Thư mục `docs/` này chứa tài liệu kiến trúc và các ghi chú hỗ trợ cho repository `SIEM-Detection-as-Code`.

Bộ tài liệu hiện tại được tổ chức theo kiến trúc mới của repository, với tài liệu kiến trúc tiếng Việt và tiếng Anh được tách riêng để đội ngũ có thể duy trì song song.

## Cấu trúc tài liệu

```text
docs/
|-- README.md
|-- README.vi.md
|-- architecture/
|   |-- project-architecture.md
|   |-- tenants-relationship.md
|   `-- mappings-relationship.md
|-- en/
|   `-- architecture/
|       |-- project-architecture.md
|       |-- tenants-relationship.md
|       `-- mappings-relationship.md
`-- note/
    |-- base-note.txt
    `-- SIEM-DaC-Idea.md
```

## Nội dung của từng khu vực

### `architecture/`

Các tài liệu kiến trúc tiếng Việt cho mô hình repository hiện tại:

- `project-architecture.md`: kiến trúc tổng quan của project
- `tenants-relationship.md`: cấu trúc và quan hệ trong tenant layer
- `mappings-relationship.md`: phạm vi, contract, và định hướng của mapping layer

### `en/architecture/`

Các bản tiếng Anh của nhóm tài liệu kiến trúc chính, được giữ theo cấu trúc mirror:

- `project-architecture.md`
- `tenants-relationship.md`
- `mappings-relationship.md`

### `note/`

Các ghi chú làm việc và ý tưởng thiết kế ban đầu, dùng để lưu bối cảnh lịch sử hoặc draft suy nghĩ:

- `base-note.txt`
- `SIEM-DaC-Idea.md`

Các note này hữu ích để tham khảo, nhưng nguồn kiến trúc chính nên là các tài liệu trong `architecture/` và `en/architecture/`.

## Thứ tự đọc khuyến nghị

### Nếu muốn hiểu kiến trúc hiện tại

1. `architecture/project-architecture.md`
2. `architecture/tenants-relationship.md`
3. `architecture/mappings-relationship.md`

### Nếu muốn đọc bản tiếng Anh

1. `en/architecture/project-architecture.md`
2. `en/architecture/tenants-relationship.md`
3. `en/architecture/mappings-relationship.md`

### Nếu muốn xem bối cảnh lịch sử

1. `note/base-note.txt`
2. `note/SIEM-DaC-Idea.md`

## Mục đích của bộ tài liệu

Bộ tài liệu trong thư mục này phản ánh định hướng hiện tại của repository:

- giữ `Detection as Code` là mô hình vận hành cốt lõi
- chuyển dần khỏi cách triển khai và quản lý rule thủ công
- chuẩn hóa quan hệ giữa rules, mappings, tenant configuration, và rendered artifacts
- cung cấp một tham chiếu kiến trúc rõ ràng hơn trong lúc implementation code vẫn đang được điều chỉnh

## Trạng thái hiện tại

Ở thời điểm hiện tại:

- tài liệu kiến trúc đáng tin cậy hơn các giả định implementation cũ
- `docs/architecture/` là nguồn tham chiếu chính bằng tiếng Việt
- `docs/en/architecture/` là nguồn tham chiếu chính bằng tiếng Anh
- một số file note cũ có thể vẫn còn dùng naming legacy như `SIEM-DaC`

## Tóm tắt

Hãy dùng thư mục này như điểm vào chính để hiểu `SIEM-Detection-as-Code` hiện đang được tổ chức như thế nào.

Nếu cần kiến trúc, hãy bắt đầu từ `architecture/` hoặc `en/architecture/`. Nếu cần bối cảnh cũ hoặc lịch sử thiết kế, hãy đọc `note/`.
